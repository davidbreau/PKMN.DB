CREATE TABLE IF NOT EXISTS Apprentissages (
    nom_pkmn TEXT,
    capacite TEXT,
    generation INTEGER,
    ct INTEGER NULL,
    dt INTEGER NULL,
    reproduction BOOLEAN,
    FOREIGN KEY (nom_pkmn) REFERENCES Pokemons(nom_pkmn),
    FOREIGN KEY (capacite) REFERENCES Capacites(capacite)
);

-- TABLE D'ASSOCIATION
-- APPRENTISSAGE // Pokemon - Capacite