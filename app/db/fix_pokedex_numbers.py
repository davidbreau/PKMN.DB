import sys
import os
from pathlib import Path
import re
import logging
from difflib import SequenceMatcher

# Ajouter le répertoire parent au path pour pouvoir importer les modules du projet
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlmodel import SQLModel, Session, create_engine, select, update
from app.models.tables.pokemon import Pokemon

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chemin vers la base de données
DB_PATH = Path('app/db/PKMN.db')
SQLITE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

def clean_name(name):
    """Nettoie un nom pour faciliter la comparaison"""
    # Supprimer les préfixes et suffixes communs pour les formes
    cleaned = re.sub(r'(Mega|Alolan|Galarian|Hisuian|Form|Mask|Mode|Style|Rider|Primal|Eternamax|Gigantamax|Rapid-Strike|Single-Strike)\s+', '', name)
    # Supprimer les descriptions entre parenthèses
    cleaned = re.sub(r'\([^)]*\)', '', cleaned)
    # Nettoyer les espaces supplémentaires
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def similarity(a, b):
    """Calcule la similarité entre deux chaînes de caractères"""
    return SequenceMatcher(None, a, b).ratio()

def find_base_pokemon(form_name, all_pokemon):
    """Trouve le Pokémon de base correspondant à une forme spéciale"""
    # Nettoyer le nom de la forme
    clean_form_name = clean_name(form_name)
    
    # Initialiser les variables pour trouver la meilleure correspondance
    best_match = None
    best_score = 0
    
    # Parcourir tous les Pokémon de base (ID <= 1025)
    for pokemon in all_pokemon:
        if pokemon.id > 1025:
            continue
            
        # Comparer avec le nom anglais
        clean_base_name = clean_name(pokemon.name_en)
        score = similarity(clean_form_name, clean_base_name)
        
        # Si c'est une meilleure correspondance, la conserver
        if score > best_score:
            best_score = score
            best_match = pokemon
    
    # Une correspondance est considérée bonne si le score est supérieur à 0.6
    if best_match and best_score > 0.6:
        return best_match
    
    # Si aucune bonne correspondance n'est trouvée, rechercher des mots communs
    words_form = set(clean_form_name.lower().split())
    
    for pokemon in all_pokemon:
        if pokemon.id > 1025:
            continue
            
        words_base = set(clean_name(pokemon.name_en).lower().split())
        common_words = words_form.intersection(words_base)
        
        # Si des mots en commun et score > 0.4, c'est probablement une correspondance
        if common_words and similarity(clean_form_name, clean_name(pokemon.name_en)) > 0.4:
            return pokemon
    
    # Aucune correspondance trouvée
    return None

def fix_pokedex_numbers():
    """Corrige les numéros de Pokédex National pour les formes spéciales"""
    logger.info("Début de la correction des numéros de Pokédex National...")
    
    with Session(engine) as session:
        # Récupérer tous les Pokémon
        all_pokemon = session.exec(select(Pokemon)).all()
        
        # Liste des Pokémon pour lesquels un numéro de Pokédex National a été corrigé
        fixed_pokemon = []
        
        # Parcourir les Pokémon avec ID > 10000 (formes spéciales)
        for pokemon in all_pokemon:
            if pokemon.id <= 10000:
                continue
                
            # Trouver le Pokémon de base correspondant
            base_pokemon = find_base_pokemon(pokemon.name_en, all_pokemon)
            
            if base_pokemon:
                # Enregistrer l'ancien numéro pour le logging
                old_number = pokemon.national_pokedex_number
                
                # Mettre à jour le numéro de Pokédex National
                pokemon.national_pokedex_number = base_pokemon.national_pokedex_number
                
                # Ajouter à la liste des Pokémon corrigés
                fixed_pokemon.append((pokemon.id, pokemon.name_en, old_number, base_pokemon.national_pokedex_number, base_pokemon.name_en))
                
                # Mettre à jour dans la base de données
                session.add(pokemon)
        
        # Sauvegarder les modifications
        if fixed_pokemon:
            session.commit()
            
            # Afficher les corrections effectuées
            logger.info(f"Nombre de Pokémon corrigés: {len(fixed_pokemon)}")
            for pokemon_id, name, old_number, new_number, base_name in fixed_pokemon:
                logger.info(f"ID {pokemon_id} - {name}: {old_number} -> {new_number} (basé sur {base_name})")
        else:
            logger.info("Aucun Pokémon à corriger.")

# Exécution du script
if __name__ == "__main__":
    fix_pokedex_numbers() 