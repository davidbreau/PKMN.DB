from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .evolution import Evolution
    from .pokemon import Pokemon

class PokemonDetail(SQLModel, table=True):
    __tablename__ = "pokemon_details"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    species_id: int
    name_en: str = Field(max_length=100, unique=True)
    name_fr: str | None = Field(default=None, max_length=100, unique=True)
    type_1_id: int
    type_1: str = Field(max_length=20)
    type_2_id: int | None = None
    type_2: str | None = Field(default=None, max_length=20)
    height_m: int
    weight_kg: int
    base_experience: int | None = None
    order: int | None = None
    is_default: bool
    is_legendary: bool = Field(default=False)
    is_mythical: bool = Field(default=False)
    is_baby: bool = Field(default=False)
    gender_rate: int | None = None
    capture_rate: int | None = None
    base_happiness: int | None = None
    hatch_counter: int | None = None
    has_gender_differences: bool | None = Field(default=False)
    forms_switchable: bool | None = Field(default=False)
    egg_group_1: str | None = Field(default=None, max_length=20)
    egg_group_2: str | None = Field(default=None, max_length=20)
    color: str | None = Field(default=None, max_length=20)
    shape: str | None = Field(default=None, max_length=20)
    evolves_from_species_id: int | None = None
    evolution_chain_id: int | None = None
    habitat: str | None = Field(default=None, max_length=20)
    generation: str | None = Field(default=None, max_length=20)
    growth_rate: str | None = Field(default=None, max_length=20)
    
    # RELATIONSHIPS
    pokemon: "Pokemon" = Relationship(back_populates="details")
    evolutions_from: List["Evolution"] = Relationship(back_populates="pokemon_from", sa_relationship_kwargs={"foreign_keys": "Evolution.pokemon_from_id"})
    evolutions_to: List["Evolution"] = Relationship(back_populates="pokemon_to", sa_relationship_kwargs={"foreign_keys": "Evolution.pokemon_to_id"}) 