from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class PokemonSprite(SQLModel, table=True):
    __tablename__ = "pokemon_sprites"
    
    pokemon_id: int = Field(primary_key=True)
    pokemon_name: str = Field(max_length=100)
    
    # Sprites par défaut
    front_default: Optional[str] = None
    back_default: Optional[str] = None
    front_shiny: Optional[str] = None
    back_shiny: Optional[str] = None
    
    # Sprites officiels
    official_artwork: Optional[str] = None
    official_artwork_shiny: Optional[str] = None
    
    # Dream World
    dream_world: Optional[str] = None
    
    # Home
    home_default: Optional[str] = None
    home_shiny: Optional[str] = None
    
    # Pokémon GO
    pokemon_go: Optional[str] = None
    pokemon_go_shiny: Optional[str] = None
    
    # Relationship can be added later
    # pokemon: "PokemonDetail" = Relationship(back_populates="sprite") 