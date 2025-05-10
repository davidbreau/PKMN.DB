#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(message)s')

class DataBase:
    _instance: Optional['DataBase'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.db_path = Path('app/db/PKMN.db')
            self.db_path.parent.mkdir(exist_ok=True, parents=True)
            self.engine = create_engine(
                f"sqlite:///{self.db_path}", 
                echo=True, 
                connect_args={"check_same_thread": False}
            )
            self.initialized = True
    
    def init_db(self):
        """Initialise la base de données avec les tables."""
        from app.tables import (
            Ability, Evolution, Game, Machine, Move, 
            PokedexNumber, PokemonAbility, PokemonDetail, 
            PokemonLearnset, PokemonSprite, PokemonStat, 
            Pokemon, TypeEffectiveness, Type
        )
        
        logging.info(f"Initialisation de la base de données dans {self.db_path}...")
        SQLModel.metadata.create_all(self.engine)
        logging.info("✅ Base de données initialisée")
    
    def get_session(self) -> Session:
        """Retourne une nouvelle session de base de données."""
        return Session(self.engine)
    
    def reset_db(self):
        """Réinitialise la base de données en supprimant toutes les tables."""
        SQLModel.metadata.drop_all(self.engine)
        logging.info("✅ Base de données réinitialisée")

# Instance singleton de la base de données
db = DataBase() 