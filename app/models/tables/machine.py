from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .move import Move
    from .game import Game

class Machine(SQLModel, table=True):
    __tablename__ = "machines"
    
    # COLUMNS
    id: int = Field(default=None, primary_key=True)
    machine_number: str = Field(max_length=10)
    move_id: int = Field(foreign_key="moves.id")
    move_name: str | None = Field(default=None, max_length=100)
    version_group: str = Field(max_length=50, foreign_key="games.version_group", index=True)
    
    # RELATIONSHIPS
    move_id___Move__id: "Move" = Relationship(
        back_populates="id___Machine__move_id"
    )
    version_group___Game__version_group: "Game" = Relationship(
        back_populates="version_group___Machine__version_group"
    )

 
 