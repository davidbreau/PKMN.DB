import logging
from app.api.ingestion.client import PokeApiClient
from app.models.enums.pokeapi import EndPoint
from app.models.tables.type import Type
from pathlib import Path
from typing import Dict, Any, List, Optional
from functools import partial
import ujson
import roman
from sqlmodel import Session, SQLModel, create_engine

from app.db.engine import engine as engine_factory

logger = logging.getLogger(__name__)

# Default path for test database
TEST_DB_PATH = Path('app/db/test.db')
# Create SQLAlchemy engine directly
SQLITE_URL = f"sqlite:///{TEST_DB_PATH}"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
# use standard SQLAlchemy engine

class TypeImporter:
    """ Importer for Pokemon type data. """
    
    def __init__(self, client: Optional[PokeApiClient] = None):
        """ Initialize the type importer.
        Args:
            client: Optional API client, creates a new client by default """
        self.client = client or PokeApiClient()
        self.get_types = partial(self.client.call, EndPoint.TYPE)
        
    def import_all(self) -> List[Type]:
        """ Import all types from the API and store them in the database.
        Returns:
            List of imported Type objects """
        # Ensure tables exist
        SQLModel.metadata.create_all(engine)
        # create tables if they don't exist
        
        types_list = self.get_types(limit=1)
        total_count = types_list.get("count", 0)
        
        logger.info(f"Starting import of {total_count} types...")
        
        all_types = self.get_types(limit=total_count).get("results", [])
        imported_types = []
        # get types list
        
        with Session(engine) as session:
            for i, type_info in enumerate(all_types, 1):
                try:
                    # Extract URL and get resource_id from the last segment
                    url = type_info.get("url", "")
                    resource_id = url.rstrip("/").split("/")[-1]
                    
                    type_data = self.get_types(resource_id=resource_id)
                    
                    type_obj = self._process_type_data(type_data)
                    
                    session.add(type_obj)
                    imported_types.append(type_obj)
                    
                    logger.info(f"Imported type: {type_obj.name} (ID: {type_obj.id})")
                except Exception as e:
                    logger.error(f"Error importing type {i}: {e}")
                    continue  # Skip to next type on error
            
            # Commit successful imports even if some failed
            try:
                session.commit()
                logger.info(f"Committed {len(imported_types)} types to database")
            except Exception as e:
                logger.error(f"Failed to commit changes: {e}")
                session.rollback()
                return []
            # process and save each type, continue on errors
        
        logger.info(f"Import completed. {len(imported_types)} types imported.")
        return imported_types
    
    def _process_type_data(self, data: Dict[str, Any]) -> Type:
        """ Process raw type data and create a Type object.
        Args:
            data: Raw type data from the API
            
        Returns:
            The created Type object """
        type_id = data.get("id")
        name = data.get("name")
        
        name_fr = None
        for name_entry in data.get("names", []):
            if name_entry.get("language", {}).get("name") == "fr":
                name_fr = name_entry.get("name")
                break
        # extract french name
        
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
        
        return Type(
            id=type_id,
            name=name,
            name_fr=name_fr,
            generation=generation
        )


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run importer
    importer = TypeImporter()
    types = importer.import_all()
    
    # Print summary
    print(f"Successfully imported {len(types)} types.")
    # allow direct execution
