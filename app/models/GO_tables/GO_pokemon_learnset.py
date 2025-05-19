from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .GO_pokemon import GO_Pokemon
    from .GO_move import GO_Move

class GO_PokemonLearnset(SQLModel, table=True):
    __tablename__ = "go_pokemon_learnsets"
    
    # COLUMNS
    id: int | None = Field(default=None, primary_key=True)
    pokemon_id: int = Field(foreign_key="go_pokemons.id", index=True)
    move_id: int = Field(foreign_key="go_moves.id", index=True)
    move_name: str = Field(max_length=100, index=True)
    original_move_id: int | None = Field(default=None, index=True)  # Pour joindre avec la base principale
    is_fast: bool
    is_charged: bool
    is_elite: bool = Field(default=False)
    
    # RELATIONSHIPS
    pokemon_id___GO_Pokemon__id: "GO_Pokemon" = Relationship(
        back_populates="id___GO_PokemonLearnset__pokemon_id"
    )
    
    move_id___GO_Move__id: "GO_Move" = Relationship(
        back_populates="id___GO_PokemonLearnset__move_id"
    ) 