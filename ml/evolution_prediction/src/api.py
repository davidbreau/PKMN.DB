import os
import json
import numpy as np
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List
from pathlib import Path

# Chemin vers les modèles
MODEL_DIR = Path(__file__).parent.parent / "models"

# Charger les configurations
with open(MODEL_DIR / "evolution_columns.json", "r") as f:
    columns_config = json.load(f)

# Charger les scalers et le modèle
model = joblib.load(MODEL_DIR / "evolution_model.joblib")
X_scaler = joblib.load(MODEL_DIR / "evolution_scaler_X.joblib")
y_scaler = joblib.load(MODEL_DIR / "evolution_scaler_y.joblib")

input_cols = columns_config["input_cols"]
target_cols = columns_config["target_cols"]

# Modèle de données pour l'entrée de l'API
class PokemonStatsInput(BaseModel):
    base_hp: float = Field(..., description="Points de vie du Pokémon")
    base_attack: float = Field(..., description="Attaque du Pokémon")
    base_defense: float = Field(..., description="Défense du Pokémon")
    base_sp_attack: float = Field(..., description="Attaque spéciale du Pokémon")
    base_sp_defense: float = Field(..., description="Défense spéciale du Pokémon")
    base_speed: float = Field(..., description="Vitesse du Pokémon")
    base_height: float = Field(..., description="Taille du Pokémon en mètres")
    base_weight: float = Field(..., description="Poids du Pokémon en kg")
    base_experience: float = Field(..., description="Expérience de base du Pokémon")

# Modèle de données pour la sortie de l'API
class PokemonEvolutionPrediction(BaseModel):
    evolved_attack: float
    evolved_defense: float
    evolved_sp_attack: float
    evolved_sp_defense: float
    evolved_speed: float
    original_stats: Dict[str, float]
    stat_increases: Dict[str, float]
    percentage_increases: Dict[str, float]

# Création de l'application FastAPI
app = FastAPI(
    title="API de Prédiction d'Évolution Pokémon",
    description="Cette API prédit les statistiques d'un Pokémon après évolution basée sur un modèle d'apprentissage automatique",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Bienvenue dans l'API de Prédiction d'Évolution Pokémon"}

@app.post("/predict", response_model=PokemonEvolutionPrediction)
def predict_evolution(pokemon: PokemonStatsInput):
    try:
        # Conversion des données d'entrée en tableau numpy
        input_data = np.array([[
            pokemon.base_hp,
            pokemon.base_attack,
            pokemon.base_defense,
            pokemon.base_sp_attack,
            pokemon.base_sp_defense,
            pokemon.base_speed,
            pokemon.base_height,
            pokemon.base_weight,
            pokemon.base_experience
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
                "base_attack": float(pokemon.base_attack),
                "base_defense": float(pokemon.base_defense),
                "base_sp_attack": float(pokemon.base_sp_attack),
                "base_sp_defense": float(pokemon.base_sp_defense),
                "base_speed": float(pokemon.base_speed)
            },
            "stat_increases": {
                "attack_increase": float(output[0] - pokemon.base_attack),
                "defense_increase": float(output[1] - pokemon.base_defense),
                "sp_attack_increase": float(output[2] - pokemon.base_sp_attack),
                "sp_defense_increase": float(output[3] - pokemon.base_sp_defense),
                "speed_increase": float(output[4] - pokemon.base_speed)
            },
            "percentage_increases": {
                "attack_percent": float((output[0] / pokemon.base_attack - 1) * 100) if pokemon.base_attack > 0 else 0,
                "defense_percent": float((output[1] / pokemon.base_defense - 1) * 100) if pokemon.base_defense > 0 else 0,
                "sp_attack_percent": float((output[2] / pokemon.base_sp_attack - 1) * 100) if pokemon.base_sp_attack > 0 else 0,
                "sp_defense_percent": float((output[3] / pokemon.base_sp_defense - 1) * 100) if pokemon.base_sp_defense > 0 else 0,
                "speed_percent": float((output[4] / pokemon.base_speed - 1) * 100) if pokemon.base_speed > 0 else 0
            }
        }
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 