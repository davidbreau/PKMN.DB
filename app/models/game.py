from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from models import PokemonLearnset, Machine

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
    machines: List["Machine"] = Relationship(back_populates="game", sa_relationship_kwargs={"primaryjoin": "Game.version_group == Machine.version_group"})
    pokemon_learnsets: List["PokemonLearnset"] = Relationship(back_populates="game", sa_relationship_kwargs={"primaryjoin": "Game.version_group == PokemonLearnset.version_group"}) 