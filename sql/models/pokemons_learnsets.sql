CREATE TABLE IF NOT EXISTS pokemons_learnsets (
    pokemon_id INTEGER NOT NULL,
    move_id INTEGER NOT NULL,
    move_name VARCHAR(100) NOT NULL,
    method VARCHAR(100) NOT NULL,
    level INTEGER NULL,
    version_group VARCHAR(100) NOT NULL
);
