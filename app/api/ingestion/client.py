import requests
from typing import Dict, Any

class PokeApiClient:
    """Client pour l'API PokeAPI."""
    
    BASE_URL = "https://pokeapi.co/api/v2"
    
    def __init__(self, cache_enabled: bool = True):
        """Initialise le client PokeAPI.
        
        Args:
            cache_enabled: Si True, active le cache des requêtes.
        """
        self.session = requests.Session()
        self.cache_enabled = cache_enabled
        self._cache = {} 