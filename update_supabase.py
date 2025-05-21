#!/usr/bin/env python3
"""
Script pour mettre à jour les mesures dans la table pokemon_details de Supabase
Division de height_m par 10 et multiplication de weight_kg par 10
"""

import os
import sys
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def update_pokemon_details():
    """
    Met à jour les colonnes height_m et weight_kg dans la table pokemon_details de Supabase
    - Divise height_m par 10
    - Multiplie weight_kg par 10
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("Les variables d'environnement SUPABASE_URL et SUPABASE_KEY sont requises")
        sys.exit(1)
    
    try:
        # Connexion à Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Connexion à Supabase établie")
        
        # 1. D'abord, récupérons tous les pokemon_details pour les traiter
        response = supabase.table("pokemon_details").select("*").execute()
        
        if not hasattr(response, 'data') or not response.data:
            logger.error("Aucune donnée trouvée dans la table pokemon_details")
            return
        
        logger.info(f"Nombre d'enregistrements trouvés: {len(response.data)}")
        
        # 2. Pour chaque enregistrement, mettre à jour height_m et weight_kg
        updated_count = 0
        for pokemon in response.data:
            pokemon_id = pokemon["pokemon_id"]
            old_height = pokemon.get("height_m")
            old_weight = pokemon.get("weight_kg")
            
            # Calculer les nouvelles valeurs
            new_height = old_height / 10 if old_height is not None else None
            new_weight = old_weight * 10 if old_weight is not None else None
            
            # Mettre à jour l'enregistrement dans Supabase
            update_response = supabase.table("pokemon_details").update({
                "height_m": new_height,
                "weight_kg": new_weight
            }).eq("pokemon_id", pokemon_id).execute()
            
            if hasattr(update_response, 'data') and update_response.data:
                updated_count += 1
                logger.info(f"Pokémon {pokemon_id} mis à jour: height {old_height} -> {new_height}, weight {old_weight} -> {new_weight}")
        
        logger.info(f"Mise à jour terminée. {updated_count} enregistrements mis à jour.")
    
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de Supabase: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Début de la mise à jour des mesures dans Supabase")
    update_pokemon_details()
    logger.info("Fin de la mise à jour des mesures dans Supabase") 