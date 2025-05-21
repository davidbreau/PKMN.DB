import polars as pl
from pathlib import Path
from app.db.engine import engine
from sqlalchemy import text

def get_mega_evolution_data():
    """Extract mega evolution data pairs from the database"""
    query = text("""
    SELECT DISTINCT
        -- Base Pokemon data
        p1.id as base_pokemon_id,
        p1.name_en as base_name,
        s1.hp as base_hp,
        s1.attack as base_attack,
        s1.defense as base_defense,
        s1.special_attack as base_sp_attack,
        s1.special_defense as base_sp_defense,
        s1.speed as base_speed,
        t1.name as base_type_1,
        t2.name as base_type_2,
        pd1.is_legendary as base_is_legendary,
        pd1.is_mythical as base_is_mythical,
        pd1.height_m as base_height,
        pd1.weight_kg as base_weight,
        pd1.base_experience as base_experience,
        pd1.gender_rate as base_gender_rate,
        pd1.capture_rate as base_capture_rate,
        pd1.base_happiness as base_happiness,
        pd1.hatch_counter as base_hatch_counter,
        pd1.has_gender_differences as base_has_gender_differences,
        pd1.egg_group_1 as base_egg_group_1,
        pd1.egg_group_2 as base_egg_group_2,
        pd1.color as base_color,
        pd1.shape as base_shape,
        pd1.habitat as base_habitat,
        pd1.generation as base_generation,
        pd1.growth_rate as base_growth_rate,
        
        -- Mega evolution data
        p2.id as evolved_pokemon_id,
        p2.name_en as evolved_name,
        s2.hp as evolved_hp,
        s2.attack as evolved_attack,
        s2.defense as evolved_defense,
        s2.special_attack as evolved_sp_attack,
        s2.special_defense as evolved_sp_defense,
        s2.speed as evolved_speed,
        t3.name as evolved_type_1,
        t4.name as evolved_type_2,
        pd2.height_m as evolved_height,
        pd2.weight_kg as evolved_weight,
        pd2.base_experience as evolved_experience
    FROM pokemons p1
    JOIN pokemons p2 ON (
        p2.name_en LIKE 'Mega %'
        AND p2.name_en != 'Meganium'
        AND CASE 
            WHEN p2.name_en LIKE '% X' OR p2.name_en LIKE '% Y' 
            THEN p1.name_en = REPLACE(REPLACE(REPLACE(p2.name_en, 'Mega ', ''), ' X', ''), ' Y', '')
            ELSE p1.name_en = REPLACE(p2.name_en, 'Mega ', '')
        END
    )
    JOIN pokemon_stats s1 ON p1.id = s1.pokemon_id
    JOIN pokemon_stats s2 ON p2.id = s2.pokemon_id
    JOIN types t1 ON p1.type_1_id = t1.id
    LEFT JOIN types t2 ON p1.type_2_id = t2.id
    JOIN types t3 ON p2.type_1_id = t3.id
    LEFT JOIN types t4 ON p2.type_2_id = t4.id
    JOIN pokemon_details pd1 ON p1.id = pd1.pokemon_id
    JOIN pokemon_details pd2 ON p2.id = pd2.pokemon_id
    ORDER BY p1.name_en
    """)
    
    db_path = Path("../../../app/db")
    with engine.connect("V2_PKMN.db", folder=db_path) as session:
        result = session.execute(query)
        df = pl.from_records(result.fetchall(), schema=result.keys())
    
    output_dir = Path("../data")
    output_dir.mkdir(parents=True, exist_ok=True)
    df.write_csv(output_dir / "bronzemega_evolutions.csv")
    
    return df

if __name__ == "__main__":
    df = get_mega_evolution_data()
    print(f"Extracted {len(df)} mega evolution pairs") 