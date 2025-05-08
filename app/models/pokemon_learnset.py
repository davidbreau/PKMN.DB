from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class PokemonLearnset(SQLModel, table=True):
    __tablename__ = "pokemons_learnsets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    pokemon_id: int = Field(foreign_key="pokemon_details.id", index=True)
    move_id: int = Field(foreign_key="moves.id")
    move_name: str = Field(max_length=100)
    method: str = Field(max_length=100)
    level: Optional[int] = None
    version_group: str = Field(max_length=100)
    
    # Relationships can be added later
    # pokemon: "PokemonDetail" = Relationship(back_populates="learnsets")
    # move: "Move" = Relationship(back_populates="learnsets") 