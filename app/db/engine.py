# app/db/engine.py
from pathlib import Path
from sqlmodel import create_engine, Session
from contextlib import contextmanager

class Engine:
    def __init__(self):
        # Chemin absolu vers le dossier db, peu importe d'où est lancé le script
        self.default_folder = Path(__file__).resolve().parent
    
    @contextmanager
    def connect(self, db_name: str, folder: Path = None, echo: bool = False):
        """Context manager pour se connecter à la base de données locale.
        
        Args:
            db_name: Nom du fichier de base de données
            folder: Dossier contenant la base (défaut: app/db)
            echo: Afficher les logs SQL (défaut: False)
        """
        db_dir = folder or self.default_folder
        # Créer le répertoire parent si nécessaire
        db_dir.mkdir(parents=True, exist_ok=True)
        
        db_path = db_dir / db_name
        engine = create_engine(
            f"sqlite:///{db_path}", 
            echo=echo, 
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