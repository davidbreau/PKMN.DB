from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .pokemon_detail import PokemonDetail
    from .pokemon_ability import PokemonAbility
    from .pokemon_stat import PokemonStat
    from .pokemon_sprite import PokemonSprite
    from .pokemon_learnset import PokemonLearnset
    from .pokedex_number import PokedexNumber
    from .evolution import Evolution
    from .type import Type

class Pokemon(SQLModel, table=True):
    __tablename__ = "pokemons"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    national_pokedex_number: int
    name_en: str = Field(max_length=100, unique=True)
    name_fr: str | None = Field(default=None, max_length=100)
    type_1_id: int = Field(foreign_key="types.id")
    type_2_id: int | None = Field(default=None, foreign_key="types.id")
    sprite_url: str | None = Field(default=None, max_length=255)
    cry_url: str | None = Field(default=None, max_length=255)
    
    # RELATIONSHIPS
    type_1_id___Type__id: "Type" = Relationship(
        back_populates="id___Pokemon__type_1_id",
        sa_relationship_kwargs={"foreign_keys": "[Pokemon.type_1_id]"}
    )
    type_2_id___Type__id: Optional["Type"] = Relationship(
        back_populates="id___Pokemon__type_2_id",
        sa_relationship_kwargs={"foreign_keys": "[Pokemon.type_2_id]"}
    )
    
    id___Evolution__pokemon_from_id: List["Evolution"] = Relationship(
        back_populates="pokemon_from_id___Pokemon__id",
        sa_relationship_kwargs={"foreign_keys": "[Evolution.pokemon_from_id]"}
    )
    id___Evolution__pokemon_to_id: List["Evolution"] = Relationship(
        back_populates="pokemon_to_id___Pokemon__id",
        sa_relationship_kwargs={"foreign_keys": "[Evolution.pokemon_to_id]"}
    )
    
    id___PokemonLearnset__pokemon_id: List["PokemonLearnset"] = Relationship(
        back_populates="pokemon_id___Pokemon__id"
    )
    
    id___PokedexNumber__pokemon_id: "PokedexNumber" = Relationship(
        back_populates="pokemon_id___Pokemon__id"
    )
    
    id___PokemonSprite__pokemon_id: "PokemonSprite" = Relationship(
        back_populates="pokemon_id___Pokemon__id"
    )
    
    id___PokemonStat__pokemon_id: "PokemonStat" = Relationship(
        back_populates="pokemon_id___Pokemon__id"
    )
    
    id___PokemonDetail__pokemon_id: "PokemonDetail" = Relationship(
        back_populates="pokemon_id___Pokemon__id"
    )
    
    id___PokemonAbility__pokemon_id: List["PokemonAbility"] = Relationship(
        back_populates="pokemon_id___Pokemon__id"
    )
