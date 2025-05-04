CREATE TABLE IF NOT EXISTS GO_Capacites (
    capacite TEXT PRIMARY KEY,
    type_pkmn TEXT,
    categorie TEXT,
    raids_dommage INTEGER,
    raids_delai_recuperation FLOAT,
    raids_gain_energie INTEGER NULL,
    raids_temps_dommage FLOAT,
    pvp_dommage INTEGER,
    pvp_delai_recuperation INTEGER NULL,
    pvp_gain_energie INTEGER NULL,
    pvp_cout_energie INTEGER,
    stats_boost TEXT NULL,
    FOREIGN KEY (capacite) REFERENCES GO_Apprentissage(capacite),
    FOREIGN KEY (type_pkmn) REFERENCES Types(type_pkmn)
);

-- CAPACITE (Pokemon GO)