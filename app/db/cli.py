import argparse
import logging
from pathlib import Path
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_parser():
    parser = argparse.ArgumentParser(description='PKMN.DB Database Management Tools')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup databases')
    backup_parser.add_argument('--output-dir', help='Custom output directory for backups')
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge databases')
    merge_parser.add_argument('--output', help='Output filename for merged database', default='PKMN_UNIFIED.db')
    merge_parser.add_argument('--prefix', help='Prefix for GO database tables', default='go_')
    merge_parser.add_argument('--skip-backup', action='store_true', help='Skip database backup before merging')
    merge_parser.add_argument('--force', action='store_true', help='Overwrite existing database if it exists')
    
    # List tables command
    list_parser = subparsers.add_parser('list-tables', help='List tables in a database')
    list_parser.add_argument('database', choices=['pkmn', 'go', 'unified'], help='Database to list tables from')
    
    return parser

def run_backup(args):
    from backup import backup_databases
    
    if args.output_dir:
        output_dir = Path(args.output_dir)
        if not output_dir.exists():
            os.makedirs(output_dir)
        logger.info(f"Using custom backup directory: {output_dir}")
        backup_dir = backup_databases(custom_backup_dir=output_dir)
    else:
        backup_dir = backup_databases()
    
    logger.info(f"Backup completed successfully to {backup_dir}")

def run_merge(args):
    from merge_databases import DatabaseMerger
    
    if not args.skip_backup:
        logger.info("Creating backups before merging...")
        from backup import backup_databases
        backup_databases()
    
    merger = DatabaseMerger()
    
    # Override default output path if specified
    if args.output:
        merger.merged_db_path = Path(merger.current_dir) / args.output
    
    # Check if merged DB already exists
    if merger.merged_db_path.exists() and not args.force:
        logger.error(f"Merged database already exists at {merger.merged_db_path}. Use --force to overwrite.")
        return False
    
    try:
        # Use the prefix for GO tables if specified
        merged_db_path = merger.merge_databases(go_prefix=args.prefix)
        logger.info(f"Merged database created at: {merged_db_path}")
        return True
    except Exception as e:
        logger.error(f"Error during database merge: {e}")
        return False

def list_tables(args):
    import sqlite3
    db_paths = {
        'pkmn': Path(__file__).parent / "PKMN.db",
        'go': Path(__file__).parent / "PKMNGO.db",
        'unified': Path(__file__).parent / "PKMN_UNIFIED.db"
    }
    
    db_path = db_paths[args.database]
    
    if not db_path.exists():
        logger.error(f"Database {db_path} does not exist")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        
        print(f"\nTables in {db_path.name}:")
        for table in tables:
            print(f"  - {table}")
        
        return True
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return False

def main():
    parser = setup_parser()
    args = parser.parse_args()
    
    if args.command == 'backup':
        run_backup(args)
    elif args.command == 'merge':
        run_merge(args)
    elif args.command == 'list-tables':
        list_tables(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 