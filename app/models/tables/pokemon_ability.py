from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .pokemon import Pokemon
    from .ability import Ability

class PokemonAbility(SQLModel, table=True):
    __tablename__ = "pokemon_abilities"
    
    # COLUMNS
    pokemon_id: int = Field(foreign_key="pokemons.id", primary_key=True)
    ability_id: int = Field(foreign_key="abilities.id")
    ability_name: str = Field(foreign_key="abilities.name", max_length=30)
    is_hidden: bool = Field(default=False)
    slot: int = Field(primary_key=True)
    
    # RELATIONSHIPS
    pokemon_id___Pokemon__id: "Pokemon" = Relationship(
        back_populates="id___PokemonAbility__pokemon_id"
    )
    ability_id___Ability__id: "Ability" = Relationship(
        back_populates="id___PokemonAbility__ability_id",
        sa_relationship_kwargs={"foreign_keys": "[PokemonAbility.ability_id]"}
    )
    ability_name___Ability__name: "Ability" = Relationship(
        back_populates="name___PokemonAbility__ability_name",
        sa_relationship_kwargs={"foreign_keys": "[PokemonAbility.ability_name]"}
    )
 