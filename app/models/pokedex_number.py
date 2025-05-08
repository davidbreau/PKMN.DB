from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class PokedexNumber(SQLModel, table=True):
    __tablename__ = "pokedex_numbers"
    
    pokemon_id: int = Field(primary_key=True, foreign_key="pokemon_details.id")
    national: Optional[int] = None
    kanto: Optional[int] = None
    original_johto: Optional[int] = None
    updated_johto: Optional[int] = None
    hoenn: Optional[int] = None
    original_sinnoh: Optional[int] = None
    extended_sinnoh: Optional[int] = None
    unova_bw: Optional[int] = None
    unova_b2w2: Optional[int] = None
    kalos_central: Optional[int] = None
    kalos_coastal: Optional[int] = None
    kalos_mountain: Optional[int] = None
    alola: Optional[int] = None
    melemele: Optional[int] = None
    akala: Optional[int] = None
    ulaula: Optional[int] = None
    poni: Optional[int] = None
    galar: Optional[int] = None
    isle_of_armor: Optional[int] = None
    crown_tundra: Optional[int] = None
    hisui: Optional[int] = None
    paldea: Optional[int] = None
    
    # Relationship can be added later
    # pokemon: "PokemonDetails" = Relationship(back_populates="pokedex_number") 