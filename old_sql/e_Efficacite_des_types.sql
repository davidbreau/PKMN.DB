CREATE TABLE IF NOT EXISTS Efficacite_des_types (
    type_offensif TEXT,
    type_deffensif TEXT,
    multiplicateur FLOAT,
    GO_multiplicateur FLOAT,
    FOREIGN KEY (type_offensif) REFERENCES Types(type_pkmn),
    FOREIGN KEY (type_deffensif) REFERENCES Types(type_pkmn)
);

-- TABLE D'ASSOCIATION
-- EFFICACITE DES TYPES // Type à Type