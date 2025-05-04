-- Table des évolutions
CREATE TABLE IF NOT EXISTS evolutions (
    id SERIAL PRIMARY KEY,
    evolution_chain_id INTEGER NOT NULL,  -- ID de la chaîne d'évolution dans l'API
    pokemon_from_id INTEGER NOT NULL REFERENCES pokemons(id),  -- Pokémon de base
    pokemon_to_id INTEGER NOT NULL REFERENCES pokemons(id),    -- Pokémon évolué
    
    trigger VARCHAR(50),             -- level-up, trade, use-item, etc.

  -- Cette table capture les relations directes d'évolution
  -- Par exemple: Bulbasaur → Ivysaur → Venusaur sera stocké comme deux enregistrements:
  -- 1. Bulbasaur → Ivysaur
  -- 2. Ivysaur → Venusaur
