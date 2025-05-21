import os
import sqlite3
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from dotenv import load_dotenv
import logging
from pathlib import Path
from supabase import create_client, Client

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Chemin vers la base SQLite locale
SQLITE_PATH = os.getenv("SQLITE_PATH", "app/db/V2_PKMN.db")

class Database:
    """Classe qui gère les connexions à la base de données (SQLite ou Supabase)"""
    
    def __init__(self):
        self.supabase_client = None
        self.sqlite_conn = None
        
        # Initialiser Supabase si les identifiants sont disponibles
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                self.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
                logger.info("Connexion à Supabase établie")
            except Exception as e:
                logger.error(f"Erreur de connexion à Supabase: {str(e)}")
        
        # Initialiser SQLite comme fallback
        sqlite_path = Path(SQLITE_PATH)
        if not sqlite_path.exists():
            logger.error(f"Base de données SQLite non trouvée à {sqlite_path}")
            raise FileNotFoundError(f"Base de données SQLite non trouvée à {sqlite_path}")
        
        try:
            self.sqlite_conn = sqlite3.connect(SQLITE_PATH)
            self.sqlite_conn.row_factory = sqlite3.Row
            logger.info(f"Connexion à SQLite établie: {SQLITE_PATH}")
        except Exception as e:
            logger.error(f"Erreur de connexion à SQLite: {str(e)}")
            raise
    
    @contextmanager
    def get_db_connection(self):
        """Retourne une connexion à la base de données (SQLite par défaut)"""
        if self.sqlite_conn:
            try:
                yield self.sqlite_conn
            finally:
                # Ne pas fermer la connexion, juste commit
                self.sqlite_conn.commit()
        else:
            raise Exception("Aucune connexion à la base de données disponible")
    
    def query_supabase(self, table: str, select: str = "*", filters: Dict = None, limit: int = None) -> List[Dict[str, Any]]:
        """Exécuter une requête sur Supabase"""
        if not self.supabase_client:
            raise Exception("Connexion Supabase non disponible")
        
        query = self.supabase_client.table(table).select(select)
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        
        if hasattr(response, 'data'):
            return response.data
        return []
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Exécute une requête SQL sur SQLite"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            # Convertir les résultats en dictionnaires
            return [dict(row) for row in rows]
    
    def get_all_pokemon(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Récupère tous les Pokémon avec pagination"""
        query = """
        SELECT p.*, t1.name as type_1_name, t2.name as type_2_name
        FROM pokemons p
        JOIN types t1 ON p.type_1_id = t1.id
        LEFT JOIN types t2 ON p.type_2_id = t2.id
        ORDER BY p.national_pokedex_number
        LIMIT ? OFFSET ?
        """
        return self.execute_query(query, (limit, offset))
    
    def get_pokemon_by_id(self, pokemon_id: int) -> Dict[str, Any]:
        """Récupère un Pokémon par son ID"""
        query = """
        SELECT p.*, t1.name as type_1_name, t2.name as type_2_name
        FROM pokemons p
        JOIN types t1 ON p.type_1_id = t1.id
        LEFT JOIN types t2 ON p.type_2_id = t2.id
        WHERE p.id = ?
        """
        results = self.execute_query(query, (pokemon_id,))
        return results[0] if results else None
    
    def get_pokemon_details(self, pokemon_id: int) -> Dict[str, Any]:
        """Récupère les détails d'un Pokémon"""
        query = """
        SELECT *
        FROM pokemon_details
        WHERE pokemon_id = ?
        """
        results = self.execute_query(query, (pokemon_id,))
        return results[0] if results else None
    
    def get_pokemon_stats(self, pokemon_id: int) -> Dict[str, Any]:
        """Récupère les statistiques d'un Pokémon"""
        query = """
        SELECT *
        FROM pokemon_stats
        WHERE pokemon_id = ?
        """
        results = self.execute_query(query, (pokemon_id,))
        return results[0] if results else None
    
    def get_pokemon_moves(self, pokemon_id: int, game_version: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère les attaques d'un Pokémon, optionnellement filtrées par version de jeu"""
        query = """
        SELECT pl.*, m.*, g.name as game_name, g.generation_number
        FROM pokemon_learnsets pl
        JOIN moves m ON pl.move_id = m.id
        JOIN games g ON pl.version_group = g.version_group
        WHERE pl.pokemon_id = ?
        """
        params = (pokemon_id,)
        
        if game_version:
            query += " AND pl.version_group = ?"
            params = (pokemon_id, game_version)
        
        return self.execute_query(query, params)
    
    def get_all_games(self) -> List[Dict[str, Any]]:
        """Récupère tous les jeux"""
        query = """
        SELECT *
        FROM games
        ORDER BY generation_number, name
        """
        return self.execute_query(query)
    
    def count_pokemon(self) -> int:
        """Compte le nombre total de Pokémon"""
        query = """
        SELECT COUNT(*) as count
        FROM pokemons
        """
        results = self.execute_query(query)
        return results[0]["count"] if results else 0

# Créer une instance de la base de données
db = Database() 