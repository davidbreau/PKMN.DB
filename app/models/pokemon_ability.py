from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class PokemonAbility(SQLModel, table=True):
    __tablename__ = "pokemons_abilities"
    
    pokemon_id: int = Field(foreign_key="pokemons.id", primary_key=True)
    ability_id: int = Field(foreign_key="abilities.id")
    ability_name: str = Field(max_length=30, foreign_key="abilities.name")
    is_hidden: bool = Field(default=False)
    slot: int = Field(primary_key=True)
    
    # Relationships can be added later
    # pokemon: "Pokemon" = Relationship(back_populates="abilities")
    # ability: "Ability" = Relationship(back_populates="pokemons") 