import logging
from pathlib import Path
from sqlmodel import SQLModel
from typing import Optional
from app.db.engine import engine

logging.basicConfig(level=logging.INFO, format='%(message)s')

# Chemins de la base de données
LOCAL_DB_PATH = Path('PKMN.db')

class LocalDatabase:
    _instance: Optional['LocalDatabase'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
    
    def build(self, db_path: Path = LOCAL_DB_PATH):
        """Construit la base de données avec les tables."""
        from app.models.tables import __all_tables__
        
        logging.info(f"Construction de la base de données {db_path}...")
        with engine.connect(str(db_path)) as session:
            SQLModel.metadata.create_all(session.get_bind())
        logging.info("✅ Base de données construite")

# Instance singleton
db = LocalDatabase()

if __name__ == "__main__":
    db.build() 