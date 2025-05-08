from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class Game(SQLModel, table=True):
    __tablename__ = "games"
    
    id: int = Field(default=None, primary_key=True) 
    name: str = Field(max_length=50)
    generation_number: int
    generation_name: str = Field(max_length=50)
    version_group: str = Field(max_length=50)
    region_name: str = Field(max_length=50) 