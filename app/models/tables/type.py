from typing import List, Optional, TYPE_CHECKING
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
    id___Pokemon__type_1_id: List["Pokemon"] = Relationship(
        back_populates="type_1_id___Type__id",
        sa_relationship_kwargs={"foreign_keys": "[Pokemon.type_1_id]"}
    )
    id___Pokemon__type_2_id: Optional[List["Pokemon"]] = Relationship(
        back_populates="type_2_id___Type__id",
        sa_relationship_kwargs={"foreign_keys": "[Pokemon.type_2_id]"}
    )
    
    id___TypeEffectiveness__attacking_type_id: List["TypeEffectiveness"] = Relationship(
        back_populates="attacking_type_id___Type__id",
        sa_relationship_kwargs={"foreign_keys": "[TypeEffectiveness.attacking_type_id]"}
    )
    id___TypeEffectiveness__defending_type_id: List["TypeEffectiveness"] = Relationship(
        back_populates="defending_type_id___Type__id",
        sa_relationship_kwargs={"foreign_keys": "[TypeEffectiveness.defending_type_id]"}
    )
