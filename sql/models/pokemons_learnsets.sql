CREATE TABLE IF NOT EXISTS pokemons_learnsets (
    pokemon_id INTEGER NOT NULL REFERENCES pokemons(id),
    move_id INTEGER NOT NULL REFERENCES moves(id),
    move_name VARCHAR(100) NOT NULL REFERENCES moves(name_en),
    method VARCHAR(100) NOT NULL,
    level INTEGER NULL,
    version_group VARCHAR(100) NOT NULL,
    PRIMARY KEY (pokemon_id, move_id)
);
