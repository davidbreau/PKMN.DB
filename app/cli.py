#!/usr/bin/env python3
"""
PKMN.DB CLI - Interface en ligne de commande pour gérer la base de données Pokémon et l'API
"""

import argparse
import uvicorn
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_api(host="0.0.0.0", port=8000, reload=True):
    """Lance l'API Starlette"""
    logger.info(f"Démarrage de l'API sur {host}:{port}")
    uvicorn.run("app.api.main:app", host=host, port=port, reload=reload)


def main():
    """Point d'entrée principal du CLI"""
    parser = argparse.ArgumentParser(description="CLI pour PKMN.DB")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
    
    # Commande API
    api_parser = subparsers.add_parser("api", help="Gérer l'API")
    api_parser.add_argument("--host", type=str, default="0.0.0.0", help="Hôte de l'API (défaut: 0.0.0.0)")
    api_parser.add_argument("--port", type=int, default=8000, help="Port de l'API (défaut: 8000)")
    api_parser.add_argument("--no-reload", action="store_true", help="Désactiver le rechargement automatique")
    
    # Analyser les arguments
    args = parser.parse_args()
    
    # Si aucune commande n'est fournie, afficher l'aide
    if not args.command:
        parser.print_help()
        return
    
    # Exécuter la commande
    if args.command == "api":
        reload = not args.no_reload
        run_api(host=args.host, port=args.port, reload=reload)


if __name__ == "__main__":
    main() 