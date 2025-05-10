# app/db/engine.py
from pathlib import Path
from sqlmodel import create_engine, Session
from contextlib import contextmanager

class Engine:
    def __init__(self):
        self.default_folder = Path('app/db')
    
    @contextmanager
    def connect(self, db_name: str, folder: Path = None):
        """Context manager pour se connecter à la base de données locale.
        
        Args:
            db_name: Nom du fichier de base de données
            folder: Dossier contenant la base (défaut: app/db)
        """
        db_dir = folder or self.default_folder
        engine = create_engine(
            f"sqlite:///{db_dir / db_name}", 
            echo=True, 
            connect_args={"check_same_thread": False}
        )
        session = Session(engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

# Instance singleton
engine = Engine()