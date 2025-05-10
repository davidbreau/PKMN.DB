from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .pokemon import Pokemon
    from .ability import Ability

class PokemonAbility(SQLModel, table=True):
    __tablename__ = "pokemons_abilities"
    
    # COLUMNS
    pokemon_id: int = Field(foreign_key="pokemons.id", primary_key=True)
    ability_id: int = Field(foreign_key="abilities.id")
    ability_name: str = Field(max_length=30)
    is_hidden: bool = Field(default=False)
    slot: int = Field(primary_key=True)
    
    # RELATIONSHIPS
    pokemon: "Pokemon" = Relationship(back_populates="abilities")
    ability: "Ability" = Relationship(back_populates="pokemon_abilities") 