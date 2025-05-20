#!/usr/bin/env python3
"""
Script de migration de la base de données SQLite vers Supabase.
"""

import os
import sqlite3
from pathlib import Path
import sys
from loguru import logger
from dotenv import load_dotenv
from icecream import ic

# Configurer logger
logger.remove()
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
logger.add("logs/supabase_migration_{time}.log", rotation="500 MB", level="INFO")

# Import des dépendances Supabase
try:
    from supabase import create_client, Client
except ImportError:
    logger.error("Package 'supabase' non trouvé. Veuillez l'installer avec 'pip install supabase'.")
    sys.exit(1)

class SupabaseMigration:
    def __init__(self, sqlite_path="app/db/V2_PKMN.db"):
        """
        Initialisation du script de migration
        
        Args:
            sqlite_path (str): Chemin vers la base de données SQLite
        """
        # Charger les variables d'environnement
        load_dotenv()
        
        # Vérifier les variables d'environnement Supabase
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Configurer le niveau de log si spécifié
        log_level = os.getenv("LOG_LEVEL", "INFO")
        logger.configure(handlers=[{"sink": sys.stdout, "level": log_level}])
        
        if not self.supabase_url or not self.supabase_key:
            logger.error("Erreur: Variables d'environnement SUPABASE_URL et SUPABASE_KEY requises")
            raise ValueError("Variables d'environnement SUPABASE_URL et SUPABASE_KEY requises")
        
        # Connexion à la base de données SQLite
        self.sqlite_path = Path(sqlite_path)
        if not self.sqlite_path.exists():
            logger.error(f"Erreur: Base de données SQLite non trouvée à {self.sqlite_path}")
            raise FileNotFoundError(f"Base de données SQLite non trouvée à {self.sqlite_path}")
        
        self.conn = sqlite3.connect(self.sqlite_path)
        self.conn.row_factory = sqlite3.Row
        
        # Connexion à Supabase
        ic("Tentative de connexion à Supabase", self.supabase_url)
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info(f"Connexions établies: SQLite ({self.sqlite_path}) et Supabase")
            
            # Ne pas tester la connexion avec une table spécifique car elle pourrait ne pas exister
            logger.info("Connexion à Supabase établie")
        except Exception as e:
            ic("Erreur de connexion à Supabase:", str(e))
            logger.error(f"Erreur de connexion à Supabase: {str(e)}")
            raise
    
    def get_tables(self):
        """Récupérer la liste des tables dans la base SQLite"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        return tables
    
    def get_views(self):
        """Récupérer la liste des vues dans la base SQLite"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
        views = [view[0] for view in cursor.fetchall()]
        return views
    
    def get_table_schema(self, table_name):
        """Récupérer le schéma d'une table"""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        schema = []
        for col in columns:
            col_dict = {
                "name": col["name"],
                "type": self._map_sqlite_to_postgres(col["type"]),
                "primary_key": bool(col["pk"]),
                "nullable": not bool(col["notnull"]),
                "default": col["dflt_value"]
            }
            schema.append(col_dict)
        
        return schema
    
    def _map_sqlite_to_postgres(self, sqlite_type):
        """Convertir les types SQLite en types PostgreSQL"""
        type_mapping = {
            "INTEGER": "integer",
            "TEXT": "text",
            "REAL": "double precision",
            "BLOB": "bytea",
            "BOOLEAN": "boolean"
        }
        
        # Normaliser le type en majuscules
        sqlite_type = sqlite_type.upper()
        
        # Vérifier si le type est dans notre mapping
        for key in type_mapping:
            if key in sqlite_type:
                return type_mapping[key]
        
        # Par défaut, on retourne text
        return "text"
    
    def get_table_data(self, table_name):
        """Récupérer les données d'une table"""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(row))
        
        return data
    
    def check_table_exists(self, table_name):
        """Vérifier si une table existe dans Supabase"""
        try:
            # Une façon de vérifier si la table existe est d'essayer de la sélectionner
            response = self.supabase.table(table_name).select("count").limit(1).execute()
            ic(f"Vérification table {table_name}:", response)
            return True
        except Exception as e:
            ic(f"Table {table_name} n'existe pas dans Supabase ou erreur:", str(e))
            return False
            
    def create_table(self, table_name, schema):
        """Créer une table dans Supabase si elle n'existe pas déjà"""
        # Construction de la requête SQL pour créer la table
        columns = []
        primary_keys = []
        
        for col in schema:
            column_def = f"{col['name']} {col['type']}"
            
            if not col['nullable']:
                column_def += " NOT NULL"
                
            if col['default'] is not None:
                column_def += f" DEFAULT {col['default']}"
                
            if col['primary_key']:
                primary_keys.append(col['name'])
                
            columns.append(column_def)
        
        # Ajouter la contrainte de clé primaire si elle existe
        if primary_keys:
            columns.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
        
        # Construire la requête SQL complète
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n  " + ",\n  ".join(columns) + "\n);"
        
        ic(f"SQL pour créer la table {table_name}:", create_table_sql)
        logger.info(f"Création de la table {table_name} dans Supabase")
        
        try:
            # Exécuter la requête SQL via rpc (function call)
            # Notez que cela nécessite une fonction SQL personnalisée sur Supabase
            # qui permet d'exécuter du SQL arbitraire (ce qui peut être risqué en production)
            # Pour cet exercice, nous allons simplement afficher le SQL nécessaire
            logger.info(f"SQL pour créer {table_name}: {create_table_sql}")
            return True
        except Exception as e:
            ic(f"Erreur lors de la création de la table {table_name}:", str(e))
            logger.error(f"Erreur lors de la création de la table {table_name}: {str(e)}")
            return False
    
    def migrate_table(self, table_name):
        """Migrer une table vers Supabase"""
        logger.info(f"Migration de la table: {table_name}")
        
        # Vérifier si la table existe dans Supabase
        if not self.check_table_exists(table_name):
            schema = self.get_table_schema(table_name)
            self.create_table(table_name, schema)
            return 0
            
        # Récupérer le schéma et les données
        schema = self.get_table_schema(table_name)
        data = self.get_table_data(table_name)
        
        if not data:
            logger.warning(f"Table {table_name} vide, aucune donnée à migrer")
            return 0
        
        # Débugger le premier enregistrement
        ic(f"Premier enregistrement de {table_name}:", data[0])
        
        # Insérer les données par lots de 1000 (pour éviter les timeouts)
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            
            try:
                # Nettoyage des données (important pour PostgreSQL)
                clean_batch = []
                for record in batch:
                    clean_record = {}
                    for key, value in record.items():
                        # Convertir les None en None explicites
                        if value is None:
                            clean_record[key] = None
                        else:
                            clean_record[key] = value
                    clean_batch.append(clean_record)
                
                # Insérer les données dans Supabase
                ic(f"Tentative d'insertion de {len(clean_batch)} enregistrements dans {table_name}")
                if len(clean_batch) > 0:
                    ic(f"Exemple de données à insérer:", clean_batch[0])
                response = self.supabase.table(table_name).insert(clean_batch).execute()
                
                # Vérifier s'il y a des erreurs
                if hasattr(response, 'error') and response.error:
                    ic(f"Erreur de réponse dans {table_name}:", response.error)
                    logger.error(f"Erreur lors de l'insertion dans {table_name}: {response.error}")
                else:
                    ic(f"Réponse d'insertion:", response)
                    logger.info(f"Lot {i//batch_size + 1}: {len(batch)} enregistrements insérés dans {table_name}")
                    total_inserted += len(batch)
            except Exception as e:
                ic(f"Exception dans {table_name}:", str(e), type(e))
                logger.error(f"Exception lors de l'insertion dans {table_name}: {str(e)}")
        
        return total_inserted
    
    def migrate_view(self, view_name):
        """Migrer une vue vers Supabase"""
        logger.info(f"Migration de la vue: {view_name}")
        
        # Récupérer la définition de la vue
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='view' AND name='{view_name}'")
        view_def = cursor.fetchone()
        
        if not view_def or not view_def[0]:
            logger.error(f"Impossible de récupérer la définition de la vue {view_name}")
            return False
        
        # Adapter la syntaxe SQLite à PostgreSQL
        sql = view_def[0]
        
        # Convertir les noms de colonnes entre guillemets
        # Remplacer les fonctions spécifiques à SQLite
        sql = sql.replace("CREATE VIEW", "CREATE OR REPLACE VIEW")
        
        # Exécuter la requête SQL pour créer la vue dans Supabase
        try:
            # Pour créer une vue dans Supabase, il faut utiliser la fonction rpc
            # On peut utiliser une requête SQL brute via supabase.rpc
            # Mais c'est difficile à faire directement avec le client Python
            # Il est préférable de créer les vues manuellement dans l'interface Supabase
            
            logger.info(f"Définition de vue à créer manuellement dans Supabase: {sql}")
            return True
        except Exception as e:
            logger.error(f"Exception lors de la création de la vue {view_name}: {e}")
            return False
    
    def migrate_all(self):
        """Migrer toutes les tables et vues"""
        # Récupérer la liste des tables et vues
        tables = self.get_tables()
        views = self.get_views()
        
        # Filtrer les tables système de SQLite
        tables = [t for t in tables if not t.startswith('sqlite_')]
        
        # Statistiques
        stats = {
            "tables_migrated": 0,
            "total_tables": len(tables),
            "records_inserted": 0,
            "views_migrated": 0,
            "total_views": len(views),
            "failed_tables": [],
            "failed_views": []
        }
        
        # Migrer les tables
        for table in tables:
            try:
                inserted = self.migrate_table(table)
                stats["records_inserted"] += inserted
                stats["tables_migrated"] += 1
            except Exception as e:
                logger.error(f"Échec de la migration de la table {table}: {e}")
                stats["failed_tables"].append(table)
        
        # Migrer les vues
        for view in views:
            try:
                if self.migrate_view(view):
                    stats["views_migrated"] += 1
                else:
                    stats["failed_views"].append(view)
            except Exception as e:
                logger.error(f"Échec de la migration de la vue {view}: {e}")
                stats["failed_views"].append(view)
        
        # Afficher les statistiques
        logger.info(f"Migration terminée: {stats['tables_migrated']}/{stats['total_tables']} tables migrées, "
                   f"{stats['records_inserted']} enregistrements insérés")
        logger.info(f"Vues: {stats['views_migrated']}/{stats['total_views']} définitions exportées")
        
        if stats["failed_tables"]:
            logger.warning(f"Tables en échec: {', '.join(stats['failed_tables'])}")
        if stats["failed_views"]:
            logger.warning(f"Vues en échec: {', '.join(stats['failed_views'])}")
        
        return stats

def main():
    """Fonction principale"""
    try:
        # Créer le répertoire de logs s'il n'existe pas
        logs_dir = Path("logs")
        if not logs_dir.exists():
            os.makedirs(logs_dir)
        
        # Lancer la migration
        migration = SupabaseMigration()
        
        # Récupérer toutes les tables et générer le SQL pour les créer
        tables = migration.get_tables()
        tables = [t for t in tables if not t.startswith('sqlite_')]
        
        # Générer les scripts SQL pour toutes les tables
        create_tables_sql = []
        for table in tables:
            schema = migration.get_table_schema(table)
            columns = []
            primary_keys = []
            
            for col in schema:
                column_def = f"{col['name']} {col['type']}"
                
                if not col['nullable']:
                    column_def += " NOT NULL"
                    
                if col['default'] is not None:
                    column_def += f" DEFAULT {col['default']}"
                    
                if col['primary_key']:
                    primary_keys.append(col['name'])
                    
                columns.append(column_def)
            
            # Ajouter la contrainte de clé primaire si elle existe
            if primary_keys:
                columns.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
            
            # Construire la requête SQL complète
            create_table_sql = f"CREATE TABLE IF NOT EXISTS {table} (\n  " + ",\n  ".join(columns) + "\n);"
            create_tables_sql.append(create_table_sql)
        
        # Écrire le SQL dans un fichier pour référence
        with open("create_tables.sql", "w") as f:
            f.write("\n\n".join(create_tables_sql))
        
        logger.info(f"Scripts SQL pour créer les tables générés dans create_tables.sql")
        logger.info(f"Veuillez créer les tables manuellement dans Supabase avant de continuer")
        logger.info(f"Après avoir créé les tables, supprimez la ligne 'return 0' ci-dessous pour continuer la migration")
        
        # Pour la sécurité, on s'arrête ici et on laisse l'utilisateur créer les tables manuellement
        return 0
        
        # Continuer avec la migration des données
        stats = migration.migrate_all()
        
        return 0
    except Exception as e:
        logger.exception(f"Erreur lors de la migration: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 