CREATE TABLE IF NOT EXISTS pokemons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,    -- Auto-incremented technical identifier for the database
    pokedex_no INTEGER NOT NULL,             -- National Pokedex number
    name_en VARCHAR(100) NOT NULL UNIQUE,
    name_fr VARCHAR(100) NULL UNIQUE,
    sort_order INTEGER,                      
    height_m FLOAT,
    weight_kg FLOAT,
    base_experience INTEGER,
    effort_point VARCHAR(15),
    is_default BOOLEAN
);

