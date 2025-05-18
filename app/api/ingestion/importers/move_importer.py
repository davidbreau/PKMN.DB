import logging
from app.api.ingestion.client import PokeApiClient
from app.models.enums.pokeapi import EndPoint
from app.models.tables.move import Move
from pathlib import Path
from typing import Dict, Any, List, Optional
from functools import partial
import roman
import time
from sqlmodel import Session, SQLModel, create_engine
import ujson

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

class MoveImporter:
    """ Importer for Pokemon move data. """
    
    def __init__(self, client: Optional[PokeApiClient] = None):
        """ Initialize the move importer.
        Args:
            client: Optional API client, creates a new client by default """
        self.client = client or PokeApiClient()
        self.get_moves = partial(self.client.call, EndPoint.MOVE)
        
    def import_all(self, limit: Optional[int] = None) -> List[Move]:
        """ Import all moves from the API and store them in the database.
        Args:
            limit: Optional maximum number of moves to import
        Returns:
            List of imported Move objects """
        # Ensure tables exist
        SQLModel.metadata.create_all(engine)
        # create tables if they don't exist
        
        moves_list = self.get_moves(limit=1)
        total_count = moves_list.get("count", 0)
        
        if limit is not None:
            total_count = min(limit, total_count)
            logger.info(f"Limiting import to {total_count} moves")
        
        logger.info(f"Starting import of {total_count} moves...")
        
        all_moves = self.get_moves(limit=total_count).get("results", [])
        imported_moves = []
        # get moves list
        
        with Session(engine) as session:
            for i, move_info in enumerate(all_moves, 1):
                if limit is not None and i > limit:
                    break
                    
                try:
                    # Extract URL and get resource_id from the last segment
                    url = move_info.get("url", "")
                    resource_id = url.rstrip("/").split("/")[-1]
                    
                    move_data = self.get_moves(resource_id=resource_id)
                    
                    move_obj = self._process_move_data(move_data)
                    if move_obj:
                        session.add(move_obj)
                        imported_moves.append(move_obj)
                        logger.info(f"Imported move: {move_obj.name} (ID: {move_obj.id})")
                    
                    # Small delay to be respectful to the API
                    time.sleep(0.5)
                except Exception as e:
                    logger.error(f"Error importing move {i}: {e}")
                    continue  # Skip to next move on error
            
            # Commit successful imports even if some failed
            try:
                session.commit()
                logger.info(f"Committed {len(imported_moves)} moves to database")
            except Exception as e:
                logger.error(f"Failed to commit changes: {e}")
                session.rollback()
                return []
            # process and save each move, continue on errors
        
        logger.info(f"Import completed. {len(imported_moves)} moves imported.")
        return imported_moves
    
    def _process_move_data(self, data: Dict[str, Any]) -> Optional[Move]:
        """ Process raw move data and create a Move object.
        Args:
            data: Raw move data from the API
            
        Returns:
            The created Move object or None if processing failed
        """
        try:
            move_id = data.get("id")
            name = data.get("name")
            
            # Extract French name
            name_fr = None
            for name_entry in data.get("names", []):
                if name_entry.get("language", {}).get("name") == "fr":
                    name_fr = name_entry.get("name")
                    break
            
            # Extract damage, precision
            damage = data.get("power")
            precision = data.get("accuracy")
            
            # Extract damage class (physical, special, status)
            damage_class = None
            damage_class_data = data.get("damage_class", {})
            if damage_class_data:
                damage_class = damage_class_data.get("name")
            
            # Extract flavor text (English) - plus conviviale pour l'utilisateur
            effect = None
            flavor_entries_en = [entry for entry in data.get("flavor_text_entries", []) 
                                if entry.get("language", {}).get("name") == "en"]
            
            if flavor_entries_en:
                # Prendre le flavor text le plus récent
                effect = flavor_entries_en[0].get("flavor_text")
            
            # Si aucun flavor text anglais, essayons d'utiliser l'effect technique
            if not effect:
                for effect_entry in data.get("effect_entries", []):
                    if effect_entry.get("language", {}).get("name") == "en":
                        effect = effect_entry.get("effect")
                        if effect and "$effect_chance" in effect:
                            effect_chance = data.get("effect_chance", 0)
                            effect = effect.replace("$effect_chance", str(effect_chance))
                        break
            
            # Extract flavor text (French)
            effect_fr = None
            flavor_entries_fr = [entry for entry in data.get("flavor_text_entries", []) 
                                if entry.get("language", {}).get("name") == "fr"]
            
            if flavor_entries_fr:
                # Prendre le flavor text le plus récent
                effect_fr = flavor_entries_fr[0].get("flavor_text")
            
            # Si aucun flavor text français, essayons d'utiliser l'effect technique
            if not effect_fr:
                for effect_entry in data.get("effect_entries", []):
                    if effect_entry.get("language", {}).get("name") == "fr":
                        effect_fr = effect_entry.get("effect")
                        if effect_fr and "$effect_chance" in effect_fr:
                            effect_chance = data.get("effect_chance", 0)
                            effect_fr = effect_fr.replace("$effect_chance", str(effect_chance))
                        break
            
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
            
            return Move(
                id=move_id,
                name=name,
                name_fr=name_fr,
                damage=damage,
                precision=precision,
                damage_class=damage_class,
                effect=effect,
                effect_fr=effect_fr,
                generation=generation
            )
            
        except Exception as e:
            logger.error(f"Error processing move data: {e}")
            return None


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run importer
    importer = MoveImporter()
    # Use the configuration variables
    moves = importer.import_all()
    
    # Print summary
    print(f"Successfully imported {len(moves)} moves.")
    # allow direct execution 