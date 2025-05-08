from typing import Optional
from decimal import Decimal
from sqlmodel import Field, SQLModel, Relationship

class TypeEffectiveness(SQLModel, table=True):
    __tablename__ = "types_effectiveness"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    attacking_type: str = Field(max_length=20)
    defending_type: str = Field(max_length=20)
    effectiveness: float = Field()  # SQLModel utilise float pour NUMERIC
    
    # Une contrainte unique pourrait être ajoutée
    class Config:
        sa_column_kwargs = {
            "effectiveness": {"precision": 2, "scale": 1}
        } 