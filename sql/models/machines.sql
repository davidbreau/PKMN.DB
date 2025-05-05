-- Table des machines (TMs/HMs)
CREATE TABLE IF NOT EXISTS machines (
    id SERIAL PRIMARY KEY,
    machine_number VARCHAR(10) NOT NULL,   
    item_id INTEGER NOT NULL,               
    move_id INTEGER NOT NULL REFERENCES moves(id), 
    version_group VARCHAR(50) NOT NULL,      -
);


