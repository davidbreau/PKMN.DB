-- Mettre à jour les mesures dans la table pokemon_details de Supabase
-- Division de height_m par 10 et multiplication de weight_kg par 10

UPDATE pokemon_details 
SET 
    height_m = height_m / 10,
    weight_kg = weight_kg * 10
WHERE 
    height_m IS NOT NULL OR weight_kg IS NOT NULL;

-- Pour vérifier combien de lignes ont été modifiées
-- Pour PostgreSQL, utiliser GET DIAGNOSTICS au lieu de changes()
-- GET DIAGNOSTICS rows_affected = ROW_COUNT;
-- Cette commande doit être utilisée dans une fonction ou une procédure stockée

-- Alternative: vérifier un échantillon de données mises à jour 
SELECT pokemon_id, height_m, weight_kg FROM pokemon_details LIMIT 5; 