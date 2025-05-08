from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from models import Move, Game

class Machine(SQLModel, table=True):
    __tablename__ = "machines"
    
    # COLUMNS
    id: int = Field(default=None, primary_key=True)
    machine_number: str = Field(max_length=10)
    move_id: int = Field(foreign_key="moves.id")
    move_name: Optional[str] = Field(default=None, max_length=100)
    version_group: str = Field(max_length=50, index=True)
    
    # RELATIONSHIPS
    move: "Move" = Relationship(back_populates="machines")
    game: "Game" = Relationship(back_populates="machines", sa_relationship_kwargs={"primaryjoin": "Machine.version_group == Game.version_group"}) 