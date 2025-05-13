import logging
from app.api.ingestion.client import PokeApiClient
from app.models.enums.pokeapi import EndPoint
from app.models.tables.evolution import Evolution
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from functools import partial
import ujson
import time
from sqlmodel import Session, SQLModel, create_engine

# Configuration variables
LIMIT_IMPORT = True
IMPORT_LIMIT = 20

logger = logging.getLogger(__name__)

# Default path for test database
TEST_DB_PATH = Path('app/db/test.db')
# Create SQLAlchemy engine directly
SQLITE_URL = f"sqlite:///{TEST_DB_PATH}"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
# use standard SQLAlchemy engine

class EvolutionImporter:
    """ Importer for Pokemon evolution data. """
    
    def __init__(self, client: Optional[PokeApiClient] = None):
        """ Initialize the evolution importer.
        Args:
            client: Optional API client, creates a new client by default """
        self.client = client or PokeApiClient()
        self.get_evolution_chains = partial(self.client.call, EndPoint.EVOLUTION_CHAIN)
        self.get_pokemon_species = partial(self.client.call, EndPoint.POKEMON_SPECIES)
        self.get_pokemon = partial(self.client.call, EndPoint.POKEMON)
        
    def import_all(self, limit: Optional[int] = None) -> List[Evolution]:
        """ Import all evolution chains from the API and store them in the database.
        Args:
            limit: Optional maximum number of evolution chains to import
        Returns:
            List of imported Evolution objects """
        # Ensure tables exist
        SQLModel.metadata.create_all(engine)
        # create tables if they don't exist
        
        chains_list = self.get_evolution_chains(limit=1)
        total_count = chains_list.get("count", 0)
        
        if limit is not None:
            total_count = min(limit, total_count)
            logger.info(f"Limiting import to {total_count} evolution chains")
        
        logger.info(f"Starting import of {total_count} evolution chains...")
        
        all_chains = self.get_evolution_chains(limit=total_count).get("results", [])
        imported_evolutions = []
        # get evolution chains list
        
        with Session(engine) as session:
            for i, chain_info in enumerate(all_chains, 1):
                if limit is not None and i > limit:
                    break
                    
                try:
                    # Extract URL and get resource_id from the last segment
                    url = chain_info.get("url", "")
                    resource_id = url.rstrip("/").split("/")[-1]
                    
                    chain_data = self.get_evolution_chains(resource_id=resource_id)
                    
                    # Process the evolution chain recursively
                    evolution_records = self._process_chain(chain_data)
                    for evolution in evolution_records:
                        session.add(evolution)
                        imported_evolutions.append(evolution)
                    
                    logger.info(f"Imported evolution chain: {resource_id} (Records: {len(evolution_records)})")
                    
                    # Small delay to be respectful to the API
                    time.sleep(1.0)
                except Exception as e:
                    logger.error(f"Error importing evolution chain {i}: {e}")
                    continue  # Skip to next chain on error
            
            # Commit successful imports even if some failed
            try:
                session.commit()
                logger.info(f"Committed {len(imported_evolutions)} evolution records to database")
            except Exception as e:
                logger.error(f"Failed to commit changes: {e}")
                session.rollback()
                return []
            # process and save each evolution chain, continue on errors
        
        logger.info(f"Import completed. {len(imported_evolutions)} evolution records imported.")
        return imported_evolutions
    
    def _process_chain(self, chain_data: Dict[str, Any]) -> List[Evolution]:
        """ Process evolution chain data and create Evolution objects.
        Args:
            chain_data: Raw evolution chain data from the API
            
        Returns:
            List of Evolution objects for this chain """
        chain_id = chain_data.get("id")
        evolutions = []
        
        # Get the base chain link
        base_link = chain_data.get("chain", {})
        self._process_chain_link(base_link, None, chain_id, evolutions)
        
        return evolutions
    
    def _process_chain_link(self, link: Dict[str, Any], parent_species_id: Optional[int], 
                            chain_id: int, evolutions: List[Evolution]) -> None:
        """ Recursively process chain links to extract evolution data.
        Args:
            link: Chain link data 
            parent_species_id: ID of the parent species (None for base)
            chain_id: Evolution chain ID
            evolutions: List to append created Evolution objects to
        """
        species_data = link.get("species", {})
        species_id = self._get_species_id(species_data)
        
        # If there's a parent, create an evolution record
        if parent_species_id is not None:
            # Process evolution details
            for evo_detail in link.get("evolution_details", []):
                trigger_data = self._format_evolution_trigger(evo_detail)
                
                # Get Pokemon IDs from species IDs
                from_pokemon_id = self._get_pokemon_id_from_species(parent_species_id)
                to_pokemon_id = self._get_pokemon_id_from_species(species_id)
                
                if from_pokemon_id and to_pokemon_id:
                    evolution = Evolution(
                        evolution_chain_id=chain_id,
                        pokemon_from_id=from_pokemon_id,
                        pokemon_to_id=to_pokemon_id,
                        trigger=trigger_data
                    )
                    evolutions.append(evolution)
                    
        # Process all evolves_to links recursively
        for evolves_to in link.get("evolves_to", []):
            self._process_chain_link(evolves_to, species_id, chain_id, evolutions)
    
    def _get_species_id(self, species_data: Dict[str, Any]) -> Optional[int]:
        """ Extract species ID from species data.
        Args:
            species_data: Species data from API
            
        Returns:
            Species ID or None if not found
        """
        url = species_data.get("url", "")
        try:
            return int(url.rstrip("/").split("/")[-1])
        except (ValueError, IndexError):
            return None
    
    def _get_pokemon_id_from_species(self, species_id: int) -> Optional[int]:
        """ Get the Pokemon ID from a species ID by making an API call.
        Args:
            species_id: The species ID
            
        Returns:
            Pokemon ID or None if not found
        """
        try:
            species_data = self.get_pokemon_species(resource_id=str(species_id))
            default_variety = next(
                (v for v in species_data.get("varieties", []) 
                 if v.get("is_default", False)), 
                None
            )
            
            if default_variety:
                pokemon_url = default_variety.get("pokemon", {}).get("url", "")
                pokemon_id = int(pokemon_url.rstrip("/").split("/")[-1])
                return pokemon_id
            return None
        except Exception as e:
            logger.error(f"Error getting Pokemon ID for species {species_id}: {e}")
            return None
    
    def _format_evolution_trigger(self, evo_detail: Dict[str, Any]) -> str:
        """ Format evolution details into a human-readable trigger string.
        Args:
            evo_detail: Evolution details from API
            
        Returns:
            Formatted trigger string
        """
        trigger_parts = []
        
        # Extract trigger name
        trigger = evo_detail.get("trigger", {}).get("name")
        if trigger:
            trigger_parts.append(f"{trigger}")
        
        # Extract all non-null criteria
        for key, value in evo_detail.items():
            # Skip the trigger object and null values
            if key == "trigger" or value is None or value == "" or value is False:
                continue
                
            # Handle special cases
            if isinstance(value, dict) and "name" in value:
                trigger_parts.append(f"{key}: {value['name']}")
            elif isinstance(value, bool) and value is True:
                trigger_parts.append(key)
            else:
                trigger_parts.append(f"{key}: {value}")
        
        return ", ".join(trigger_parts)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run importer
    importer = EvolutionImporter()
    # Use the configuration variables
    evolutions = importer.import_all(limit=IMPORT_LIMIT if LIMIT_IMPORT else None)
    
    # Print summary
    print(f"Successfully imported {len(evolutions)} evolution records.")
    # allow direct execution 