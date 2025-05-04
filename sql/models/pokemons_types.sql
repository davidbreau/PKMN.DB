CREATE TABLE IF NOT EXISTS pokemons_types (
    pokemon_id INTEGER NOT NULL REFERENCES pokemons(id),
    pokemon_name VARCHAR(100) NOT NULL REFERENCES pokemons(name),
    type_id INTEGER NOT NULL REFERENCES types(id),
    slot INTEGER NOT NULL,
    PRIMARY KEY (pokemon_id, slot)
);
