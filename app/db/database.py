import os
import logging
from dotenv import load_dotenv
from supabase import create_client
from typing import Optional, Dict, Any, List

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class Database:
    """Classe qui gère les connexions à la base de données (Supabase)"""
    
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("SUPABASE_URL et SUPABASE_KEY doivent être définis")
        self.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Connexion à Supabase établie")
    
    def query_supabase(self, table: str, select: str = "*", filters: dict = None, limit: int = None) -> List[Dict[str, Any]]:
        """Exécuter une requête sur Supabase"""
        query = self.supabase_client.table(table).select(select)
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        if limit:
            query = query.limit(limit)
        response = query.execute()
        return getattr(response, "data", [])
    
    # --- Méthodes principales ---
    def get_all_pokemon(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self.query_supabase("pokemons", select="*", limit=limit)
    
    def get_pokemon_by_id(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        data = self.query_supabase("pokemons", filters={"id": pokemon_id})
        return data[0] if data else None
    
    def get_pokemon_details(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        data = self.query_supabase("pokemon_details", filters={"pokemon_id": pokemon_id})
        return data[0] if data else None
    
    def get_pokemon_stats(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        data = self.query_supabase("pokemon_stats", filters={"pokemon_id": pokemon_id})
        return data[0] if data else None
    
    def get_pokemon_moves(self, pokemon_id: int, game_version: Optional[str] = None) -> List[Dict[str, Any]]:
        filters = {"pokemon_id": pokemon_id}
        if game_version:
            filters["version_group"] = game_version
        return self.query_supabase("pokemon_learnsets", filters=filters)
    
    def get_all_games(self) -> List[Dict[str, Any]]:
        return self.query_supabase("games")
    
    def count_pokemon(self) -> int:
        data = self.query_supabase("pokemons", select="id")
        return len(data)

# Créer une instance de la base de données
db = Database() 