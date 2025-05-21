import polars as pl
from pathlib import Path
from app.db.engine import engine
from sqlalchemy import text

def get_mega_evolution_data():
    """
    Extraire les données des méga-évolutions des Pokémon depuis la base V2.
    Retourne un DataFrame contenant toutes les informations sur les paires de méga-évolutions
    """
    print("Démarrage de l'extraction des données...")
    
    # Requête pour obtenir les paires de méga-évolution avec leurs stats et caractéristiques
    query = text("""
    WITH mega_pokemon AS (
        -- Trouver d'abord tous les Pokémon Mega
        SELECT 
            id,
            name_en,
            -- Extraire le nom de base en enlevant "Mega " du début
            REPLACE(name_en, 'Mega ', '') as base_form_name
        FROM pokemons
        WHERE name_en LIKE 'Mega %'
        AND name_en != 'Meganium'
    )
    SELECT DISTINCT
        p1.id as base_pokemon_id,
        p1.name_en as base_name,
        -- Stats de base
        s1.hp as base_hp,
        s1.attack as base_attack,
        s1.defense as base_defense,
        s1.special_attack as base_sp_attack,
        s1.special_defense as base_sp_defense,
        s1.speed as base_speed,
        -- Types et catégories de base
        t1.name as base_type_1,
        t2.name as base_type_2,
        pd1.is_legendary as base_is_legendary,
        pd1.is_mythical as base_is_mythical,
        -- ID et nom de la méga-évolution
        mp.id as evolved_pokemon_id,
        mp.name_en as evolved_name,
        -- Types de la méga-évolution
        t3.name as evolved_type_1,
        t4.name as evolved_type_2,
        -- Stats de la méga-évolution
        s2.hp as evolved_hp,
        s2.attack as evolved_attack,
        s2.defense as evolved_defense,
        s2.special_attack as evolved_sp_attack,
        s2.special_defense as evolved_sp_defense,
        s2.speed as evolved_speed
    FROM mega_pokemon mp
    -- Trouver le Pokémon de base correspondant
    JOIN pokemons p1 ON (
        -- Cas spéciaux pour Charizard X/Y et Mewtwo X/Y
        CASE 
            WHEN mp.name_en LIKE '% X' OR mp.name_en LIKE '% Y' 
            THEN p1.name_en = REPLACE(REPLACE(mp.base_form_name, ' X', ''), ' Y', '')
            ELSE p1.name_en = mp.base_form_name
        END
    )
    -- Jointures pour les stats
    JOIN pokemon_stats s1 ON p1.id = s1.pokemon_id
    JOIN pokemon_stats s2 ON mp.id = s2.pokemon_id
    -- Jointures pour les types du Pokémon de base
    JOIN types t1 ON p1.type_1_id = t1.id
    LEFT JOIN types t2 ON p1.type_2_id = t2.id
    -- Jointure pour les détails du Pokémon de base
    JOIN pokemon_details pd1 ON p1.id = pd1.pokemon_id
    -- Jointures pour les types de la méga-évolution
    JOIN types t3 ON (SELECT type_1_id FROM pokemons WHERE id = mp.id) = t3.id
    LEFT JOIN types t4 ON (SELECT type_2_id FROM pokemons WHERE id = mp.id) = t4.id
    ORDER BY p1.name_en  -- Trier par nom pour faciliter la vérification
    """)
    
    print("Connexion à la base de données...")
    # Utiliser le context manager pour la connexion
    db_path = Path("../../../app/db")
    print(f"Chemin de la base de données: {db_path.resolve()}")
    
    with engine.connect("V2_PKMN.db", folder=db_path) as session:
        print("Exécution de la requête...")
        # Exécuter la requête et convertir en DataFrame Polars
        result = session.execute(query)
        print("Conversion en DataFrame...")
        df = pl.from_records(result.fetchall(), schema=result.keys())
        print(f"Nombre de lignes trouvées: {len(df)}")

    # Sauvegarder le DataFrame complet
    output_dir = Path("../data")
    output_dir.mkdir(parents=True, exist_ok=True)
    df.write_csv(output_dir / "mega_evolutions.csv")
    print(f"\nDataset sauvegardé dans : {output_dir / 'mega_evolutions.csv'}")
    
    return df

if __name__ == "__main__":
    # Test de l'extraction
    df = get_mega_evolution_data()
    
    print("\nAperçu des données :")
    print(df.head())
    
    # Calculer les changements de stats
    stat_changes = pl.DataFrame({
        'name': df['base_name'],
        'hp_change': df['evolved_hp'] - df['base_hp'],
        'atk_change': df['evolved_attack'] - df['base_attack'],
        'def_change': df['evolved_defense'] - df['base_defense'],
        'sp_atk_change': df['evolved_sp_attack'] - df['base_sp_attack'],
        'sp_def_change': df['evolved_sp_defense'] - df['base_sp_defense'],
        'speed_change': df['evolved_speed'] - df['base_speed']
    })
    
    print("\nMoyenne des changements de stats après méga-évolution :")
    print(stat_changes.select(pl.exclude('name')).mean())
    
    print("\nTop 5 des plus grandes augmentations de stats :")
    for stat in ['atk_change', 'def_change', 'sp_atk_change', 'sp_def_change', 'speed_change']:
        temp_df = stat_changes.select(['name', stat]).sort(stat, descending=True).head(5)
        print(f"\nTop 5 {stat}:")
        for row in temp_df.iter_rows():
            print(f"{row[0]}: +{row[1]}")
    
    # Analyse des changements de types
    print("\nPokémon qui changent de type lors de la méga-évolution :")
    type_changes = df.with_columns([
        pl.concat_str([pl.col('base_type_1'), pl.col('base_type_2')], separator='/').alias('base_type'),
        pl.concat_str([pl.col('evolved_type_1'), pl.col('evolved_type_2')], separator='/').alias('mega_type')
    ]).filter(
        pl.col('base_type') != pl.col('mega_type')
    ).select(['base_name', 'base_type', 'mega_type'])
    
    if len(type_changes) > 0:
        for row in type_changes.iter_rows():
            print(f"{row[0]}: {row[1]} → {row[2]}") 