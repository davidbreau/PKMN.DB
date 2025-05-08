from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class Pokemon(SQLModel, table=True):
    __tablename__ = "pokemons"
    
    id: int = Field(primary_key=True)
    national_pokedex_number: int
    name_en: str = Field(max_length=100, unique=True)
    name_fr: Optional[str] = Field(default=None, max_length=100, unique=True)
    type_1_id: int
    type_2_id: Optional[int] = None
    sprite_url: Optional[str] = Field(default=None, max_length=255)
    cry_url: Optional[str] = Field(default=None, max_length=255)
    
    # Relationships can be added later
    # details: "PokemonDetail" = Relationship(back_populates="pokemon")
    # abilities: List["PokemonAbility"] = Relationship(back_populates="pokemon")
    # stats: "PokemonStat" = Relationship(back_populates="pokemon")
    # sprites: "PokemonSprite" = Relationship(back_populates="pokemon")
    # learnsets: List["PokemonLearnset"] = Relationship(back_populates="pokemon") 