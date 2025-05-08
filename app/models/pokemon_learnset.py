from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from models import Pokemon, Move, Game

class PokemonLearnset(SQLModel, table=True):
    __tablename__ = "pokemons_learnsets"
    
    # COLUMNS
    id: int | None = Field(default=None, primary_key=True)
    pokemon_id: int = Field(foreign_key="pokemons.id", index=True)
    move_id: int = Field(foreign_key="moves.id")
    move_name: str = Field(max_length=100)
    method: str = Field(max_length=100)
    level: int | None = None
    version_group: str = Field(max_length=100, index=True)
    
    # RELATIONSHIPS
    pokemon: "Pokemon" = Relationship(back_populates="learnsets")
    move: "Move" = Relationship(back_populates="learnsets")
    game: "Game" = Relationship(back_populates="pokemon_learnsets", sa_relationship_kwargs={"primaryjoin": "PokemonLearnset.version_group == Game.version_group"}) 