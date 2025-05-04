-- Table pour les statistiques des pokémons
CREATE TABLE IF NOT EXISTS pokemon_stats (
    pokemon_name VARCHAR(100) NOT NULL REFERENCES pokemons(name),
    pokemon_id INTEGER NOT NULL REFERENCES pokemons(id),
    hp INTEGER NOT NULL,
    attack INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    special_attack INTEGER NOT NULL,
    special_defense INTEGER NOT NULL,
    speed INTEGER NOT NULL,
    PRIMARY KEY (pokemon_name),
    UNIQUE (pokemon_id)
);

  -- Chaque pokémon n'a qu'un seul ensemble de statistiques de base
  -- Cette table est liée à la table pokemons par la clé étrangère pokemon_id 