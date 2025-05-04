CREATE TABLE IF NOT EXISTS Capacites (
    capacite TEXT PRIMARY KEY,
    type_pkmn TEXT,
    categorie TEXT,
    pp INTEGER,
    puissance INTEGER NULL,
    cible TEXT,
    taux_critique INTEGER NULL,
    priorite INTEGER,
    effet TEXT,
    FOREIGN KEY (capacite) REFERENCES Apprentissage(nom_pk),
    FOREIGN KEY (type_pkmn) REFERENCES Types(type_pkmn)
);