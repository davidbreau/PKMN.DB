import logging
from app.api.ingestion.client import PokeApiClient
from app.models.enums.pokeapi import EndPoint
from app.models.tables.ability import Ability
from pathlib import Path
from typing import Dict, Any, List, Optional
from functools import partial
import ujson
import roman
import time
from sqlmodel import Session, SQLModel, create_engine

# Configuration variables
LIMIT_IMPORT = False
IMPORT_LIMIT = None

logger = logging.getLogger(__name__)

# Default path for PKMN.db database
DB_PATH = Path('app/db/PKMN.db')
# Create SQLAlchemy engine directly
SQLITE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
# use standard SQLAlchemy engine

class AbilityImporter:
    """ Importer for Pokemon ability data. """
    
    def __init__(self, client: Optional[PokeApiClient] = None):
        """ Initialize the ability importer.
        Args:
            client: Optional API client, creates a new client by default """
        self.client = client or PokeApiClient()
        self.get_abilities = partial(self.client.call, EndPoint.ABILITY)
        
    def import_all(self, limit: Optional[int] = None) -> List[Ability]:
        """ Import all abilities from the API and store them in the database.
        Args:
            limit: Optional maximum number of abilities to import
        Returns:
            List of imported Ability objects """
        # Ensure tables exist
        SQLModel.metadata.create_all(engine)
        # create tables if they don't exist
        
        abilities_list = self.get_abilities(limit=1)
        total_count = abilities_list.get("count", 0)
        
        if limit is not None:
            total_count = min(limit, total_count)
            logger.info(f"Limiting import to {total_count} abilities")
        
        logger.info(f"Starting import of {total_count} abilities...")
        
        all_abilities = self.get_abilities(limit=total_count).get("results", [])
        imported_abilities = []
        # get abilities list
        
        with Session(engine) as session:
            for i, ability_info in enumerate(all_abilities, 1):
                if limit is not None and i > limit:
                    break
                    
                try:
                    # Extract URL and get resource_id from the last segment
                    url = ability_info.get("url", "")
                    resource_id = url.rstrip("/").split("/")[-1]
                    
                    ability_data = self.get_abilities(resource_id=resource_id)
                    
                    # Small delay to be respectful to the API
                    time.sleep(0.5)
                    
                    ability_obj = self._process_ability_data(ability_data)
                    
                    session.add(ability_obj)
                    imported_abilities.append(ability_obj)
                    
                    logger.info(f"Imported ability: {ability_obj.name} (ID: {ability_obj.id})")
                except Exception as e:
                    logger.error(f"Error importing ability {i}: {e}")
                    continue  # Skip to next ability on error
            
            # Commit successful imports even if some failed
            try:
                session.commit()
                logger.info(f"Committed {len(imported_abilities)} abilities to database")
            except Exception as e:
                logger.error(f"Failed to commit changes: {e}")
                session.rollback()
                return []
            # process and save each ability, continue on errors
        
        logger.info(f"Import completed. {len(imported_abilities)} abilities imported.")
        return imported_abilities
    
    def _process_ability_data(self, data: Dict[str, Any]) -> Ability:
        """ Process raw ability data and create an Ability object.
        Args:
            data: Raw ability data from the API
            
        Returns:
            The created Ability object """
        ability_id = data.get("id")
        name = data.get("name")
        
        # Extract French name
        name_fr = None
        for name_entry in data.get("names", []):
            if name_entry.get("language", {}).get("name") == "fr":
                name_fr = name_entry.get("name")
                break
        # extract french name
        
        # Extract effect text (English)
        effect = None
        for effect_entry in data.get("effect_entries", []):
            if effect_entry.get("language", {}).get("name") == "en":
                effect = effect_entry.get("effect")
                break
        # extract english effect
        
        # Extract effect text (French)
        effect_fr = None
        for effect_entry in data.get("effect_entries", []):
            if effect_entry.get("language", {}).get("name") == "fr":
                effect_fr = effect_entry.get("effect")
                break
        
        # If no French effect found, try to get French flavor text as fallback
        if not effect_fr:
            # Sort by version_group ID (descending) to get the most recent entry first
            flavor_entries = sorted(
                data.get("flavor_text_entries", []),
                key=lambda x: int(x.get("version_group", {}).get("url", "0").split("/")[-2] or 0),
                reverse=True
            )
            
            for flavor_entry in flavor_entries:
                if flavor_entry.get("language", {}).get("name") == "fr":
                    effect_fr = flavor_entry.get("flavor_text")
                    logger.info(f"Using flavor text for French effect of {name}")
                    break
        # extract french effect or flavor text
        
        # Extract generation
        generation = None
        gen_data = data.get("generation", {})
        if gen_data:
            gen_name = gen_data.get("name", "")
            if gen_name.startswith("generation-"):
                try:
                    # Convert from generation-i, generation-ii, etc. to 1, 2, etc.
                    gen_roman = gen_name.split("-")[1].upper()
                    generation = roman.fromRoman(gen_roman)
                except (IndexError, ValueError, roman.InvalidRomanNumeralError):
                    logger.warning(f"Could not parse generation from {gen_name}")
        # parse generation roman numeral to integer
        
        return Ability(
            id=ability_id,
            name=name,
            name_fr=name_fr,
            effect=effect,
            effect_fr=effect_fr,
            generation=generation
        )


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run importer
    importer = AbilityImporter()
    # Use the configuration variables
    abilities = importer.import_all()
    
    # Print summary
    print(f"Successfully imported {len(abilities)} abilities.")
    # allow direct execution 