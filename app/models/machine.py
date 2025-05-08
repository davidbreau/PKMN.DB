from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class Machine(SQLModel, table=True):
    __tablename__ = "machines"
    
    id: int = Field(default=None, primary_key=True)
    machine_number: str = Field(max_length=10)
    move_id: int = Field(foreign_key="moves.id")
    move_name: Optional[str] = Field(default=None, max_length=100)
    version_group: str = Field(max_length=50)
    
    # Relationship can be added later
    # move: "Move" = Relationship(back_populates="machines") 