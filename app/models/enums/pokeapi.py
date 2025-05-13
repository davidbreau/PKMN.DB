from enum import Enum

class EndPoint(Enum):
    """Types de ressources disponibles dans l'API PokeAPI."""
    TYPE = "type"
    POKEMON = "pokemon"
    ABILITY = "ability" 
    MOVE = "move"
    ITEM = "item"
    GAME = "version" 