from sqlalchemy import text
from app.db.engine import engine

# Requête pour lister toutes les tables
query = text("SELECT name FROM sqlite_master WHERE type='table';")

# Exécution de la requête
with engine.connect("V2_PKMN.db") as session:
    result = session.execute(query)
    tables = result.fetchall()

print("Tables disponibles dans V2_PKMN.db:")
for table in tables:
    print(f"- {table[0]}") 