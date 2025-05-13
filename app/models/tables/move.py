from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .machine import Machine
    from .pokemon_learnset import PokemonLearnset

class Move(SQLModel, table=True):
    __tablename__ = "moves"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100, unique=True)
    name_fr: str | None = Field(default=None, max_length=100, unique=True)
    damage: int | None = None
    precision: int | None = None
    damage_class: str | None = Field(default=None, max_length=50)
    effect: str | None = Field(default=None, max_length=1000)
    effect_fr: str | None = Field(default=None, max_length=1000)
    generation: int | None = None
    
    # RELATIONSHIPS
    id___Machine__move_id: List["Machine"] = Relationship(
        back_populates="move_id___Move__id"
    )

    id___PokemonLearnset__move_id: List["PokemonLearnset"] = Relationship(
        back_populates="move_id___Move__id"
    )
