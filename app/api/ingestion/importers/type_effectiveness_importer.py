import logging
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sqlmodel import Session, SQLModel, select
from app.models.tables.type_effectiveness import TypeEffectiveness
from app.models.tables.type import Type
from app.db.engine import engine as db_engine

# Configuration variables
DB_PATH = Path('app/db/PKMN.db')
CSV_FILE_PATH = Path('data/typing_chart.csv')

logger = logging.getLogger(__name__)

class TypeEffectivenessImporter:
    """ Importer for Pokemon type effectiveness data from CSV file. """
    
    def __init__(self, csv_file_path: Optional[Path] = None):
        """ Initialize the type effectiveness importer.
        Args:
            csv_file_path: Optional path to the CSV file, uses CSV_FILE_PATH by default """
        self.csv_file_path = csv_file_path or CSV_FILE_PATH
        self.type_name_to_id_mapping = {}
    
    def import_all(self):
        """ Import all type effectiveness data to the database. """
        # Use the engine context manager to get a session
        with db_engine.connect('PKMN.db') as session:
            try:
                # First, build the mapping from type names to type IDs
                self._build_type_mapping(session)
                
                if not self.type_name_to_id_mapping:
                    logger.error("No types found in the database. Please import types first.")
                    return
                
                # Read the CSV file
                effectiveness_data = self._read_csv()
                
                # Process each row
                count = 0
                
                for attacking_type, defenses in effectiveness_data.items():
                    for defending_type, effectiveness in defenses.items():
                        # Skip if no effectiveness data
                        if effectiveness is None:
                            continue
                        
                        # Convert type names to IDs
                        attacking_type_id = self.type_name_to_id_mapping.get(attacking_type.lower())
                        defending_type_id = self.type_name_to_id_mapping.get(defending_type.lower())
                        
                        if not attacking_type_id or not defending_type_id:
                            logger.warning(f"Type not found in database: {attacking_type} or {defending_type}")
                            continue
                        
                        # Create and store TypeEffectiveness entry
                        try:
                            self._create_type_effectiveness(
                                session, 
                                attacking_type_id, 
                                defending_type_id, 
                                effectiveness
                            )
                            count += 1
                        except Exception as e:
                            logger.error(f"Error creating type effectiveness entry: {e}")
                
                logger.info(f"Imported {count} type effectiveness entries")
                
            except Exception as e:
                logger.error(f"Error during type effectiveness import: {e}")
                raise
    
    def _build_type_mapping(self, session: Session):
        """ Build a mapping from type names to type IDs.
        Args:
            session: Database session
        """
        types = session.exec(select(Type)).all()
        self.type_name_to_id_mapping = {t.name.lower(): t.id for t in types}
        logger.info(f"Found {len(self.type_name_to_id_mapping)} types in the database")
    
    def _read_csv(self) -> Dict[str, Dict[str, Optional[float]]]:
        """ Read the CSV file and extract type effectiveness data.
        Returns:
            Dictionary mapping attacking type to defending type to effectiveness
        """
        effectiveness_data = {}
        
        try:
            with open(self.csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                # First row contains the headers (defending types)
                headers = next(reader)
                defending_types = headers[1:]  # Skip the first column which is "Types"
                
                # Each subsequent row contains data for one attacking type
                for row in reader:
                    attacking_type = row[0]
                    type_data = {}
                    
                    for i, defending_type in enumerate(defending_types):
                        if i + 1 < len(row) and row[i + 1]:
                            try:
                                # Convert effectiveness to float (e.g., "0.5" -> 0.5)
                                value = float(row[i + 1])
                                type_data[defending_type] = value
                            except ValueError:
                                # In case of non-numeric entries
                                logger.warning(f"Invalid effectiveness value: {row[i + 1]} for {attacking_type} vs {defending_type}")
                                type_data[defending_type] = None
                        else:
                            # Empty cell means normal effectiveness (1.0)
                            type_data[defending_type] = None
                    
                    effectiveness_data[attacking_type] = type_data
            
            logger.info(f"Successfully read type effectiveness data from {self.csv_file_path}")
            return effectiveness_data
        
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
    
    def _create_type_effectiveness(self, session: Session, attacking_type_id: int, 
                                  defending_type_id: int, effectiveness: float) -> None:
        """ Create or update a TypeEffectiveness entry in the database.
        Args:
            session: Database session
            attacking_type_id: The attacking type ID
            defending_type_id: The defending type ID
            effectiveness: The effectiveness value (e.g., 0.5, 1.0, 2.0)
        """
        # If no explicit effectiveness provided, default to 1.0 (normal effectiveness)
        if effectiveness is None:
            effectiveness = 1.0
        
        # Check if entry already exists
        statement = select(TypeEffectiveness).where(
            TypeEffectiveness.attacking_type_id == attacking_type_id,
            TypeEffectiveness.defending_type_id == defending_type_id
        )
        existing = session.exec(statement).first()
        
        if existing:
            logger.info(f"Type effectiveness for {attacking_type_id} vs {defending_type_id} already exists, updating")
            existing.effectiveness = effectiveness
        else:
            # Create new entry
            entry = TypeEffectiveness(
                attacking_type_id=attacking_type_id,
                defending_type_id=defending_type_id,
                effectiveness=effectiveness
            )
            session.add(entry)
            logger.debug(f"Added type effectiveness: {attacking_type_id} vs {defending_type_id} = {effectiveness}")

# For CLI usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    importer = TypeEffectivenessImporter()
    importer.import_all() 