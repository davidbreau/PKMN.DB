from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from models import Pokemon

class Type(SQLModel, table=True):
    __tablename__ = "types"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    name: str = Field(max_length=20, unique=True)
    name_fr: str | None = Field(default=None, max_length=20, unique=True)
    generation: int | None = None
    
    # RELATIONSHIPS
    pokemons_primary: List["Pokemon"] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Type.id == Pokemon.type_1_id", "backref": "type_1"}
    )
    pokemons_secondary: List["Pokemon"] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Type.id == Pokemon.type_2_id", "backref": "type_2"}
    ) 