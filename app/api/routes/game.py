import logging
from litestar import get
from litestar.response import Response

from app.db.database import db

logger = logging.getLogger(__name__)

@get("/games")
async def get_games() -> Response:
    """Récupère la liste des jeux"""
    try:
        games = db.get_all_games()
        
        result = {
            "total": len(games),
            "games": []
        }
        
        for game in games:
            game_data = {
                "id": game["id"],
                "name": game["name"],
                "generation_number": game["generation_number"],
                "generation_name": game["generation_name"],
                "version_group": game["version_group"],
                "region_name": game["region_name"],
            }
            result["games"].append(game_data)
        
        return Response(result)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des jeux: {str(e)}")
        return Response(
            {"error": "Erreur lors de la récupération des jeux"},
            status_code=500,
        ) 