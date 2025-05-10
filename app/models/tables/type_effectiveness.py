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
    attacking_type: "Type" = Relationship(back_populates="attacking_effectiveness", sa_relationship_kwargs={"primaryjoin": "TypeEffectiveness.attacking_type_id == Type.id"})
    defending_type: "Type" = Relationship(back_populates="defending_effectiveness", sa_relationship_kwargs={"primaryjoin": "TypeEffectiveness.defending_type_id == Type.id"}) 