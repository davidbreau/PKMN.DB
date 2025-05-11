from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .pokemon import Pokemon

class Evolution(SQLModel, table=True):
    __tablename__ = "evolutions"
    
    # COLUMNS
    id: int = Field(default=None, primary_key=True)
    evolution_chain_id: int
    pokemon_from_id: int = Field(foreign_key="pokemons.id")
    pokemon_to_id: int = Field(foreign_key="pokemons.id")
    trigger: str | None = Field(default=None, max_length=50)
    
    # RELATIONSHIPS
    pokemon_from_id___Pokemon__id: List["Pokemon"] = Relationship(
        back_populates="id___Evolution__pokemon_from_id",
        sa_relationship_kwargs={"foreign_keys": "[Evolution.pokemon_from_id]"}
    )
    pokemon_to_id___Pokemon__id: List["Pokemon"] = Relationship(
        back_populates="id___Evolution__pokemon_to_id",
        sa_relationship_kwargs={"foreign_keys": "[Evolution.pokemon_to_id]"}
    ) 