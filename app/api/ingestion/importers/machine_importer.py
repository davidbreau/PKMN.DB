import logging
from app.api.ingestion.client import PokeApiClient
from app.models.enums.pokeapi import EndPoint
from app.models.tables.machine import Machine
from pathlib import Path
from typing import Dict, Any, List, Optional
from functools import partial
import time
import re
from sqlmodel import Session, SQLModel, create_engine

# Configuration variables
LIMIT_IMPORT = True
IMPORT_LIMIT = 50

logger = logging.getLogger(__name__)

# Default path for test database
TEST_DB_PATH = Path('app/db/test.db')
# Create SQLAlchemy engine directly
SQLITE_URL = f"sqlite:///{TEST_DB_PATH}"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
# use standard SQLAlchemy engine

class MachineImporter:
    """ Importer for Pokemon machines (TM/HM) data. """
    
    def __init__(self, client: Optional[PokeApiClient] = None):
        """ Initialize the machine importer.
        Args:
            client: Optional API client, creates a new client by default """
        self.client = client or PokeApiClient()
        self.get_machines = partial(self.client.call, EndPoint.MACHINE)
        self.get_moves = partial(self.client.call, EndPoint.MOVE)
        self.get_items = partial(self.client.call, EndPoint.ITEM)
        
        # Cache to avoid repeated API calls
        self.move_cache = {}
        
    def import_all(self, limit: Optional[int] = None) -> List[Machine]:
        """ Import all machines from the API and store them in the database.
        Args:
            limit: Optional maximum number of machines to import
        Returns:
            List of imported Machine objects """
        # Ensure tables exist
        SQLModel.metadata.create_all(engine)
        # create tables if they don't exist
        
        machines_list = self.get_machines(limit=1)
        total_count = machines_list.get("count", 0)
        
        if limit is not None:
            total_count = min(limit, total_count)
            logger.info(f"Limiting import to {total_count} machines")
        
        logger.info(f"Starting import of {total_count} machines...")
        
        all_machines = []
        for i in range(1, total_count + 1):
            try:
                # Machine IDs are sequential
                machine_data = self.get_machines(resource_id=str(i))
                all_machines.append(machine_data)
            except Exception as e:
                logger.error(f"Error fetching machine {i}: {e}")
                break
            # Sleep to be respectful to the API
            time.sleep(0.5)
        
        imported_machines = []
        # get machines list
        
        with Session(engine) as session:
            for i, machine_data in enumerate(all_machines, 1):
                if limit is not None and i > limit:
                    break
                    
                try:
                    machine_obj = self._process_machine_data(machine_data)
                    if machine_obj:
                        session.add(machine_obj)
                        imported_machines.append(machine_obj)
                        logger.info(f"Imported machine: {machine_obj.machine_number} - {machine_obj.move_name} (Version: {machine_obj.version_group})")
                except Exception as e:
                    logger.error(f"Error importing machine {i}: {e}")
                    continue  # Skip to next machine on error
            
            # Commit successful imports even if some failed
            try:
                session.commit()
                logger.info(f"Committed {len(imported_machines)} machines to database")
            except Exception as e:
                logger.error(f"Failed to commit changes: {e}")
                session.rollback()
                return []
            # process and save each machine, continue on errors
        
        logger.info(f"Import completed. {len(imported_machines)} machines imported.")
        return imported_machines
    
    def _process_machine_data(self, machine_data: Dict[str, Any]) -> Optional[Machine]:
        """ Process machine data and create a Machine object.
        Args:
            machine_data: Raw machine data from the API
            
        Returns:
            The created Machine object or None if processing failed
        """
        try:
            machine_id = machine_data.get("id")
            
            # Get item data (TM/HM)
            item_data = machine_data.get("item", {})
            item_name = item_data.get("name", "")
            
            # Extract machine number (TM01, HM02, etc.)
            machine_number = item_name.upper()
            
            # Get move data
            move_data = machine_data.get("move", {})
            move_url = move_data.get("url", "")
            move_id = int(move_url.rstrip("/").split("/")[-1]) if move_url else None
            move_name = move_data.get("name", "")
            
            # Get version group
            version_group_data = machine_data.get("version_group", {})
            version_group = version_group_data.get("name", "")
            
            # Create Machine object
            return Machine(
                id=machine_id,
                machine_number=machine_number,
                move_id=move_id,
                move_name=move_name,
                version_group=version_group
            )
        except Exception as e:
            logger.error(f"Error processing machine data: {e}")
            return None


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run importer
    importer = MachineImporter()
    # Use the configuration variables
    machines = importer.import_all(limit=IMPORT_LIMIT if LIMIT_IMPORT else None)
    
    # Print summary
    print(f"Successfully imported {len(machines)} machines.")
    # allow direct execution 