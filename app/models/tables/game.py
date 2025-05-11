from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .pokemon_learnset import PokemonLearnset
    from .machine import Machine

class Game(SQLModel, table=True):
    __tablename__ = "games"
    
    # COLUMNS
    id: int = Field(default=None, primary_key=True) 
    name: str = Field(max_length=50)
    generation_number: int
    generation_name: str = Field(max_length=50)
    version_group: str = Field(max_length=50, unique=True)
    region_name: str = Field(max_length=50)
    
    # RELATIONSHIPS
    version_group___Machine__version_group: List["Machine"] = Relationship(
        back_populates="version_group___Game__version_group"
    )

    version_group___PokemonLearnset__version_group: List["PokemonLearnset"] = Relationship(
        back_populates="version_group___Game__version_group"
    )
