from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .pokemon import Pokemon

class PokedexNumber(SQLModel, table=True):
    __tablename__ = "pokedex_numbers"
    
    # COLUMNS
    pokemon_id: int = Field(primary_key=True, foreign_key="pokemons.id")
    national: int | None = None
    kanto: int | None = None
    original_johto: int | None = None
    updated_johto: int | None = None
    hoenn: int | None = None
    original_sinnoh: int | None = None
    extended_sinnoh: int | None = None
    unova_bw: int | None = None
    unova_b2w2: int | None = None
    kalos_central: int | None = None
    kalos_coastal: int | None = None
    kalos_mountain: int | None = None
    alola: int | None = None
    melemele: int | None = None
    akala: int | None = None
    ulaula: int | None = None
    poni: int | None = None
    galar: int | None = None
    isle_of_armor: int | None = None
    crown_tundra: int | None = None
    hisui: int | None = None
    paldea: int | None = None
    
    # RELATIONSHIPS
    pokemon_id___Pokemon__id: "Pokemon" = Relationship(
        back_populates="id___PokedexNumber__pokemon_id"
    )

    
 