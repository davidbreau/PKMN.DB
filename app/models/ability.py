from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from pokemon_ability import PokemonAbility

class Ability(SQLModel, table=True):
    __tablename__ = "abilities"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    name_en: str = Field(unique=True)
    name_fr: str | None = Field(default=None, unique=True)
    effect: str | None = Field(default=None, max_length=1000)
    effect_fr: str | None = Field(default=None, max_length=1000)
    generation: int | None = None
    
    # RELATIONSHIPS
    pokemon_abilities: List["PokemonAbility"] = Relationship(back_populates="ability") 