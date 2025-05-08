from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class PokemonStat(SQLModel, table=True):
    __tablename__ = "pokemon_stats"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    pokemon_name: str = Field(max_length=100)
    pokemon_id: int = Field(foreign_key="pokemon_details.id", index=True)
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    
    # Relationship can be added later
    # pokemon: "PokemonDetail" = Relationship(back_populates="stats") 