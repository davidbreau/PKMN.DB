CREATE TABLE IF NOT EXISTS Talents (
    talent TEXT PRIMARY KEY,
    generation INTEGER,
    effet TEXT,
    FOREIGN KEY (talent) REFERENCES Pokemons(talent_1),
    FOREIGN KEY (talent) REFERENCES Pokemons(talent_2),
    FOREIGN KEY (talent) REFERENCES Pokemons(talent_cache)
);

-- TALENT