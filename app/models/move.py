from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from models import Machine, PokemonLearnset

class Move(SQLModel, table=True):
    __tablename__ = "moves"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100, unique=True)
    name_fr: str | None = Field(default=None, max_length=100, unique=True)
    damage: int | None = None
    precision: int | None = None
    effect: str | None = Field(default=None, max_length=1000)
    effect_fr: str | None = Field(default=None, max_length=1000)
    generation: int | None = None
    
    # RELATIONSHIPS
    machines: List["Machine"] = Relationship(back_populates="move")
    learnsets: List["PokemonLearnset"] = Relationship(back_populates="move") 