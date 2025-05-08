from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .pokemon import Pokemon
    from .type_effectiveness import TypeEffectiveness

class Type(SQLModel, table=True):
    __tablename__ = "types"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    name: str = Field(max_length=20, unique=True)
    name_fr: str | None = Field(default=None, max_length=20, unique=True)
    generation: int | None = None
    
    # RELATIONSHIPS
    # Relations avec Pokémon
    pokemons_primary: List["Pokemon"] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Type.id == Pokemon.type_1_id", "backref": "type_1"}
    )
    pokemons_secondary: List["Pokemon"] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Type.id == Pokemon.type_2_id", "backref": "type_2"}
    )
    
    # Relations avec TypeEffectiveness
    attacking_effectiveness: List["TypeEffectiveness"] = Relationship(
        back_populates="attacking_type", 
        sa_relationship_kwargs={"primaryjoin": "Type.id == TypeEffectiveness.attacking_type_id"}
    )
    defending_effectiveness: List["TypeEffectiveness"] = Relationship(
        back_populates="defending_type", 
        sa_relationship_kwargs={"primaryjoin": "Type.id == TypeEffectiveness.defending_type_id"}
    ) 