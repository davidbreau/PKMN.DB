from enum import Enum

class EndPoint(Enum):
    """Types de ressources disponibles dans l'API PokeAPI."""
    TYPE = "type"
    POKEMON = "pokemon"
    ABILITY = "ability" 
    MOVE = "move"
    ITEM = "item"
    GAME = "version" 
    EVOLUTION_CHAIN = "evolution-chain"
    POKEMON_SPECIES = "pokemon-species" 
    VERSION_GROUP = "version-group"
    GENERATION = "generation"
    REGION = "region"
    MACHINE = "machine"
    POKEMON_FORM = "pokemon-form" 