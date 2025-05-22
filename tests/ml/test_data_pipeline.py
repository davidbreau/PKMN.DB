import pytest
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

def test_data_shape():
    """Test that the data has the expected shape and columns"""
    # Charger les données (ajustez le chemin selon votre structure)
    df = pd.read_csv("data/silver/evolution_stats.csv")
    
    # Vérifier les colonnes attendues
    expected_columns = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed',
                       'evolved_hp', 'evolved_attack', 'evolved_defense', 
                       'evolved_sp_attack', 'evolved_sp_defense']
    assert all(col in df.columns for col in expected_columns)
    
    # Vérifier qu'il n'y a pas de valeurs manquantes
    assert not df[expected_columns].isnull().any().any()

def test_scaling():
    """Test that the scaling works as expected"""
    X = np.array([[1, 2], [3, 4], [5, 6]])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Vérifier que la moyenne est proche de 0
    assert np.abs(X_scaled.mean()) < 1e-10
    
    # Vérifier que l'écart-type est proche de 1
    assert np.abs(X_scaled.std() - 1) < 1e-10

def test_prediction_range():
    """Test that model predictions are within expected ranges"""
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.multioutput import RegressorChain
    
    # Données de test simples
    X = np.random.rand(10, 6) * 100  # Stats de base entre 0 et 100
    y = np.random.rand(10, 5) * 150  # Stats évoluées entre 0 et 150
    
    # Entraîner un modèle simple
    model = RegressorChain(GradientBoostingRegressor(random_state=42))
    model.fit(X, y)
    
    # Faire des prédictions
    predictions = model.predict(X)
    
    # Vérifier que les prédictions sont dans des ranges raisonnables
    assert np.all(predictions >= 0)  # Pas de stats négatives
    assert np.all(predictions <= 255)  # Max possible pour les stats Pokémon 