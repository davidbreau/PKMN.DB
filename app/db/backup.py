import shutil
from pathlib import Path
from datetime import datetime
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_databases(custom_backup_dir=None):
    """
    Create backup copies of the PKMN.db and PKMNGO.db databases
    
    Args:
        custom_backup_dir: Custom directory path to store backups. If None, creates a 'backups' 
                          directory in the same directory as this script.
    """
    current_dir = Path(__file__).parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create backups directory if it doesn't exist
    if custom_backup_dir:
        backups_dir = Path(custom_backup_dir)
    else:
        backups_dir = current_dir / "backups"
        
    if not backups_dir.exists():
        os.makedirs(backups_dir)
        logger.info(f"Created backups directory at {backups_dir}")
    
    # Backup PKMN.db
    pkmn_db_path = current_dir / "PKMN.db"
    if pkmn_db_path.exists():
        backup_path = backups_dir / f"PKMN_backup_{timestamp}.db"
        shutil.copy2(pkmn_db_path, backup_path)
        logger.info(f"Backed up PKMN.db to {backup_path}")
    else:
        logger.warning(f"PKMN.db not found at {pkmn_db_path}")
    
    # Backup PKMNGO.db
    pkmngo_db_path = current_dir / "PKMNGO.db"
    if pkmngo_db_path.exists():
        backup_path = backups_dir / f"PKMNGO_backup_{timestamp}.db"
        shutil.copy2(pkmngo_db_path, backup_path)
        logger.info(f"Backed up PKMNGO.db to {backup_path}")
    else:
        logger.warning(f"PKMNGO.db not found at {pkmngo_db_path}")
    
    return backups_dir

if __name__ == "__main__":
    backup_databases() 