import logging
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Chemins de la base de données
LOCAL_GO_DB_PATH = (Path(__file__).resolve().parents[2] / 'app' / 'db' / 'PKMNGO.db')

class PokemonGODatabase:
    _instance: Optional['PokemonGODatabase'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
    
    def build(self, db_path: Path = LOCAL_GO_DB_PATH):
        """Construit la base de données Pokémon GO avec les tables."""
        # Importer les modèles GO depuis le dossier GO_tables
        from app.models.GO_tables.GO_pokemon import GO_Pokemon
        from app.models.GO_tables.GO_pokemon_stats import GO_PokemonStats
        from app.models.GO_tables.GO_move import GO_Move
        from app.models.GO_tables.GO_pokemon_learnset import GO_PokemonLearnset
        from app.models.GO_tables.GO_type import GO_Type
        from app.models.GO_tables.GO_type_effectiveness import GO_TypeEffectiveness
        
        logger.info(f"Construction de la base de données Pokémon GO {db_path}...")
        
        # Créer le répertoire parent si nécessaire
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Créer le moteur SQLite
        engine = create_engine(
            f"sqlite:///{db_path}",
            echo=True,
            connect_args={"check_same_thread": False}
        )
        
        # Créer toutes les tables
        SQLModel.metadata.create_all(engine)
        
        logger.info("✅ Base de données Pokémon GO construite")
        
        # Initialiser les types et leurs relations en premier
        logger.info("Initialisation des types...")
        self.init_go_types(engine)
        logger.info("✅ Types initialisés")
        
        return engine
    
    def init_go_types(self, engine):
        """Initialise les types Pokémon GO et leurs relations d'efficacité."""
        from app.models.GO_tables.GO_type import GO_Type
        from app.models.GO_tables.GO_type_effectiveness import GO_TypeEffectiveness
        
        # Type effectiveness matrix (1.6 for super effective, 0.625 for not very effective, 0.391 for double not very effective)
        TYPE_EFFECTIVENESS = {
            "Normal": {"Rock": 0.625, "Ghost": 0.391, "Steel": 0.625},
            "Fighting": {"Normal": 1.6, "Flying": 0.625, "Poison": 0.625, "Rock": 1.6, "Bug": 0.625, "Ghost": 0.391, "Steel": 1.6, "Psychic": 0.625, "Ice": 1.6, "Dark": 1.6, "Fairy": 0.625},
            "Flying": {"Fighting": 1.6, "Rock": 0.625, "Bug": 1.6, "Steel": 0.625, "Grass": 1.6, "Electric": 0.625},
            "Poison": {"Poison": 0.625, "Ground": 0.625, "Rock": 0.625, "Ghost": 0.625, "Steel": 0.391, "Grass": 1.6, "Fairy": 1.6},
            "Ground": {"Flying": 0.391, "Poison": 1.6, "Rock": 1.6, "Bug": 0.625, "Steel": 1.6, "Fire": 1.6, "Grass": 0.625, "Electric": 1.6},
            "Rock": {"Fighting": 0.625, "Flying": 1.6, "Ground": 0.625, "Bug": 1.6, "Steel": 0.625, "Fire": 1.6, "Ice": 1.6},
            "Bug": {"Fighting": 0.625, "Flying": 0.625, "Poison": 0.625, "Ghost": 0.625, "Steel": 0.625, "Fire": 0.625, "Grass": 1.6, "Psychic": 1.6, "Dark": 1.6, "Fairy": 0.625},
            "Ghost": {"Normal": 0.391, "Ghost": 1.6, "Psychic": 1.6, "Dark": 0.625},
            "Steel": {"Rock": 1.6, "Steel": 0.625, "Fire": 0.625, "Water": 0.625, "Electric": 0.625, "Ice": 1.6, "Fairy": 1.6},
            "Fire": {"Rock": 0.625, "Bug": 1.6, "Steel": 1.6, "Fire": 0.625, "Water": 0.625, "Grass": 1.6, "Ice": 1.6, "Dragon": 0.625},
            "Water": {"Ground": 1.6, "Rock": 1.6, "Fire": 1.6, "Water": 0.625, "Grass": 0.625, "Dragon": 0.625},
            "Grass": {"Flying": 0.625, "Poison": 0.625, "Ground": 1.6, "Rock": 1.6, "Bug": 0.625, "Steel": 0.625, "Fire": 0.625, "Water": 1.6, "Grass": 0.625, "Dragon": 0.625},
            "Electric": {"Flying": 1.6, "Ground": 0.391, "Water": 1.6, "Grass": 0.625, "Electric": 0.625, "Dragon": 0.625},
            "Psychic": {"Fighting": 1.6, "Poison": 1.6, "Steel": 0.625, "Psychic": 0.625, "Dark": 0.391},
            "Ice": {"Flying": 1.6, "Ground": 1.6, "Steel": 0.625, "Fire": 0.625, "Water": 0.625, "Grass": 1.6, "Ice": 0.625, "Dragon": 1.6},
            "Dragon": {"Steel": 0.625, "Dragon": 1.6, "Fairy": 0.391},
            "Dark": {"Fighting": 0.625, "Ghost": 1.6, "Psychic": 1.6, "Dark": 0.625, "Fairy": 0.625},
            "Fairy": {"Fighting": 1.6, "Poison": 0.625, "Steel": 0.625, "Fire": 0.625, "Dragon": 1.6, "Dark": 1.6}
        }
        
        with Session(engine) as session:
            # Add types using the class method
            types = GO_Type.create_all_types()
            for type_data in types:
                session.add(type_data)
            session.commit()
            
            # Create type effectiveness relationships
            type_dict = {t.name: t.id for t in session.query(GO_Type).all()}
            
            for attacking_type, defenses in TYPE_EFFECTIVENESS.items():
                for defending_type, effectiveness in defenses.items():
                    effectiveness_entry = GO_TypeEffectiveness(
                        attacking_type_id=type_dict[attacking_type],
                        defending_type_id=type_dict[defending_type],
                        effectiveness=effectiveness
                    )
                    session.add(effectiveness_entry)
            
            session.commit()
            logger.info("✅ Types et relations d'efficacité initialisés")

# Instance singleton
go_db = PokemonGODatabase()

if __name__ == "__main__":
    go_db.build() 