from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class Evolution(SQLModel, table=True):
    __tablename__ = "evolutions"
    
    id: int = Field(default=None, primary_key=True)
    evolution_chain_id: int
    pokemon_from_id: int
    pokemon_to_id: int
    trigger: Optional[str] = Field(default=None, max_length=50)
    
    # Relationships could be added later
    # pokemon_from: "PokemonDetails" = Relationship(back_populates="evolutions_from", foreign_key="pokemon_from_id")
    # pokemon_to: "PokemonDetails" = Relationship(back_populates="evolutions_to", foreign_key="pokemon_to_id") 