import logging
from app.api.ingestion.client import PokeApiClient
from app.models.enums.pokeapi import EndPoint
from app.models.tables.game import Game
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from functools import partial
import time
import roman
from sqlmodel import Session, SQLModel, create_engine

# Configuration variables
LIMIT_IMPORT = True
IMPORT_LIMIT = 10

logger = logging.getLogger(__name__)

# Default path for test database
TEST_DB_PATH = Path('app/db/test.db')
# Create SQLAlchemy engine directly
SQLITE_URL = f"sqlite:///{TEST_DB_PATH}"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
# use standard SQLAlchemy engine

class GameImporter:
    """ Importer for Pokemon game data. """
    
    def __init__(self, client: Optional[PokeApiClient] = None):
        """ Initialize the game importer.
        Args:
            client: Optional API client, creates a new client by default """
        self.client = client or PokeApiClient()
        self.get_versions = partial(self.client.call, EndPoint.GAME)
        self.get_version_groups = partial(self.client.call, EndPoint.VERSION_GROUP)
        self.get_generations = partial(self.client.call, EndPoint.GENERATION)
        self.get_regions = partial(self.client.call, EndPoint.REGION)
        
        # Cache to avoid repeated API calls
        self.version_group_cache = {}
        self.generation_cache = {}
        self.region_cache = {}
        
    def import_all(self, limit: Optional[int] = None) -> List[Game]:
        """ Import all game versions from the API and store them in the database.
        Args:
            limit: Optional maximum number of game versions to import
        Returns:
            List of imported Game objects """
        # Ensure tables exist
        SQLModel.metadata.create_all(engine)
        # create tables if they don't exist
        
        versions_list = self.get_versions(limit=1)
        total_count = versions_list.get("count", 0)
        
        if limit is not None:
            total_count = min(limit, total_count)
            logger.info(f"Limiting import to {total_count} game versions")
        
        logger.info(f"Starting import of {total_count} game versions...")
        
        all_versions = self.get_versions(limit=total_count).get("results", [])
        imported_games = []
        # get versions list
        
        with Session(engine) as session:
            for i, version_info in enumerate(all_versions, 1):
                if limit is not None and i > limit:
                    break
                    
                try:
                    # Extract URL and get resource_id from the last segment
                    url = version_info.get("url", "")
                    resource_id = url.rstrip("/").split("/")[-1]
                    
                    version_data = self.get_versions(resource_id=resource_id)
                    
                    game_obj = self._process_version_data(version_data)
                    if game_obj:
                        session.add(game_obj)
                        imported_games.append(game_obj)
                        logger.info(f"Imported game version: {game_obj.name} (Group: {game_obj.version_group})")
                    
                    # Small delay to be respectful to the API
                    time.sleep(0.5)
                except Exception as e:
                    logger.error(f"Error importing game version {i}: {e}")
                    continue  # Skip to next version on error
            
            # Commit successful imports even if some failed
            try:
                session.commit()
                logger.info(f"Committed {len(imported_games)} game versions to database")
            except Exception as e:
                logger.error(f"Failed to commit changes: {e}")
                session.rollback()
                return []
            # process and save each game version, continue on errors
        
        logger.info(f"Import completed. {len(imported_games)} game versions imported.")
        return imported_games
    
    def _process_version_data(self, version_data: Dict[str, Any]) -> Optional[Game]:
        """ Process version data and create a Game object.
        Args:
            version_data: Raw version data from the API
            
        Returns:
            The created Game object or None if processing failed
        """
        try:
            version_id = version_data.get("id")
            version_name = version_data.get("name")
            
            # Get version group data
            version_group_url = version_data.get("version_group", {}).get("url", "")
            version_group_id = version_group_url.rstrip("/").split("/")[-1]
            
            # Get version group info from cache or API
            if version_group_id in self.version_group_cache:
                version_group_data = self.version_group_cache[version_group_id]
            else:
                version_group_data = self.get_version_groups(resource_id=version_group_id)
                self.version_group_cache[version_group_id] = version_group_data
                time.sleep(0.5)  # Small delay to be respectful to the API
            
            version_group_name = version_group_data.get("name")
            
            # Get generation data
            generation_url = version_group_data.get("generation", {}).get("url", "")
            generation_id = generation_url.rstrip("/").split("/")[-1]
            
            # Get generation info from cache or API
            if generation_id in self.generation_cache:
                generation_data = self.generation_cache[generation_id]
            else:
                generation_data = self.get_generations(resource_id=generation_id)
                self.generation_cache[generation_id] = generation_data
                time.sleep(0.5)  # Small delay to be respectful to the API
            
            # Convert generation name (e.g., "generation-i") to number
            generation_name = generation_data.get("name", "")
            
            generation_number = int(generation_id)  # Default to ID
            
            # Get localized generation name (English or French)
            formatted_generation_name = None
            for name_entry in generation_data.get("names", []):
                language = name_entry.get("language", {}).get("name", "")
                if language == "fr":  # Prioritize French
                    formatted_generation_name = name_entry.get("name")
                    break
                elif language == "en":
                    formatted_generation_name = name_entry.get("name")
            
            # Try to extract roman numeral from name if no localized name found
            if not formatted_generation_name and generation_name.startswith("generation-"):
                try:
                    roman_numeral = generation_name.split("-")[1].upper()
                    generation_number = roman.fromRoman(roman_numeral)
                except (IndexError, ValueError, roman.InvalidRomanNumeralError):
                    logger.warning(f"Could not parse generation number from {generation_name}, using ID {generation_id} instead")
            
            # Get region data
            region_url = generation_data.get("main_region", {}).get("url", "")
            region_id = region_url.rstrip("/").split("/")[-1]
            
            # Get region info from cache or API
            if region_id in self.region_cache:
                region_data = self.region_cache[region_id]
            else:
                region_data = self.get_regions(resource_id=region_id)
                self.region_cache[region_id] = region_data
                time.sleep(0.5)  # Small delay to be respectful to the API
            
            region_name = region_data.get("name")
            
            # Format region name to capitalize first letter
            if region_name:
                region_name = region_name.capitalize()
            
            # Create Game object
            return Game(
                id=version_id,
                name=version_name,
                generation_number=generation_number,
                generation_name=formatted_generation_name,
                version_group=version_group_name,
                region_name=region_name
            )
        except Exception as e:
            logger.error(f"Error processing version data: {e}")
            return None


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run importer
    importer = GameImporter()
    # Use the configuration variables
    games = importer.import_all(limit=IMPORT_LIMIT if LIMIT_IMPORT else None)
    
    # Print summary
    print(f"Successfully imported {len(games)} game versions.")
    # allow direct execution 