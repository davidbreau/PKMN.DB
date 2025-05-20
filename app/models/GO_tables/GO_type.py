from typing import List, Optional, TYPE_CHECKING, Dict, ClassVar
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .GO_pokemon import GO_Pokemon
    from .GO_type_effectiveness import GO_TypeEffectiveness
    from .GO_move import GO_Move

class GO_Type(SQLModel, table=True):
    __tablename__ = "go_types"
    
    # COLUMNS
    id: int = Field(primary_key=True)
    name: str = Field(max_length=20, unique=True)
    name_fr: str | None = Field(default=None, max_length=20, unique=True)
    weather_boost: str | None = Field(default=None, max_length=20)  # e.g., "Sunny", "Rain", etc.
    
    # RELATIONSHIPS
    id___GO_Move__type_id: List["GO_Move"] = Relationship(
        back_populates="type_id___GO_Type__id",
        sa_relationship_kwargs={"lazy": "joined"}
    )
    
    id___GO_TypeEffectiveness__attacking_type_id: List["GO_TypeEffectiveness"] = Relationship(
        back_populates="attacking_type_id___GO_Type__id",
        sa_relationship_kwargs={"foreign_keys": "[GO_TypeEffectiveness.attacking_type_id]", "lazy": "joined"}
    )
    
    id___GO_TypeEffectiveness__defending_type_id: List["GO_TypeEffectiveness"] = Relationship(
        back_populates="defending_type_id___GO_Type__id",
        sa_relationship_kwargs={"foreign_keys": "[GO_TypeEffectiveness.defending_type_id]", "lazy": "joined"}
    )

    # Static data for types
    TYPES_DATA: ClassVar[Dict[str, Dict]] = {
        "Normal": {"id": 1, "name_fr": "Normal", "weather_boost": "Partly cloudy"},
        "Fighting": {"id": 2, "name_fr": "Combat", "weather_boost": "Cloudy"},
        "Flying": {"id": 3, "name_fr": "Vol", "weather_boost": "Wind"},
        "Poison": {"id": 4, "name_fr": "Poison", "weather_boost": "Cloudy"},
        "Ground": {"id": 5, "name_fr": "Sol", "weather_boost": "Sunny"},
        "Rock": {"id": 6, "name_fr": "Roche", "weather_boost": "Partly cloudy"},
        "Bug": {"id": 7, "name_fr": "Insecte", "weather_boost": "Rain"},
        "Ghost": {"id": 8, "name_fr": "Spectre", "weather_boost": "Fog"},
        "Steel": {"id": 9, "name_fr": "Acier", "weather_boost": "Snow"},
        "Fire": {"id": 10, "name_fr": "Feu", "weather_boost": "Sunny"},
        "Water": {"id": 11, "name_fr": "Eau", "weather_boost": "Rain"},
        "Grass": {"id": 12, "name_fr": "Plante", "weather_boost": "Sunny"},
        "Electric": {"id": 13, "name_fr": "Électrik", "weather_boost": "Rain"},
        "Psychic": {"id": 14, "name_fr": "Psy", "weather_boost": "Wind"},
        "Ice": {"id": 15, "name_fr": "Glace", "weather_boost": "Snow"},
        "Dragon": {"id": 16, "name_fr": "Dragon", "weather_boost": "Wind"},
        "Dark": {"id": 17, "name_fr": "Ténèbres", "weather_boost": "Fog"},
        "Fairy": {"id": 18, "name_fr": "Fée", "weather_boost": "Cloudy"}
    }

    @classmethod
    def create_all_types(cls) -> List["GO_Type"]:
        """Crée et retourne une liste de toutes les instances de types."""
        return [
            cls(
                id=data["id"],
                name=name,
                name_fr=data["name_fr"],
                weather_boost=data["weather_boost"]
            )
            for name, data in cls.TYPES_DATA.items()
        ] 