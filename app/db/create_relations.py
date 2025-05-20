import sqlite3
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DBRelationBuilder:
    def __init__(self, db_path="PKMN_MERGED.db"):
        self.current_dir = Path(__file__).parent
        self.db_path = self.current_dir / db_path
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        
        # Connection with foreign key support
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def create_mapping_tables(self):
        """Create tables to map between PKMN and PKMNGO entities"""
        # Create pokemon mapping table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS pokemon_mapping (
            go_pokemon_id INTEGER PRIMARY KEY,
            pkmn_pokemon_id INTEGER,
            FOREIGN KEY (pkmn_pokemon_id) REFERENCES pokemon(id)
        )
        """)
        
        # Create move mapping table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS move_mapping (
            go_move_id INTEGER PRIMARY KEY,
            pkmn_move_id INTEGER,
            FOREIGN KEY (pkmn_move_id) REFERENCES move(id)
        )
        """)
        
        # Create type mapping table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS type_mapping (
            go_type_id INTEGER PRIMARY KEY,
            pkmn_type_id INTEGER,
            FOREIGN KEY (pkmn_type_id) REFERENCES type(id)
        )
        """)
        
        self.conn.commit()
        logger.info("Created mapping tables")
    
    def map_pokemons_by_pokedex_number(self):
        """
        Map Pokémon GO Pokémon to main DB Pokémon primarily by pokédex number
        """
        # Get all GO Pokémon
        self.cursor.execute("SELECT id, name, pokedex_number FROM go_pokemon")
        go_pokemon = self.cursor.fetchall()
        
        # Get all PKMN Pokémon
        self.cursor.execute("SELECT id, name, pokedex_number FROM pokemon")
        pkmn_by_pokedex = {row['pokedex_number']: row['id'] for row in self.cursor.fetchall()}
        
        # Build and insert mappings
        mappings = []
        missing_count = 0
        
        for go_poke in go_pokemon:
            pokedex_num = go_poke['pokedex_number']
            if pokedex_num in pkmn_by_pokedex:
                mappings.append((go_poke['id'], pkmn_by_pokedex[pokedex_num]))
            else:
                missing_count += 1
                logger.warning(f"No main DB Pokémon found for GO Pokémon {go_poke['name']} (#{pokedex_num})")
        
        # Insert mappings
        self.cursor.executemany(
            "INSERT OR REPLACE INTO pokemon_mapping (go_pokemon_id, pkmn_pokemon_id) VALUES (?, ?)",
            mappings
        )
        self.conn.commit()
        
        logger.info(f"Mapped {len(mappings)} Pokémon by pokédex number ({missing_count} missing)")
    
    def map_moves_by_name(self):
        """
        Map Pokémon GO moves to main DB moves by name similarity
        """
        # Find all move tables in GO database
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'go_%move%'")
        move_tables = [row['name'] for row in self.cursor.fetchall()]
        
        # Get main DB moves
        self.cursor.execute("SELECT id, name FROM move")
        main_moves = {row['name'].lower().strip(): row['id'] for row in self.cursor.fetchall()}
        
        mappings = []
        missing_count = 0
        
        # Process each move table
        for table in move_tables:
            self.cursor.execute(f"SELECT id, name FROM {table}")
            for move in self.cursor.fetchall():
                go_move_id = move['id']
                go_move_name = move['name'].lower().strip()
                
                # Try exact match
                if go_move_name in main_moves:
                    mappings.append((go_move_id, main_moves[go_move_name]))
                else:
                    # Try to find similar move
                    match_found = False
                    for main_name, main_id in main_moves.items():
                        # Simple substring check - could be improved with fuzzy matching
                        if go_move_name in main_name or main_name in go_move_name:
                            mappings.append((go_move_id, main_id))
                            match_found = True
                            logger.debug(f"Partial match: GO move '{go_move_name}' -> PKMN move '{main_name}'")
                            break
                    
                    if not match_found:
                        missing_count += 1
                        logger.warning(f"No matching main DB move found for GO move '{go_move_name}'")
        
        # Insert mappings
        self.cursor.executemany(
            "INSERT OR REPLACE INTO move_mapping (go_move_id, pkmn_move_id) VALUES (?, ?)",
            mappings
        )
        self.conn.commit()
        
        logger.info(f"Mapped {len(mappings)} moves by name ({missing_count} missing)")
    
    def map_types(self):
        """Map Pokémon GO types to main DB types"""
        # Get GO types
        self.cursor.execute("SELECT id, name FROM go_type")
        go_types = self.cursor.fetchall()
        
        # Get main DB types
        self.cursor.execute("SELECT id, name FROM type")
        main_types = {row['name'].lower().strip(): row['id'] for row in self.cursor.fetchall()}
        
        mappings = []
        missing_count = 0
        
        for go_type in go_types:
            go_type_id = go_type['id']
            go_type_name = go_type['name'].lower().strip()
            
            if go_type_name in main_types:
                mappings.append((go_type_id, main_types[go_type_name]))
            else:
                missing_count += 1
                logger.warning(f"No matching main DB type found for GO type '{go_type_name}'")
        
        # Insert mappings
        self.cursor.executemany(
            "INSERT OR REPLACE INTO type_mapping (go_type_id, pkmn_type_id) VALUES (?, ?)",
            mappings
        )
        self.conn.commit()
        
        logger.info(f"Mapped {len(mappings)} types ({missing_count} missing)")
    
    def create_pokemon_go_views(self):
        """
        Create views to show Pokémon GO data with main Pokémon DB references
        """
        # View for GO Pokémon with main DB info
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS go_pokemon_complete AS
        SELECT 
            gp.id AS go_id,
            gp.name AS go_name,
            gp.pokedex_number,
            p.id AS pkmn_id,
            p.name AS pkmn_name,
            p.height,
            p.weight,
            gps.base_attack,
            gps.base_defense,
            gps.base_stamina
        FROM go_pokemon gp
        JOIN pokemon_mapping pm ON gp.id = pm.go_pokemon_id
        JOIN pokemon p ON pm.pkmn_pokemon_id = p.id
        LEFT JOIN go_pokemon_stats gps ON gp.id = gps.pokemon_id
        """)
        
        # View for GO moves with main DB info
        self.cursor.execute("""
        CREATE VIEW IF NOT EXISTS go_moves_complete AS
        SELECT 
            gm.id AS go_id,
            gm.name AS go_name,
            m.id AS pkmn_id,
            m.name AS pkmn_name,
            m.power,
            m.accuracy,
            gm.power AS go_power,
            gm.energy_delta
        FROM go_fast_move gm
        JOIN move_mapping mm ON gm.id = mm.go_move_id
        JOIN move m ON mm.pkmn_move_id = m.id
        UNION
        SELECT 
            gm.id AS go_id,
            gm.name AS go_name,
            m.id AS pkmn_id,
            m.name AS pkmn_name,
            m.power,
            m.accuracy,
            gm.power AS go_power,
            gm.energy_delta
        FROM go_charged_move gm
        JOIN move_mapping mm ON gm.id = mm.go_move_id
        JOIN move m ON mm.pkmn_move_id = m.id
        """)
        
        self.conn.commit()
        logger.info("Created Pokémon GO integration views")
    
    def build_all_relations(self):
        """Execute the full relation-building process"""
        self.create_mapping_tables()
        self.map_pokemons_by_pokedex_number()
        self.map_moves_by_name()
        self.map_types()
        self.create_pokemon_go_views()
        logger.info("All database relations have been established")

if __name__ == "__main__":
    # Create relations in the merged database
    relation_builder = DBRelationBuilder()
    try:
        relation_builder.build_all_relations()
    finally:
        relation_builder.close()
    
    logger.info("Relations building completed") 