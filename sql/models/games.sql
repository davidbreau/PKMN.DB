CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    generation_number INTEGER NOT NULL,
    generation_name VARCHAR(50) NOT NULL,
    version_group VARCHAR(50) NOT NULL,
    region_name VARCHAR(50) NOT NULL
);
 