from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .pokemon_ability import PokemonAbility

class Ability(SQLModel, table=True):
    __tablename__ = "abilities"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    name: str = Field(max_length=30, unique=True)
    name_fr: str | None = Field(default=None, max_length=30, unique=True)
    effect: str | None = Field(default=None, max_length=1000)
    effect_fr: str | None = Field(default=None, max_length=1000)
    generation: int | None = None
    
    # RELATIONSHIPS
    id___PokemonAbility__ability_id: List["PokemonAbility"] = Relationship(
        back_populates="ability_id___Ability__id",
        sa_relationship_kwargs={"foreign_keys": "[PokemonAbility.ability_id]"}
    )
    
    name___PokemonAbility__ability_name: List["PokemonAbility"] = Relationship(
        back_populates="ability_name___Ability__name",
        sa_relationship_kwargs={"foreign_keys": "[PokemonAbility.ability_name]"}
    )
