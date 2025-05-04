CREATE TABLE IF NOT EXISTS Evolutions (
    pre_evolution TEXT NOT NULL,
    evolution TEXT NOT NULL,
    niveau INTEGER NULL,
    condition TEXT NULL,
    objet TEXT NULL,
    GO_Bonbons TEXT NULL,
    GO_Condition TEXT NULL,
    FOREIGN KEY (pre_evolution) REFERENCES Pokemons(nom_pkmn),
    FOREIGN KEY (evolution) REFERENCES Pokemons(nom_pkmn)
);

-- TABLE D'ASSOCIATION
-- EVOLUTION // Pokemon - Pokemon 