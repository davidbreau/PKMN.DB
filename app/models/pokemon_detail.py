from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class PokemonDetail(SQLModel, table=True):
    __tablename__ = "pokemon_details"
    
    id: int = Field(primary_key=True)
    species_id: int
    name_en: str = Field(max_length=100, unique=True)
    name_fr: Optional[str] = Field(default=None, max_length=100, unique=True)
    type_1_id: int
    type_1: str = Field(max_length=20)
    type_2_id: Optional[int] = None
    type_2: Optional[str] = Field(default=None, max_length=20)
    height_m: int
    weight_kg: int
    base_experience: Optional[int] = None
    order: Optional[int] = None
    is_default: bool
    is_legendary: bool = Field(default=False)
    is_mythical: bool = Field(default=False)
    is_baby: bool = Field(default=False)
    gender_rate: Optional[int] = None
    capture_rate: Optional[int] = None
    base_happiness: Optional[int] = None
    hatch_counter: Optional[int] = None
    has_gender_differences: Optional[bool] = Field(default=False)
    forms_switchable: Optional[bool] = Field(default=False)
    egg_group_1: Optional[str] = Field(default=None, max_length=20)
    egg_group_2: Optional[str] = Field(default=None, max_length=20)
    color: Optional[str] = Field(default=None, max_length=20)
    shape: Optional[str] = Field(default=None, max_length=20)
    evolves_from_species_id: Optional[int] = None
    evolution_chain_id: Optional[int] = None
    habitat: Optional[str] = Field(default=None, max_length=20)
    generation: Optional[str] = Field(default=None, max_length=20)
    growth_rate: Optional[str] = Field(default=None, max_length=20)
    
    # Relationships can be added later
    # pokedex_numbers: "PokedexNumber" = Relationship(back_populates="pokemon")
    # evolutions_from: List["Evolution"] = Relationship(back_populates="pokemon_from", sa_relationship_kwargs={"foreign_keys": "Evolution.pokemon_from_id"})
    # evolutions_to: List["Evolution"] = Relationship(back_populates="pokemon_to", sa_relationship_kwargs={"foreign_keys": "Evolution.pokemon_to_id"}) 