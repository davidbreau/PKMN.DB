from typing import List, TYPE_CHECKING, Optional
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .GO_pokemon_learnset import GO_PokemonLearnset
    from .GO_type import GO_Type

class GO_Move(SQLModel, table=True):
    __tablename__ = "go_moves"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True)
    original_move_id: int | None = Field(default=None, index=True)
    type_id: Optional[int] = Field(default=None, foreign_key="go_types.id")
    is_fast: bool
    is_charged: bool
    
    # Gym & Raid stats - modifiés en str pour accepter les formats comme "1.0s"
    damage: str | None = Field(default=None, max_length=20)
    energy: str | None = Field(default=None, max_length=20)
    duration: str | None = Field(default=None, max_length=20)
    
    # PVP stats - modifiés en str pour accepter les formats comme "1.0s"
    pvp_damage: str | None = Field(default=None, max_length=20)
    pvp_energy: str | None = Field(default=None, max_length=20)
    pvp_effects: str | None = Field(default=None, max_length=500)
    
    # RELATIONSHIPS
    id___GO_PokemonLearnset__move_id: List["GO_PokemonLearnset"] = Relationship(
        back_populates="move_id___GO_Move__id",
        sa_relationship_kwargs={"lazy": "joined"}
    )
    
    type_id___GO_Type__id: Optional["GO_Type"] = Relationship(
        back_populates="id___GO_Move__type_id",
        sa_relationship_kwargs={"lazy": "joined"}
    ) 