import shutil
import os
from pathlib import Path
import re
from sqlmodel import Session, select
import sqlite3
import argparse
from loguru import logger

# Définir les chemins par défaut après les imports
DEFAULT_PKMN_PATH = "PKMN copy.db"
DEFAULT_PKMNGO_PATH = "PKMNGO copy.db"
DEFAULT_OUTPUT_PATH = "PKMN copy V2.db"

# Import notre engine SQLAlchemy personnalisé
from app.db.engine import engine

# Import des modèles de tables existants
from app.models.tables import Pokemon
# Import des modèles GO
from app.models.GO_tables import GO_Pokemon, GO_PokemonStats, GO_Move, GO_PokemonLearnset, GO_Type, GO_TypeEffectiveness

class DatabaseFusion:
    def __init__(self, pkmn_path=DEFAULT_PKMN_PATH, pkmngo_path=DEFAULT_PKMNGO_PATH, output_path=DEFAULT_OUTPUT_PATH):
        self.current_dir = Path(__file__).parent
        self.pkmn_db_path = self.current_dir / pkmn_path
        self.pkmngo_db_path = self.current_dir / pkmngo_path
        self.merged_db_path = self.current_dir / output_path
        
        # Ensure source databases exist
        if not self.pkmn_db_path.exists():
            raise FileNotFoundError(f"{pkmn_path} not found at {self.pkmn_db_path}")
        if not self.pkmngo_db_path.exists():
            raise FileNotFoundError(f"{pkmngo_path} not found at {self.pkmngo_db_path}")
    
    def normalize_name(self, name):
        """Normalize a name for better matching"""
        if not name:
            return ""
        # Remove special characters, except hyphen
        name = re.sub(r'[^\w\s-]', '', name)
        # Replace multiple spaces with single space
        name = re.sub(r'\s+', ' ', name)
        # Convert to lowercase and strip
        return name.lower().strip()
    
    def get_tables(self, db_path):
        """Get all tables from a database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        return tables
    
    def copy_database_file(self, source, destination):
        """Copy the physical database file"""
        if destination.exists():
            os.remove(destination)
            logger.info(f"Removed existing {destination}")
        
        shutil.copy2(source, destination)
        logger.info(f"Copied database from {source} to {destination}")
    
    def get_table_data(self, db_path, table_name, columns=None):
        """Get data from a table, optionally selecting specific columns"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if columns:
            cols = ", ".join(columns)
            cursor.execute(f"SELECT {cols} FROM {table_name}")
        else:
            cursor.execute(f"SELECT * FROM {table_name}")
            
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def create_pokemon_mapping(self):
        """
        Create a mapping between Pokémon GO and Pokémon DB entries based on pokédex number
        Returns a dict mapping GO Pokémon IDs to main DB IDs
        """
        # Get Pokémon from main DB indexed by pokédex number
        pkmn_pokemon = self.get_table_data(self.pkmn_db_path, "pokemons", ["id", "national_pokedex_number"])
        pkmn_by_pokedex = {row['national_pokedex_number']: row['id'] for row in pkmn_pokemon}
        
        # Get Pokémon from GO DB
        go_pokemon = self.get_table_data(self.pkmngo_db_path, "go_pokemons", ["id", "name", "pokedex_number"])
        
        # Map GO Pokémon IDs to main DB IDs
        pokemon_mapping = {}
        for row in go_pokemon:
            go_id = row['id']
            pokedex_num = row['pokedex_number']
            
            if pokedex_num in pkmn_by_pokedex:
                pokemon_mapping[go_id] = pkmn_by_pokedex[pokedex_num]
            else:
                logger.warning(f"No matching main DB Pokémon for GO Pokémon {row['name']} (#{pokedex_num})")
        
        logger.info(f"Created mapping between {len(pokemon_mapping)} GO Pokémon and main DB Pokémon")
        return pokemon_mapping
    
    def create_move_mapping(self):
        """
        Create a mapping between GO moves and main DB moves based on name similarity
        Returns a dict mapping GO move IDs to main DB move IDs
        """
        # Get moves from main DB
        pkmn_moves = self.get_table_data(self.pkmn_db_path, "moves", ["id", "name"])
        pkmn_moves_by_name = {self.normalize_name(row['name']): row['id'] for row in pkmn_moves}
        
        # Initialize move mapping dict
        move_mapping = {}
        
        # Check for move tables in the GO DB
        go_tables = self.get_tables(self.pkmngo_db_path)
        move_tables = [t for t in go_tables if 'move' in t.lower()]
        
        for table in move_tables:
            go_moves = self.get_table_data(self.pkmngo_db_path, table, ["id", "name"])
            
            for move in go_moves:
                go_id = move['id']
                go_name = self.normalize_name(move['name'])
                
                # Try exact match first
                if go_name in pkmn_moves_by_name:
                    move_mapping[go_id] = pkmn_moves_by_name[go_name]
                else:
                    # Try partial match
                    matches = [name for name in pkmn_moves_by_name.keys() 
                              if go_name in name or name in go_name]
                    
                    if matches:
                        # Pick the shortest match as likely most similar
                        best_match = min(matches, key=len)
                        move_mapping[go_id] = pkmn_moves_by_name[best_match]
                    else:
                        logger.warning(f"No matching main DB move for GO move '{move['name']}'")
        
        logger.info(f"Created mapping between {len(move_mapping)} GO moves and main DB moves")
        return move_mapping
    
    def create_type_mapping(self):
        """
        Create a mapping between GO types and main DB types
        Returns a dict mapping GO type IDs to main DB type IDs
        """
        # Get types from main DB
        pkmn_types = self.get_table_data(self.pkmn_db_path, "types", ["id", "name"])
        pkmn_types_by_name = {self.normalize_name(row['name']): row['id'] for row in pkmn_types}
        
        # Check if GO type table exists
        go_tables = self.get_tables(self.pkmngo_db_path)
        if 'go_types' not in go_tables:
            logger.warning("No go_types table found in GO database")
            return {}
        
        # Get GO types
        go_types = self.get_table_data(self.pkmngo_db_path, "go_types", ["id", "name"])
        
        # Map GO type IDs to main DB type IDs
        type_mapping = {}
        for row in go_types:
            go_id = row['id']
            go_name = self.normalize_name(row['name'])
            
            if go_name in pkmn_types_by_name:
                type_mapping[go_id] = pkmn_types_by_name[go_name]
            else:
                logger.warning(f"No matching main DB type for GO type '{row['name']}'")
        
        logger.info(f"Created mapping between {len(type_mapping)} GO types and main DB types")
        return type_mapping
    
    def adapt_and_copy_go_tables(self, pokemon_mapping, move_mapping, type_mapping):
        """
        Copy tables from GO database to merged database, adapting the IDs based on mappings
        """
        # Copy the main database file as our starting point
        self.copy_database_file(self.pkmn_db_path, self.merged_db_path)
        
        # Connect to both source and destination databases
        go_conn = sqlite3.connect(self.pkmngo_db_path)
        go_conn.row_factory = sqlite3.Row
        
        merged_conn = sqlite3.connect(self.merged_db_path)
        
        # Get all GO tables
        go_tables = self.get_tables(self.pkmngo_db_path)
        
        # Skip internal SQLite tables and process the rest
        for table_name in go_tables:
            if table_name == "sqlite_sequence":
                continue
            
            # Keep the original table name if it already has go_ prefix
            if table_name.startswith('go_'):
                new_table_name = table_name
            else:
                new_table_name = f"go_{table_name}"
            
            try:
                # Get table schema
                cursor = go_conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Create table in merged database
                column_defs = [f"{col['name']} {col['type']} {'PRIMARY KEY' if col['pk'] else ''}" 
                              for col in columns]
                merged_conn.execute(f"CREATE TABLE IF NOT EXISTS {new_table_name} ({', '.join(column_defs)})")
                
                # Get data from GO database
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                if not rows:
                    logger.info(f"Table {table_name} is empty, skipping data copy")
                    continue
                
                # Insert data into merged database with adapted IDs
                for row in rows:
                    # Create a dict from the row
                    row_dict = dict(zip([col['name'] for col in columns], row))
                    
                    # Adapt pokemon_id references
                    if 'pokemon_id' in row_dict and row_dict['pokemon_id'] in pokemon_mapping:
                        if table_name in ['go_pokemon_learnsets', 'go_pokemon_stats']:
                            # Use original ID for these tables, as they relate to go_pokemon table
                            pass
                        else:
                            row_dict['pokemon_id'] = pokemon_mapping[row_dict['pokemon_id']]
                    
                    # Adapt move_id references
                    if 'move_id' in row_dict and row_dict['move_id'] in move_mapping:
                        if table_name in ['go_pokemon_learnsets']:
                            # Use original ID for these tables, as they relate to go_moves
                            pass
                        else:
                            row_dict['move_id'] = move_mapping[row_dict['move_id']]
                    
                    # Adapt type_id references
                    if 'type_id' in row_dict and row_dict['type_id'] in type_mapping:
                        if table_name in ['go_types_effectiveness', 'go_moves']:
                            # Use original ID for these tables
                            pass
                        else:
                            row_dict['type_id'] = type_mapping[row_dict['type_id']]
                    
                    # Insert the adapted row
                    placeholders = ", ".join(["?"] * len(row_dict))
                    columns_str = ", ".join(row_dict.keys())
                    merged_conn.execute(
                        f"INSERT INTO {new_table_name} ({columns_str}) VALUES ({placeholders})",
                        list(row_dict.values())
                    )
                
                merged_conn.commit()
                logger.info(f"Copied and adapted table {table_name} to {new_table_name}")
                
            except Exception as e:
                logger.error(f"Error copying table {table_name}: {e}")
                continue
        
        # Close connections
        go_conn.close()
        merged_conn.close()
    
    def update_go_pokemon_ids(self, conn, pokemon_mapping):
        """
        Vérifie et aligne les IDs entre go_pokemons et pokemons basé sur le nom et les types.
        Met à jour les références dans les autres tables GO.
        """
        try:
            # Vérifier la structure de la table go_pokemons
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(go_pokemons)")
            go_columns = {col[1]: col[0] for col in cursor.fetchall()}
            logger.info(f"Structure de la table go_pokemons: {', '.join(go_columns.keys())}")
            
            # Vérifier si les colonnes attendues existent
            required_columns = ['id', 'name', 'pokedex_number']
            for col in required_columns:
                if col not in go_columns:
                    logger.error(f"Colonne attendue '{col}' non trouvée dans go_pokemons")
                    return
            
            # Ajouter une colonne pour stocker l'ID principal
            if "main_id" not in go_columns:
                conn.execute("ALTER TABLE go_pokemons ADD COLUMN main_id INTEGER")
            
            # Pour chaque Pokémon GO, trouver son équivalent dans la base principale
            query = "SELECT id, name, pokedex_number FROM go_pokemons"
            cursor.execute(query)
            go_pokemons = cursor.fetchall()
            
            # Récupérer tous les Pokémon principaux
            cursor.execute("""
                SELECT p.id, p.name_en, p.national_pokedex_number
                FROM pokemons p
            """)
            main_pokemons = {row[0]: row for row in cursor.fetchall()}
            
            # Pour chaque Pokémon GO
            updates_count = 0
            for go_id, go_name, pokedex_num in go_pokemons:
                # Chercher par numéro de Pokédex d'abord (méthode la plus fiable)
                found_id = None
                for p_id, p in main_pokemons.items():
                    if p[2] == pokedex_num:  # national_pokedex_number
                        found_id = p_id
                        break
                
                # Si pas trouvé par numéro de Pokédex, chercher par nom
                if not found_id:
                    go_name_lower = go_name.lower()
                    for p_id, p in main_pokemons.items():
                        p_name_lower = p[1].lower()  # name_en
                        
                        # Vérifier si les noms sont similaires
                        if go_name_lower in p_name_lower or p_name_lower in go_name_lower:
                            found_id = p_id
                            break
                
                # Mettre à jour l'ID principal
                if found_id:
                    conn.execute("UPDATE go_pokemons SET main_id = ? WHERE id = ?", 
                                (found_id, go_id))
                    updates_count += 1
            
            logger.info(f"Correspondance trouvée pour {updates_count}/{len(go_pokemons)} Pokémon GO")
            
            # Mettre à jour les références dans go_pokemon_stats
            conn.execute("""
                UPDATE go_pokemon_stats
                SET pokemon_id = (
                    SELECT main_id FROM go_pokemons WHERE id = go_pokemon_stats.pokemon_id
                )
                WHERE EXISTS (
                    SELECT 1 FROM go_pokemons 
                    WHERE id = go_pokemon_stats.pokemon_id AND main_id IS NOT NULL
                )
            """)
            
            # Mettre à jour les références dans go_pokemon_learnsets
            conn.execute("""
                UPDATE go_pokemon_learnsets
                SET pokemon_id = (
                    SELECT main_id FROM go_pokemons WHERE id = go_pokemon_learnsets.pokemon_id
                )
                WHERE EXISTS (
                    SELECT 1 FROM go_pokemons 
                    WHERE id = go_pokemon_learnsets.pokemon_id AND main_id IS NOT NULL
                )
            """)
            
            conn.commit()
            logger.info("Références mises à jour dans go_pokemon_stats et go_pokemon_learnsets")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'alignement des IDs de Pokémon: {e}")

    def merge_types(self, conn, type_mapping):
        """
        Fusionner les types GO et les types principaux en ajoutant la colonne weather_boost
        """
        try:
            # D'abord, vérifier que la colonne weather_boost n'existe pas déjà dans la table types
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(types)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Ajouter la colonne weather_boost si elle n'existe pas
            if "weather_boost" not in columns:
                conn.execute("ALTER TABLE types ADD COLUMN weather_boost TEXT")
                logger.info("Ajout de la colonne weather_boost à la table types")
            
            # Mettre à jour les types avec les informations de weather_boost de GO
            for go_type_id, main_type_id in type_mapping.items():
                cursor.execute("SELECT weather_boost FROM go_types WHERE id = ?", (go_type_id,))
                result = cursor.fetchone()
                if result:
                    weather_boost = result[0]
                    conn.execute("UPDATE types SET weather_boost = ? WHERE id = ?", 
                                (weather_boost, main_type_id))
            
            conn.commit()
            logger.info("Types fusionnés avec succès: ajout des weather_boost aux types principaux")
            
        except Exception as e:
            logger.error(f"Erreur lors de la fusion des types: {e}")

    def remove_redundant_tables(self, conn):
        """
        Supprimer les tables go_pokemons et go_types qui sont désormais redondantes
        """
        try:
            # Supprimer la table go_pokemons car ses données sont maintenant référencées via les IDs principaux
            conn.execute("DROP TABLE IF EXISTS go_pokemons")
            logger.info("Table go_pokemons supprimée car redondante")
            
            # Supprimer la table go_types car ses données ont été fusionnées dans la table types principale
            conn.execute("DROP TABLE IF EXISTS go_types")
            logger.info("Table go_types supprimée car redondante")
            
            conn.commit()
        except Exception as e:
            logger.error(f"Erreur lors de la suppression des tables redondantes: {e}")
    
    def create_views(self, conn, pokemon_mapping):
        """Create useful views in the merged database"""
        try:
            # View for Pokémon GO stats linked to main Pokémon
            conn.execute("""
            CREATE VIEW IF NOT EXISTS v_pokemon_with_go_stats AS
            SELECT 
                p.id as pokemon_id,
                p.name_en as pokemon_name,
                p.national_pokedex_number as pokedex_number,
                gps.attack as go_attack,
                gps.defense as go_defense,
                gps.stamina as go_stamina,
                gps.max_cp as go_max_cp
            FROM 
                pokemons p
            LEFT JOIN 
                go_pokemon_stats gps ON p.id = gps.pokemon_id
            """)
            
            # View for Pokémon GO moves linked to main moves
            conn.execute("""
            CREATE VIEW IF NOT EXISTS v_go_moves AS
            SELECT 
                m.id as move_id,
                m.name as move_name,
                gm.name as go_name,
                gm.damage as go_damage,
                gm.energy as go_energy,
                gm.duration as go_duration,
                gm.pvp_damage as go_pvp_damage,
                gm.pvp_energy as go_pvp_energy,
                m.damage as main_damage,
                m.precision as main_precision,
                gm.is_fast
            FROM 
                moves m
            JOIN 
                go_moves gm ON lower(m.name) = lower(gm.name) OR m.name LIKE '%' || gm.name || '%' OR gm.name LIKE '%' || m.name || '%'
            """)
            
            # Vue pour les moveset GO des Pokémon
            conn.execute("""
            CREATE VIEW IF NOT EXISTS v_pokemon_go_moveset AS
            SELECT
                p.id as pokemon_id,
                p.name_en as pokemon_name,
                gm.name as move_name,
                gpl.is_fast,
                gm.damage,
                gm.energy,
                gm.duration,
                gm.pvp_damage,
                gm.pvp_energy
            FROM
                pokemons p
            JOIN
                go_pokemon_learnsets gpl ON p.id = gpl.pokemon_id
            JOIN
                go_moves gm ON gpl.move_id = gm.id
            """)
            
            conn.commit()
            logger.info("Created views for easier querying of the merged database")
            
        except Exception as e:
            logger.error(f"Error creating views: {e}")
    
    def merge_databases(self):
        """Execute the complete merging process"""
        # Create mappings
        pokemon_mapping = self.create_pokemon_mapping()
        move_mapping = self.create_move_mapping()
        type_mapping = self.create_type_mapping()
        
        # Adapt and copy GO tables to merged database
        self.adapt_and_copy_go_tables(pokemon_mapping, move_mapping, type_mapping)
        
        # Connect to the merged database for additional operations
        merged_conn = sqlite3.connect(self.merged_db_path)
        
        # 1. Vérifier et aligner les IDs entre go_pokemons et pokemons
        self.update_go_pokemon_ids(merged_conn, pokemon_mapping)
        
        # 2. Fusionner les types en ajoutant la colonne weather_boost
        self.merge_types(merged_conn, type_mapping)
        
        # 3. Supprimer go_pokemons et go_types qui sont désormais redondantes
        self.remove_redundant_tables(merged_conn)
        
        # Créer les vues pour faciliter les requêtes
        self.create_views(merged_conn, pokemon_mapping)
        
        # Fermer la connexion
        merged_conn.close()
        
        logger.info(f"Database fusion completed successfully: {self.merged_db_path}")
        return self.merged_db_path

def parse_arguments():
    parser = argparse.ArgumentParser(description="Fusionne PKMN.db et PKMNGO.db en une nouvelle base de données unifiée V2")
    
    parser.add_argument("--pkmn", default=DEFAULT_PKMN_PATH, help="Chemin vers la base de données PKMN.db (ou sa copie)")
    parser.add_argument("--pkmngo", default=DEFAULT_PKMNGO_PATH, help="Chemin vers la base de données PKMNGO.db (ou sa copie)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH, help="Nom du fichier de sortie pour la base fusionnée V2")
    
    return parser.parse_args()

if __name__ == "__main__":
    # Configuration de loguru
    logger.add("logs/merge_{time}.log", rotation="500 MB", level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
    
    args = parse_arguments()
    
    try:
        current_dir = Path(__file__).parent
        
        # Create logs directory if it doesn't exist
        logs_dir = current_dir / "logs"
        if not logs_dir.exists():
            os.makedirs(logs_dir)
            logger.info(f"Created logs directory at {logs_dir}")
        
        # Merge databases without modifying originals
        fusion = DatabaseFusion(args.pkmn, args.pkmngo, args.output)
        merged_db_path = fusion.merge_databases()
        
        print("🚀 Fusion V2 terminée!")
        print(f"📊 Sources: {args.pkmn} + {args.pkmngo}")
        print(f"✅ Base de données unifiée V2 créée à {merged_db_path}")
        logger.success(f"FUSION TERMINÉE: Base de données unifiée V2 créée à {merged_db_path}")
        
    except Exception as e:
        logger.exception(f"Erreur pendant la fusion des bases de données: {e}") 