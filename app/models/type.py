from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class Type(SQLModel, table=True):
    __tablename__ = "types"
    
    id: int = Field(primary_key=True)
    name: str = Field(max_length=20, unique=True)
    name_fr: Optional[str] = Field(default=None, max_length=20, unique=True)
    generation: Optional[int] = None
    
    # Relationships can be added later
    # pokemons_primary: List["Pokemon"] = Relationship(sa_relationship_kwargs={"primaryjoin": "Type.id == Pokemon.type_1_id", "backref": "type_1"})
    # pokemons_secondary: List["Pokemon"] = Relationship(sa_relationship_kwargs={"primaryjoin": "Type.id == Pokemon.type_2_id", "backref": "type_2"})
    # attacking_effectiveness: List["TypeEffectiveness"] = Relationship(sa_relationship_kwargs={"primaryjoin": "Type.name == TypeEffectiveness.attacking_type", "backref": "attacking_type_rel"})
    # defending_effectiveness: List["TypeEffectiveness"] = Relationship(sa_relationship_kwargs={"primaryjoin": "Type.name == TypeEffectiveness.defending_type", "backref": "defending_type_rel"}) 