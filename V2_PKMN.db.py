from sqlmodel import SQLModel, Session, select, create_engine
from sqlalchemy import text
from app.db.engine import engine

# Requête SQL pour trouver les multiplicateurs d'efficacité pour le type "ground" contre "electric" et "flying"
query = text("""
SELECT 
    t_atk.name AS attacking_type,
    t_def.name AS defending_type,
    te.effectiveness
FROM 
    go_types_effectiveness te
JOIN
    types t_atk ON te.attacking_type_id = t_atk.id
JOIN
    types t_def ON te.defending_type_id = t_def.id
WHERE 
    LOWER(t_atk.name) = 'ground' AND
    (LOWER(t_def.name) = 'electric' OR LOWER(t_def.name) = 'flying')
""")

# Exécution de la requête
with engine.connect("V2_PKMN.db") as session:
    result = session.execute(query)
    type_effects = result.fetchall()

# Créer un dictionnaire pour stocker les effets
effectiveness_dict = {}
for attacking, defending, multiplier in type_effects:
    print(f"{attacking} contre {defending}: x{multiplier}")
    effectiveness_dict[(attacking, defending)] = multiplier

print("\nDictionnaire des multiplicateurs:")
for key, value in effectiveness_dict.items():
    print(f"{key}: {value}") 