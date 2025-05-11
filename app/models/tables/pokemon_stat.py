from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
from .pokemon import Pokemon

class PokemonStat(SQLModel, table=True):
    __tablename__ = "pokemon_stats"
    
    # COLUMNS
    pokemon_id: int = Field(primary_key=True, foreign_key="pokemons.id")
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    
    # RELATIONSHIPS
    pokemon_id___Pokemon__id: "Pokemon" = Relationship(
        back_populates="id___PokemonStat__pokemon_id"
    )

    