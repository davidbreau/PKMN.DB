CREATE TABLE IF NOT EXISTS moves (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    name_fr VARCHAR(100) NULL UNIQUE,
    damage INTEGER NULL,
    precision integer NULL,
    effect VARCHAR(1000) NULL,
    effect_fr VARCHAR(1000) NULL,
    generation INTEGER
);
