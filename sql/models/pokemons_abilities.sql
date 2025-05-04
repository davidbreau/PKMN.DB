CREATE TABLE IF NOT EXISTS pokemons_abilities (
    pokemon_id INTEGER NOT NULL REFERENCES pokemons(id),
    ability_id INTEGER NOT NULL REFERENCES abilities(id),
    ability_name VARCHAR(30) NOT NULL REFERENCES abilities(name),
    is_hidden BOOLEAN NOT NULL DEFAULT false,
    slot INTEGER NOT NULL,
    PRIMARY KEY (pokemon_id, slot)
);