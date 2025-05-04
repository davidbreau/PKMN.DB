CREATE TABLE IF NOT EXISTS GO_Apprentissages (
    nom_pkmn TEXT,
    capacite TEXT,
    elite BOOLEAN,
    FOREIGN KEY (nom_pkmn) REFERENCES Pokemons(nom_pkmn),
    FOREIGN KEY (capacite) REFERENCES Capacites(capacite)
);

-- TABLE D'ASSOCIATION
-- APPRENTISSAGE (Pokemon GO) // Pokemon - GO_Capacite