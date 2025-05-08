#!/usr/bin/env python
# -*- coding: utf-8 -*-

#### uv run app/db/setup.py

import logging
from pathlib import Path
from sqlmodel import SQLModel, create_engine

logging.basicConfig(level=logging.INFO, format='%(message)s')


DB_PATH = Path('app/db/PKMN.db')
DB_PATH.parent.mkdir(exist_ok=True, parents=True)
    #Checks if the database path exists
           
engine = create_engine(
    f"sqlite:///{DB_PATH}", 
    echo=True, 
    connect_args={"check_same_thread": False}  
)

def build():
    """
    Crée toutes les tables dans la base de données.
    
    Les imports sont faits dans la fonction pour éviter les imports circulaires
    potentiels entre les modèles et le module de base de données.
    """
    # Import local des modèles - évite les imports circulaires
    from app.models import Ability, Evolution, Game, Machine, Move, PokedexNumber, PokemonAbility, PokemonDetail, PokemonLearnset, PokemonSprite, PokemonStat, Pokemon, TypeEffectiveness, Type
    
    # Créer les tables en utilisant les métadonnées des modèles SQLModel
    logging.info(f"Création des tables dans {DB_PATH}...")
    SQLModel.metadata.create_all(engine)
    logging.info("✅ Toutes les tables ont été créées")

# Point d'entrée quand le script est exécuté directement
if __name__ == "__main__":
    build()  # Appel de la fonction build() quand le script est exécuté
