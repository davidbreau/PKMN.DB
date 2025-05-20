from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .GO_pokemon import GO_Pokemon

class GO_PokemonStats(SQLModel, table=True):
    __tablename__ = "go_pokemon_stats"
    
    # COLUMNS
    pokemon_id: int = Field(primary_key=True, foreign_key="go_pokemons.id")
    max_cp: int
    attack: int
    defense: int
    stamina: int
    
    # RELATIONSHIPS
    pokemon_id___GO_Pokemon__id: "GO_Pokemon" = Relationship(
        back_populates="id___GO_PokemonStats__pokemon_id"
    ) 