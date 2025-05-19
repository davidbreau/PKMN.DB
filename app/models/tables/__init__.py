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

# Pokemon GO models
from .GO_pokemon import GO_Pokemon
from .GO_pokemon_stats import GO_PokemonStats
from .GO_move import GO_Move
from .GO_pokemon_learnset import GO_PokemonLearnset

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
    'GO_PokemonLearnset'
] 