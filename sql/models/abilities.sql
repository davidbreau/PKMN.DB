CREATE TABLE IF NOT EXISTS abilities (
    id INTEGER PRIMARY KEY,
    name_en VARCHAR(100) NOT NULL UNIQUE,
    name_fr VARCHAR(100) NULL UNIQUE,
    effect VARCHAR(1000) NULL,
    effect_fr VARCHAR(1000) NULL,
    generation INTEGER
);
