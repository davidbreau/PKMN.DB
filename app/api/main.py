#!/usr/bin/env python3
"""
API Litestar pour PKMN.DB
Fournit des endpoints GET pour accéder aux données Pokémon
"""

import logging
from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from litestar.response import Response
from litestar.openapi import OpenAPIConfig
from litestar.static_files import StaticFilesConfig

from app.api.routes.pokemon import (
    get_pokemon_list,
    get_pokemon_detail,
    get_pokemon_moves,
    get_pokemon_with_moves
)
from app.api.routes.game import get_games
from app.api.routes.home import homepage

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration CORS
cors_config = CORSConfig(
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Configuration OpenAPI
openapi_config = OpenAPIConfig(
    title="PKMN.DB API",
    version="1.0.0",
    description="API pour accéder aux données Pokémon",
    use_handler_docstrings=True,
)

# Création de l'application
app = Litestar(
    route_handlers=[
        homepage,
        get_pokemon_list,
        get_pokemon_detail,
        get_pokemon_moves,
        get_pokemon_with_moves,
        get_games
    ],
    cors_config=cors_config,
    openapi_config=openapi_config,
    debug=True
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True) 