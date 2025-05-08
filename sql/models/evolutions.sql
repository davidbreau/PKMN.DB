CREATE TABLE IF NOT EXISTS evolutions (
    id SERIAL PRIMARY KEY,
    evolution_chain_id INTEGER NOT NULL,
    pokemon_from_id INTEGER NOT NULL,
    pokemon_to_id INTEGER NOT NULL,
    trigger VARCHAR(50)
);