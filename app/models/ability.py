from typing import Optional
from sqlmodel import Field, SQLModel

class Ability(SQLModel, table=True):
    __tablename__ = "abilities"
    
    id: int = Field(primary_key=True)
    name_en: str = Field(unique=True)
    name_fr: Optional[str] = Field(default=None, unique=True)
    effect: Optional[str] = Field(default=None, max_length=1000)
    effect_fr: Optional[str] = Field(default=None, max_length=1000)
    generation: Optional[int] = None 