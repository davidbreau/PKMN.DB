from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class Move(SQLModel, table=True):
    __tablename__ = "moves"
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100, unique=True)
    name_fr: Optional[str] = Field(default=None, max_length=100, unique=True)
    damage: Optional[int] = None
    precision: Optional[int] = None
    effect: Optional[str] = Field(default=None, max_length=1000)
    effect_fr: Optional[str] = Field(default=None, max_length=1000)
    generation: Optional[int] = None
    
    # Relationship can be added later
    # machines: List["Machine"] = Relationship(back_populates="move") 