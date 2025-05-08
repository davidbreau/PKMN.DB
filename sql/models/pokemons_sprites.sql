-- Table des sprites de Pokémon
CREATE TABLE IF NOT EXISTS pokemon_sprites (
    pokemon_id SERIAL PRIMARY KEY,
    pokemon_name VARCHAR(100) NOT NULL,
    
    -- Sprites par défaut
    front_default TEXT,
    back_default TEXT,
    front_shiny TEXT,
    back_shiny TEXT,
    
    -- Sprites officiels
    official_artwork TEXT,
    official_artwork_shiny TEXT,
    
    -- Dream World
    dream_world TEXT,
    
    -- Home
    home_default TEXT,
    home_shiny TEXT,
    
    -- Pokémon GO (à remplir si disponible)
    pokemon_go TEXT,
    pokemon_go_shiny TEXT
    
);
