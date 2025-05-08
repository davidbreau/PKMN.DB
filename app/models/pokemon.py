from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from models import PokemonDetail, PokemonAbility, PokemonStat, PokemonSprite, PokemonLearnset, PokedexNumber, Evolution

class Pokemon(SQLModel, table=True):
    __tablename__ = "pokemons"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    national_pokedex_number: int
    name_en: str = Field(max_length=100, unique=True)
    name_fr: str | None = Field(default=None, max_length=100, unique=True)
    type_1_id: int
    type_2_id: int | None = None
    sprite_url: str | None = Field(default=None, max_length=255)
    cry_url: str | None = Field(default=None, max_length=255)
    
    # RELATIONSHIPS
    details: "PokemonDetail" = Relationship(back_populates="pokemon")
    abilities: List["PokemonAbility"] = Relationship(back_populates="pokemon")
    stats: "PokemonStat" = Relationship(back_populates="pokemon")
    sprites: "PokemonSprite" = Relationship(back_populates="pokemon")
    learnsets: List["PokemonLearnset"] = Relationship(back_populates="pokemon")
    pokedex_numbers: "PokedexNumber" = Relationship(back_populates="pokemon", sa_relationship_kwargs={"foreign_keys": "[PokedexNumber.pokemon_id]"})
    evolutions_from: List["Evolution"] = Relationship(back_populates="pokemon_from")
    evolutions_to: List["Evolution"] = Relationship(back_populates="pokemon_to")

