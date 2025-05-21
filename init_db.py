#!/usr/bin/env python3
"""
Script pour initialiser une base de données SQLite minimale avec quelques Pokémon
Utilisé pour le déploiement sur Render
"""

import os
import sqlite3
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chemin de la base de données
DB_PATH = os.getenv("SQLITE_PATH", "app/db/V2_PKMN.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    """Initialise la base de données avec quelques Pokémon de base"""
    logger.info(f"Initialisation de la base de données SQLite à {DB_PATH}")
    
    # Vérifier si la base existe déjà
    if os.path.exists(DB_PATH):
        logger.info(f"La base de données existe déjà à {DB_PATH}")
        return
    
    # Créer la connexion
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Créer les tables
    logger.info("Création des tables...")
    
    # Table des types
    cursor.execute('''
    CREATE TABLE types (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')
    
    # Table des Pokémon
    cursor.execute('''
    CREATE TABLE pokemons (
        id INTEGER PRIMARY KEY,
        national_pokedex_number INTEGER NOT NULL,
        name_en TEXT NOT NULL,
        name_fr TEXT NOT NULL,
        type_1_id INTEGER NOT NULL,
        type_2_id INTEGER,
        sprite_url TEXT,
        cry_url TEXT,
        FOREIGN KEY (type_1_id) REFERENCES types (id),
        FOREIGN KEY (type_2_id) REFERENCES types (id)
    )
    ''')
    
    # Table des détails
    cursor.execute('''
    CREATE TABLE pokemon_details (
        pokemon_id INTEGER PRIMARY KEY,
        height_m REAL,
        weight_kg REAL,
        base_experience INTEGER,
        is_default INTEGER,
        is_legendary INTEGER,
        is_mythical INTEGER,
        color TEXT,
        shape TEXT,
        habitat TEXT,
        generation TEXT,
        FOREIGN KEY (pokemon_id) REFERENCES pokemons (id)
    )
    ''')
    
    # Table des stats
    cursor.execute('''
    CREATE TABLE pokemon_stats (
        pokemon_id INTEGER PRIMARY KEY,
        hp INTEGER,
        attack INTEGER,
        defense INTEGER,
        special_attack INTEGER,
        special_defense INTEGER,
        speed INTEGER,
        FOREIGN KEY (pokemon_id) REFERENCES pokemons (id)
    )
    ''')
    
    # Table des jeux
    cursor.execute('''
    CREATE TABLE games (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        generation_number INTEGER,
        generation_name TEXT,
        version_group TEXT,
        region_name TEXT
    )
    ''')
    
    # Insérer quelques types
    types_data = [
        (1, 'Normal'),
        (2, 'Fighting'),
        (3, 'Flying'),
        (4, 'Poison'),
        (5, 'Ground'),
        (6, 'Rock'),
        (7, 'Bug'),
        (8, 'Ghost'),
        (9, 'Steel'),
        (10, 'Fire'),
        (11, 'Water'),
        (12, 'Grass'),
        (13, 'Electric'),
        (14, 'Psychic'),
        (15, 'Ice'),
        (16, 'Dragon'),
        (17, 'Dark'),
        (18, 'Fairy')
    ]
    cursor.executemany('INSERT INTO types VALUES (?, ?)', types_data)
    
    # Insérer quelques Pokémon
    pokemon_data = [
        (1, 1, 'Bulbasaur', 'Bulbizarre', 12, 4, 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png', 'https://play.pokemonshowdown.com/audio/cries/bulbasaur.mp3'),
        (4, 4, 'Charmander', 'Salamèche', 10, None, 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png', 'https://play.pokemonshowdown.com/audio/cries/charmander.mp3'),
        (7, 7, 'Squirtle', 'Carapuce', 11, None, 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png', 'https://play.pokemonshowdown.com/audio/cries/squirtle.mp3'),
        (25, 25, 'Pikachu', 'Pikachu', 13, None, 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png', 'https://play.pokemonshowdown.com/audio/cries/pikachu.mp3')
    ]
    cursor.executemany('INSERT INTO pokemons VALUES (?, ?, ?, ?, ?, ?, ?, ?)', pokemon_data)
    
    # Insérer les détails
    details_data = [
        (1, 0.7, 6.9, 64, 1, 0, 0, 'Green', 'Quadruped', 'Grassland', 'Generation I'),
        (4, 0.6, 8.5, 62, 1, 0, 0, 'Red', 'Biped', 'Mountain', 'Generation I'),
        (7, 0.5, 9.0, 63, 1, 0, 0, 'Blue', 'Biped', 'Waters-edge', 'Generation I'),
        (25, 0.4, 6.0, 112, 1, 0, 0, 'Yellow', 'Quadruped', 'Forest', 'Generation I')
    ]
    cursor.executemany('INSERT INTO pokemon_details VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', details_data)
    
    # Insérer les stats
    stats_data = [
        (1, 45, 49, 49, 65, 65, 45),
        (4, 39, 52, 43, 60, 50, 65),
        (7, 44, 48, 65, 50, 64, 43),
        (25, 35, 55, 40, 50, 50, 90)
    ]
    cursor.executemany('INSERT INTO pokemon_stats VALUES (?, ?, ?, ?, ?, ?, ?)', stats_data)
    
    # Insérer quelques jeux
    games_data = [
        (1, 'Red', 1, 'Generation I', 'red-blue', 'Kanto'),
        (2, 'Blue', 1, 'Generation I', 'red-blue', 'Kanto'),
        (3, 'Yellow', 1, 'Generation I', 'yellow', 'Kanto'),
        (4, 'Gold', 2, 'Generation II', 'gold-silver', 'Johto'),
        (5, 'Silver', 2, 'Generation II', 'gold-silver', 'Johto')
    ]
    cursor.executemany('INSERT INTO games VALUES (?, ?, ?, ?, ?, ?)', games_data)
    
    # Commit et fermeture
    conn.commit()
    conn.close()
    
    logger.info(f"Base de données initialisée avec succès à {DB_PATH}")

if __name__ == "__main__":
    init_db() 