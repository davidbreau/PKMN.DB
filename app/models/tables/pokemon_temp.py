from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

class PokemonTemp(SQLModel, table=True):
    __tablename__ = "pokemons_temp"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    national_pokedex_number: int
    name_en: str = Field(max_length=100, unique=True)
    name_fr: str | None = Field(default=None, max_length=100)  # Sans contrainte d'unicité
    type_1_id: int = Field(foreign_key="types.id")
    type_2_id: int | None = Field(default=None, foreign_key="types.id")
    sprite_url: str | None = Field(default=None, max_length=255)
    cry_url: str | None = Field(default=None, max_length=255) 