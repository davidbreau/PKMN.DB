CREATE TABLE IF NOT EXISTS Types (
    type_pkmn TEXT PRIMARY KEY,
    generation INTEGER,
    FOREIGN KEY (type_pkmn) REFERENCES Pokemons(type_1),
    FOREIGN KEY (type_pkmn) REFERENCES Pokemons(type_2),
    FOREIGN KEY (type_pkmn) REFERENCES Capacites(type_pkmn),
    FOREIGN KEY (type_pkmn) REFERENCES GO_Capacites(type_pkmn),
    FOREIGN KEY (type_pkmn) REFERENCES Efficacite_des_types(type_offensif),
    FOREIGN KEY (type_pkmn) REFERENCES Efficacite_des_types(type_deffensif)
);