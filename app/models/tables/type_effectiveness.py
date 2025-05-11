from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Float

if TYPE_CHECKING:
from .type import Type

class TypeEffectiveness(SQLModel, table=True):
    __tablename__ = "types_effectiveness"
    
    # COLUMNS
    id: int | None = Field(default=None, primary_key=True)
    attacking_type_id: int = Field(foreign_key="types.id")
    defending_type_id: int = Field(foreign_key="types.id")
    effectiveness: float = Field(sa_type=Float(precision=2, asdecimal=False))
    
    # RELATIONSHIPS
    attacking_type_id___Type__id: "Type" = Relationship(
        back_populates="id___TypeEffectiveness__attacking_type_id",
        sa_relationship_kwargs={"foreign_keys": "[TypeEffectiveness.attacking_type_id]"}
    )
    defending_type_id___Type__id: "Type" = Relationship(
        back_populates="id___TypeEffectiveness__defending_type_id",
        sa_relationship_kwargs={"foreign_keys": "[TypeEffectiveness.defending_type_id]"}
    )
