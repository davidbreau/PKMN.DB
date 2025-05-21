import logging
from typing import Optional, Dict, List, Any
from litestar import get
from litestar.response import Response

from app.db.database import db

logger = logging.getLogger(__name__)


@get("/pokemons")
async def get_pokemon_list(page: int = 1, limit: int = 20) -> Response:
    """Récupère la liste des pokémons avec pagination"""
    try:
        offset = (page - 1) * limit
        
        pokemons = db.get_all_pokemon(limit=limit, offset=offset)
        total = db.count_pokemon()
        
        result = {
            "total": total,
            "page": page,
            "limit": limit,
            "pokemons": []
        }
        
        for pokemon in pokemons:
            pokemon_data = {
                "id": pokemon["id"],
                "national_pokedex_number": pokemon["national_pokedex_number"],
                "name_en": pokemon["name_en"],
                "name_fr": pokemon["name_fr"],
                "type_1": {
                    "id": pokemon["type_1_id"],
                    "name": pokemon["type_1_name"],
                },
                "sprite_url": pokemon["sprite_url"],
            }
            
            if pokemon["type_2_id"]:
                pokemon_data["type_2"] = {
                    "id": pokemon["type_2_id"],
                    "name": pokemon["type_2_name"],
                }
            
            result["pokemons"].append(pokemon_data)
        
        return Response(result)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des pokémons: {str(e)}")
        return Response(
            {"error": "Erreur lors de la récupération des pokémons"},
            status_code=500,
        )


@get("/pokemons/{pokemon_id:int}")
async def get_pokemon_detail(pokemon_id: int) -> Response:
    """Récupère les détails d'un pokémon par son ID"""
    try:
        # Récupérer le pokémon
        pokemon = db.get_pokemon_by_id(pokemon_id)
        if not pokemon:
            return Response(
                {"error": f"Pokémon avec ID {pokemon_id} non trouvé"},
                status_code=404,
            )
        
        # Récupérer les détails
        details = db.get_pokemon_details(pokemon_id)
        
        # Récupérer les stats
        stats = db.get_pokemon_stats(pokemon_id)
        
        # Construire la réponse
        result = {
            "id": pokemon["id"],
            "national_pokedex_number": pokemon["national_pokedex_number"],
            "name_en": pokemon["name_en"],
            "name_fr": pokemon["name_fr"],
            "type_1": {
                "id": pokemon["type_1_id"],
                "name": pokemon["type_1_name"],
            },
            "sprite_url": pokemon["sprite_url"],
            "cry_url": pokemon["cry_url"],
        }
        
        if pokemon["type_2_id"]:
            result["type_2"] = {
                "id": pokemon["type_2_id"],
                "name": pokemon["type_2_name"],
            }
        
        # Ajouter les détails s'ils existent
        if details:
            result["height_m"] = details["height_m"]  # La conversion est déjà faite dans la base
            result["weight_kg"] = details["weight_kg"]  # La conversion est déjà faite dans la base
            result["base_experience"] = details["base_experience"]
            result["is_default"] = bool(details["is_default"])
            result["is_legendary"] = bool(details["is_legendary"])
            result["is_mythical"] = bool(details["is_mythical"])
            result["color"] = details["color"]
            result["shape"] = details["shape"]
            result["habitat"] = details["habitat"]
            result["generation"] = details["generation"]
        
        # Ajouter les stats si elles existent
        if stats:
            result["stats"] = {
                "hp": stats["hp"],
                "attack": stats["attack"],
                "defense": stats["defense"],
                "special_attack": stats["special_attack"],
                "special_defense": stats["special_defense"],
                "speed": stats["speed"],
            }
        
        return Response(result)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du pokémon {pokemon_id}: {str(e)}")
        return Response(
            {"error": "Erreur lors de la récupération du pokémon"},
            status_code=500,
        )


@get("/pokemons/{pokemon_id:int}/moves")
async def get_pokemon_moves(pokemon_id: int, game_version: Optional[str] = None) -> Response:
    """Récupère les attaques d'un pokémon par son ID avec filtres optionnels par jeu"""
    try:
        # Récupérer le pokémon pour vérifier qu'il existe
        pokemon = db.get_pokemon_by_id(pokemon_id)
        if not pokemon:
            return Response(
                {"error": f"Pokémon avec ID {pokemon_id} non trouvé"},
                status_code=404,
            )
        
        # Récupérer les attaques
        moves = db.get_pokemon_moves(pokemon_id, game_version)
        
        # Construire la réponse
        result = {
            "pokemon_id": pokemon["id"],
            "pokemon_name": pokemon["name_en"],
            "total_moves": len(moves),
            "moves": []
        }
        
        for move in moves:
            move_data = {
                "move": {
                    "id": move["move_id"],
                    "name": move["name"],
                    "name_fr": move["name_fr"],
                    "damage_class": move["damage_class"],
                    "damage": move["damage"],
                    "precision": move["precision"],
                    "effect": move["effect"],
                },
                "method": move["method"],
                "level": move["level"],
                "game": {
                    "name": move["game_name"],
                    "generation_number": move["generation_number"],
                    "version_group": move["version_group"],
                }
            }
            result["moves"].append(move_data)
        
        return Response(result)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des attaques du pokémon {pokemon_id}: {str(e)}")
        return Response(
            {"error": "Erreur lors de la récupération des attaques"},
            status_code=500,
        )


@get("/pokemons/{pokemon_id:int}/full")
async def get_pokemon_with_moves(pokemon_id: int, game_version: Optional[str] = None) -> Response:
    """Récupère les informations complètes d'un pokémon avec ses attaques par son ID"""
    try:
        # Récupérer le pokémon
        pokemon = db.get_pokemon_by_id(pokemon_id)
        if not pokemon:
            return Response(
                {"error": f"Pokémon avec ID {pokemon_id} non trouvé"},
                status_code=404,
            )
        
        # Récupérer les détails
        details = db.get_pokemon_details(pokemon_id)
        
        # Récupérer les stats
        stats = db.get_pokemon_stats(pokemon_id)
        
        # Récupérer les attaques
        moves = db.get_pokemon_moves(pokemon_id, game_version)
        
        # Construire la réponse
        result = {
            "id": pokemon["id"],
            "national_pokedex_number": pokemon["national_pokedex_number"],
            "name_en": pokemon["name_en"],
            "name_fr": pokemon["name_fr"],
            "type_1": {
                "id": pokemon["type_1_id"],
                "name": pokemon["type_1_name"],
            },
            "sprite_url": pokemon["sprite_url"],
            "cry_url": pokemon["cry_url"],
        }
        
        if pokemon["type_2_id"]:
            result["type_2"] = {
                "id": pokemon["type_2_id"],
                "name": pokemon["type_2_name"],
            }
        
        # Ajouter les détails s'ils existent
        if details:
            result["height_m"] = details["height_m"]  # La conversion est déjà faite dans la base
            result["weight_kg"] = details["weight_kg"]  # La conversion est déjà faite dans la base
            result["base_experience"] = details["base_experience"]
            result["is_default"] = bool(details["is_default"])
            result["is_legendary"] = bool(details["is_legendary"])
            result["is_mythical"] = bool(details["is_mythical"])
            result["color"] = details["color"]
            result["shape"] = details["shape"]
            result["habitat"] = details["habitat"]
            result["generation"] = details["generation"]
        
        # Ajouter les stats si elles existent
        if stats:
            result["stats"] = {
                "hp": stats["hp"],
                "attack": stats["attack"],
                "defense": stats["defense"],
                "special_attack": stats["special_attack"],
                "special_defense": stats["special_defense"],
                "speed": stats["speed"],
            }
        
        # Ajouter les attaques
        result["moves"] = []
        for move in moves:
            move_data = {
                "move": {
                    "id": move["move_id"],
                    "name": move["name"],
                    "name_fr": move["name_fr"],
                    "damage_class": move["damage_class"],
                    "damage": move["damage"],
                    "precision": move["precision"],
                    "effect": move["effect"],
                },
                "method": move["method"],
                "level": move["level"],
                "game": {
                    "name": move["game_name"],
                    "generation_number": move["generation_number"],
                    "version_group": move["version_group"],
                }
            }
            result["moves"].append(move_data)
        
        return Response(result)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations du pokémon {pokemon_id}: {str(e)}")
        return Response(
            {"error": "Erreur lors de la récupération des informations"},
            status_code=500,
        ) 