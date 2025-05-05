CREATE TABLE IF NOT EXISTS types_effectiveness (
    id SERIAL PRIMARY KEY,
    attacking_type VARCHAR(20) NOT NULL,
    defending_type VARCHAR(20) NOT NULL,
    effectiveness NUMERIC(2,1) NOT NULL
);
