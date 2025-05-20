from .ability import Ability
from .evolution import Evolution
from .game import Game
from .machine import Machine
from .move import Move
from .pokedex_number import PokedexNumber
from .pokemon import Pokemon
from .pokemon_ability import PokemonAbility
from .pokemon_detail import PokemonDetail
from .pokemon_learnset import PokemonLearnset
from .pokemon_sprite import PokemonSprite
from .pokemon_stat import PokemonStat
from .type import Type
from .type_effectiveness import TypeEffectiveness

# Import Pokémon GO models
from app.models.GO_tables.GO_pokemon import GO_Pokemon
from app.models.GO_tables.GO_pokemon_stats import GO_PokemonStats
from app.models.GO_tables.GO_move import GO_Move
from app.models.GO_tables.GO_pokemon_learnset import GO_PokemonLearnset
from app.models.GO_tables.GO_type import GO_Type
from app.models.GO_tables.GO_type_effectiveness import GO_TypeEffectiveness

__all_tables__ = [
    'Ability',
    'Evolution',
    'Game',
    'Machine',
    'Move',
    'PokedexNumber',
    'Pokemon',
    'PokemonAbility',
    'PokemonDetail',
    'PokemonLearnset',
    'PokemonSprite',
    'PokemonStat',
    'Type',
    'TypeEffectiveness',
    # Pokemon GO tables
    'GO_Pokemon',
    'GO_PokemonStats',
    'GO_Move',
    'GO_PokemonLearnset',
    'GO_Type',
    'GO_TypeEffectiveness'
] 