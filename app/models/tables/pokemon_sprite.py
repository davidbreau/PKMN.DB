from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
from .pokemon import Pokemon

class PokemonSprite(SQLModel, table=True):
    __tablename__ = "pokemon_sprites"
    
    # COLUMNS
    pokemon_id: int = Field(primary_key=True, foreign_key="pokemons.id")
    
    # Sprites par défaut
    front_default: str | None = None
    back_default: str | None = None
    front_shiny: str | None = None
    back_shiny: str | None = None
    
    # Sprites officiels
    official_artwork: str | None = None
    official_artwork_shiny: str | None = None
    
    # Dream World
    dream_world: str | None = None
    
    # Home
    home_default: str | None = None
    home_shiny: str | None = None
    
    # Pokémon GO
    pokemon_go: str | None = None
    pokemon_go_shiny: str | None = None
    
    # RELATIONSHIPS
    pokemon_id___Pokemon__id: "Pokemon" = Relationship(
        back_populates="id___PokemonSprite__pokemon_id"
    )
