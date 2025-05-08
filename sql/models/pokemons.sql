CREATE TABLE IF NOT EXISTS pokemons (
    id INTEGER PRIMARY KEY, 
    national_pokedex_number INTEGER NOT NULL,             -- National Pokedex number
    name_en VARCHAR(100) NOT NULL UNIQUE,
    name_fr VARCHAR(100) NULL UNIQUE,   
    type_1_id INTEGER NOT NULL,
    type_2_id INTEGER NULL,
    sprite_url VARCHAR(255) NULL,
    cry_url VARCHAR(255) NULL,
);

