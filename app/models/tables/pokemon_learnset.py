from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .pokemon import Pokemon
    from .move import Move
    from .game import Game

class PokemonLearnset(SQLModel, table=True):
    __tablename__ = "pokemons_learnsets"
    
    # COLUMNS
    id: int | None = Field(default=None, primary_key=True)
    pokemon_id: int = Field(foreign_key="pokemons.id", index=True)
    move_id: int = Field(foreign_key="moves.id")
    move_name: str = Field(max_length=100)
    method: str = Field(max_length=100)
    level: int | None = None
    version_group: str = Field(foreign_key="games.version_group", max_length=100, index=True)
    
    # RELATIONSHIPS
    pokemon_id___Pokemon__id: "Pokemon" = Relationship(
        back_populates="id___PokemonLearnset__pokemon_id"
    )
    
    move_id___Move__id: "Move" = Relationship(
        back_populates="id___PokemonLearnset__move_id"
    )

    version_group___Game__version_group: "Game" = Relationship(
        back_populates="version_group___PokemonLearnset__version_group"
    )
