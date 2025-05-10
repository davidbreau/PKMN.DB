from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .pokemon import Pokemon

class PokemonStat(SQLModel, table=True):
    __tablename__ = "pokemon_stats"
    
    # COLUMNS
    id: int | None = Field(default=None, primary_key=True)
    pokemon_name: str = Field(max_length=100)
    pokemon_id: int = Field(foreign_key="pokemons.id", index=True)
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    
    # RELATIONSHIPS
    pokemon: "Pokemon" = Relationship(back_populates="stats") 