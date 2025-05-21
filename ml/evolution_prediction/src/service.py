import bentoml
import numpy as np
import json
import joblib
from pathlib import Path

# Chemin vers les modèles (même dossier)
MODEL_DIR = Path(__file__).parent / "models"

# Charger les configurations
with open(MODEL_DIR / "evolution_columns.json", "r") as f:
    columns_config = json.load(f)

# Charger les scalers et le modèle
model = joblib.load(MODEL_DIR / "evolution_model.joblib")
X_scaler = joblib.load(MODEL_DIR / "evolution_scaler_X.joblib")
y_scaler = joblib.load(MODEL_DIR / "evolution_scaler_y.joblib")

@bentoml.service(
    name="mega-evolution-predictor",
    traffic={"timeout": 60},
    resources={"cpu": 1, "memory": "512Mi"}
)
class PokemonEvolutionService:
    @bentoml.api
    def predict(self, pokemon_data: dict) -> dict:
        try:
            # Extraction des données d'entrée
            input_data = np.array([[
                pokemon_data["base_hp"],
                pokemon_data["base_attack"],
                pokemon_data["base_defense"],
                pokemon_data["base_sp_attack"],
                pokemon_data["base_sp_defense"],
                pokemon_data["base_speed"],
                pokemon_data["base_height"],
                pokemon_data["base_weight"],
                pokemon_data["base_experience"]
            ]])
            
            # Mise à l'échelle des données d'entrée
            input_scaled = X_scaler.transform(input_data)
            
            # Prédiction
            output_scaled = model.predict(input_scaled)
            
            # Inverse de la mise à l'échelle pour obtenir les valeurs réelles
            output = y_scaler.inverse_transform(output_scaled)
            output = output[0]  # Premier élément du batch
            
            # Création du dictionnaire de résultats
            result = {
                "evolved_attack": float(output[0]),
                "evolved_defense": float(output[1]),
                "evolved_sp_attack": float(output[2]),
                "evolved_sp_defense": float(output[3]),
                "evolved_speed": float(output[4]),
                "original_stats": {
                    "base_attack": float(pokemon_data["base_attack"]),
                    "base_defense": float(pokemon_data["base_defense"]),
                    "base_sp_attack": float(pokemon_data["base_sp_attack"]),
                    "base_sp_defense": float(pokemon_data["base_sp_defense"]),
                    "base_speed": float(pokemon_data["base_speed"])
                },
                "stat_increases": {
                    "attack_increase": float(output[0] - pokemon_data["base_attack"]),
                    "defense_increase": float(output[1] - pokemon_data["base_defense"]),
                    "sp_attack_increase": float(output[2] - pokemon_data["base_sp_attack"]),
                    "sp_defense_increase": float(output[3] - pokemon_data["base_sp_defense"]),
                    "speed_increase": float(output[4] - pokemon_data["base_speed"])
                },
                "percentage_increases": {
                    "attack_percent": float((output[0] / pokemon_data["base_attack"] - 1) * 100) if pokemon_data["base_attack"] > 0 else 0,
                    "defense_percent": float((output[1] / pokemon_data["base_defense"] - 1) * 100) if pokemon_data["base_defense"] > 0 else 0,
                    "sp_attack_percent": float((output[2] / pokemon_data["base_sp_attack"] - 1) * 100) if pokemon_data["base_sp_attack"] > 0 else 0,
                    "sp_defense_percent": float((output[3] / pokemon_data["base_sp_defense"] - 1) * 100) if pokemon_data["base_sp_defense"] > 0 else 0,
                    "speed_percent": float((output[4] / pokemon_data["base_speed"] - 1) * 100) if pokemon_data["base_speed"] > 0 else 0
                }
            }
            
            return result
        
        except Exception as e:
            return {"error": str(e)}