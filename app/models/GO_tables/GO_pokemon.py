from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .GO_pokemon_stats import GO_PokemonStats
    from .GO_pokemon_learnset import GO_PokemonLearnset

class GO_Pokemon(SQLModel, table=True):
    __tablename__ = "go_pokemons"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100, index=True)
    pokedex_number: int | None = Field(default=None, index=True)
    released: bool = Field(default=True)
    buddy_distance: float | None = None
    
    # RELATIONSHIPS
    id___GO_PokemonStats__pokemon_id: "GO_PokemonStats" = Relationship(
        back_populates="pokemon_id___GO_Pokemon__id"
    )
    
    id___GO_PokemonLearnset__pokemon_id: List["GO_PokemonLearnset"] = Relationship(
        back_populates="pokemon_id___GO_Pokemon__id"
    ) 