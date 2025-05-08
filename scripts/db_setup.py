#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour créer, réinitialiser ou supprimer la base de données Pokémon.
Utilisé pour la certification développeur IA.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from contextlib import contextmanager
from typing import Generator, Dict, Any

from sqlmodel import SQLModel, create_engine, Session

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemins de base de données
DB_FOLDER = Path('app/db')
DB_NAME = 'pokemon.db'
DB_PATH = DB_FOLDER / DB_NAME

# Configuration de connexion
@contextmanager
def get_db_connection(
    db_path: Path = DB_PATH, 
    echo: bool = False
) -> Generator[Session, None, None]:
    """
    Établit une connexion à la base de données SQLite.
    
    Args:
        db_path: Chemin vers le fichier de base de données
        echo: Afficher les requêtes SQL
        
    Yields:
        Une session SQLModel
    """
    # Assurer que le dossier existe
    db_path.parent.mkdir(exist_ok=True, parents=True)
    
    # Créer la chaîne de connexion
    connection_string = f"sqlite:///{db_path}"
    
    # Créer le moteur
    engine = create_engine(
        connection_string,
        echo=echo,
        connect_args={"check_same_thread": False}  # Nécessaire pour SQLite
    )
    
    # Créer et retourner la session
    session = Session(engine)
    try:
        logger.info(f"Connexion établie à {db_path}")
        yield session
    finally:
        session.close()
        engine.dispose()
        logger.info("Connexion fermée")

def create_tables():
    """Crée toutes les tables définies dans les modèles SQLModel."""
    from app.models import Pokemon, Type, Ability, Move, MoveCategory, TypeEffectiveness
    # Il suffit d'importer les modèles pour qu'ils soient enregistrés par SQLModel
    
    # Création d'une connexion temporaire pour créer les tables
    with get_db_connection(echo=True) as session:
        engine = session.get_bind()
        SQLModel.metadata.create_all(engine)
        logger.info("✅ Toutes les tables ont été créées")

def drop_tables(force: bool = False):
    """Supprime toutes les tables après confirmation."""
    if not force:
        user_confirm = input("\n⚠️ Êtes-vous sûr de vouloir supprimer toutes les tables ? (y/N): ")
        if user_confirm.lower() != 'y':
            logger.info("❌ Opération annulée par l'utilisateur")
            return

    with get_db_connection(echo=True) as session:
        engine = session.get_bind()
        SQLModel.metadata.drop_all(engine)
        logger.info("✅ Toutes les tables ont été supprimées")

def reset_db(force: bool = False):
    """Réinitialise la base de données (supprime et recrée les tables)."""
    drop_tables(force=force)
    create_tables()
    logger.info("✅ Réinitialisation de la base de données terminée")

def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(
        description="Utilitaire de gestion de base de données Pokémon"
    )
    parser.add_argument("--create", action="store_true", help="Créer les tables")
    parser.add_argument("--drop", action="store_true", help="Supprimer toutes les tables")
    parser.add_argument("--reset", action="store_true", help="Réinitialiser la base de données")
    parser.add_argument("--force", action="store_true", help="Forcer l'opération sans confirmation")
    
    args = parser.parse_args()
    
    if args.create:
        create_tables()
    elif args.drop:
        drop_tables(force=args.force)
    elif args.reset:
        reset_db(force=args.force)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 