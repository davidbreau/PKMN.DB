import sqlite3
import logging
from pathlib import Path
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseMerger:
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.pkmn_db_path = self.current_dir / "PKMN.db"
        self.pkmngo_db_path = self.current_dir / "PKMNGO.db"
        self.merged_db_path = self.current_dir / "PKMN_UNIFIED.db"
        
        # Ensure source databases exist
        if not self.pkmn_db_path.exists():
            raise FileNotFoundError(f"PKMN.db not found at {self.pkmn_db_path}")
        if not self.pkmngo_db_path.exists():
            raise FileNotFoundError(f"PKMNGO.db not found at {self.pkmngo_db_path}")
    
    def get_tables(self, db_path):
        """Get all tables from a database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        return tables
    
    def get_table_schema(self, db_path, table_name):
        """Get the schema for a specific table"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        schema = cursor.fetchall()
        conn.close()
        return schema
    
    def copy_table(self, source_db, dest_db, table_name, prefix=""):
        """Copy a table from source db to destination db with optional prefix"""
        source_conn = sqlite3.connect(source_db)
        dest_conn = sqlite3.connect(dest_db)
        
        source_cursor = source_conn.cursor()
        dest_cursor = dest_conn.cursor()
        
        # Get table schema and create corresponding table in destination
        source_cursor.execute(f"PRAGMA table_info({table_name});")
        columns = source_cursor.fetchall()
        
        column_defs = [f"{col[1]} {col[2]} {'PRIMARY KEY' if col[5] else ''}" for col in columns]
        new_table_name = f"{prefix}{table_name}" if prefix else table_name
        
        try:
            dest_cursor.execute(f"CREATE TABLE IF NOT EXISTS {new_table_name} ({', '.join(column_defs)})")
            
            # Get all data from source table
            source_cursor.execute(f"SELECT * FROM {table_name}")
            rows = source_cursor.fetchall()
            
            # Insert data into destination table
            if rows:
                placeholders = ', '.join(['?'] * len(columns))
                dest_cursor.executemany(f"INSERT OR IGNORE INTO {new_table_name} VALUES ({placeholders})", rows)
                
            dest_conn.commit()
            logger.info(f"Copied table {table_name} with {len(rows)} rows to {new_table_name}")
            
        except sqlite3.Error as e:
            logger.error(f"Error copying table {table_name}: {e}")
        
        finally:
            source_conn.close()
            dest_conn.close()
    
    def merge_databases(self, go_prefix="go_"):
        """
        Merge PKMN.db and PKMNGO.db into a new unified database
        
        Args:
            go_prefix: Prefix to add to GO database tables that conflict with PKMN tables
        """
        # Delete merged db if it already exists
        if self.merged_db_path.exists():
            os.remove(self.merged_db_path)
            logger.info(f"Removed existing {self.merged_db_path}")
        
        # Create the new database
        conn = sqlite3.connect(self.merged_db_path)
        conn.close()
        logger.info(f"Created new database at {self.merged_db_path}")
        
        # Copy tables from PKMN.db
        pkmn_tables = self.get_tables(self.pkmn_db_path)
        for table in pkmn_tables:
            if table != "sqlite_sequence":  # Skip SQLite internal tables
                self.copy_table(self.pkmn_db_path, self.merged_db_path, table)
        
        # Copy tables from PKMNGO.db with prefix to avoid conflicts
        pkmngo_tables = self.get_tables(self.pkmngo_db_path)
        for table in pkmngo_tables:
            if table != "sqlite_sequence":  # Skip SQLite internal tables
                # Check if table already exists in the merged DB
                if table in pkmn_tables:
                    self.copy_table(self.pkmngo_db_path, self.merged_db_path, table, prefix=go_prefix)
                else:
                    self.copy_table(self.pkmngo_db_path, self.merged_db_path, table)
        
        logger.info("Database merge completed successfully!")
        return self.merged_db_path

if __name__ == "__main__":
    # First backup the databases
    from backup import backup_databases
    backup_databases()
    
    # Then merge them
    merger = DatabaseMerger()
    merged_db_path = merger.merge_databases()
    logger.info(f"Merged database created at: {merged_db_path}") 