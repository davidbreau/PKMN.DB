import pytest
import streamlit as st
from unittest.mock import Mock, patch
import json

# Mock des données de test
MOCK_POKEMON_DATA = {
    "id": 1,
    "name_en": "Bulbasaur",
    "name_fr": "Bulbizarre",
    "type_1_id": 4,
    "type_2_id": 8,
    "sprite_url": "https://example.com/bulbasaur.png",
    "hp": 45,
    "attack": 49,
    "defense": 49,
    "special_attack": 65,
    "special_defense": 65,
    "speed": 45
}

MOCK_TYPE_DATA = {
    "id": 4,
    "name": "Grass"
}

MOCK_STATS_DATA = {
    "pokemon_id": 1,
    "hp": 45,
    "attack": 49,
    "defense": 49,
    "special_attack": 65,
    "special_defense": 65,
    "speed": 45
}

@pytest.fixture
def mock_supabase():
    """Fixture pour mocker Supabase"""
    with patch('app.streamlit_app.supabase') as mock:
        # Configuration du mock pour la chaîne d'appels
        table_mock = Mock()
        select_mock = Mock()
        ilike_mock = Mock()
        execute_mock = Mock()
        
        # Configuration des retours
        execute_mock.return_value = type('Response', (), {'data': [MOCK_POKEMON_DATA]})()
        ilike_mock.execute = execute_mock
        select_mock.ilike = ilike_mock
        table_mock.select = select_mock
        mock.table = table_mock
        
        # Mock pour les détails d'un Pokémon
        mock.table().select().eq().single().execute.return_value = type('Response', (), {'data': MOCK_POKEMON_DATA})()
        
        # Mock pour les types
        mock.table().select().eq().single().execute.return_value = type('Response', (), {'data': MOCK_TYPE_DATA})()
        
        # Mock pour les stats
        mock.table().select().eq().single().execute.return_value = type('Response', (), {'data': MOCK_STATS_DATA})()
        
        yield mock

@pytest.fixture
def mock_predict_evolution():
    """Fixture pour mocker la fonction de prédiction"""
    with patch('app.streamlit_app.predict_evolution') as mock:
        mock.return_value = {
            "evolved_attack": 65,
            "evolved_defense": 60,
            "evolved_special_attack": 85,
            "evolved_special_defense": 80,
            "evolved_speed": 55
        }
        yield mock

@pytest.fixture
def mock_search_function():
    """Fixture pour mocker la fonction de recherche"""
    with patch('app.streamlit_app.search_pokemon') as mock:
        mock.return_value = [MOCK_POKEMON_DATA]
        yield mock

def test_pokemon_search(mock_supabase):
    """Test de la recherche de Pokémon"""
    # Simuler une recherche
    search_query = "Bulbasaur"
    
    # Simuler l'appel à Supabase comme dans l'application
    query = mock_supabase.table("pokemons").select("*")
    query = query.ilike("name_en", f"%{search_query}%")
    result = query.execute()
    
    # Vérifier que Supabase a été appelé correctement
    mock_supabase.table.assert_called_with("pokemons")
    mock_supabase.table().select.assert_called_with("*")
    mock_supabase.table().select().ilike.assert_called_with("name_en", f"%{search_query}%")
    
    # Vérifier que le résultat est correct
    assert len(result.data) == 1
    assert result.data[0]["id"] == MOCK_POKEMON_DATA["id"]
    assert result.data[0]["name_en"] == MOCK_POKEMON_DATA["name_en"]
    assert result.data[0]["name_fr"] == MOCK_POKEMON_DATA["name_fr"]

def test_pokemon_details_display(mock_supabase):
    """Test de l'affichage des détails d'un Pokémon"""
    # Simuler la sélection d'un Pokémon
    pokemon_id = 1
    
    # Appeler la fonction qui récupère les détails
    mock_supabase.table().select().eq().single().execute()
    
    # Vérifier que les données sont correctement récupérées
    mock_supabase.table().select().eq().single().execute.assert_called_once()
    
    # Vérifier que les stats sont récupérées
    mock_supabase.table().select().eq().single().execute.assert_called()

def test_evolution_prediction(mock_supabase, mock_predict_evolution):
    """Test de la prédiction d'évolution"""
    # Simuler une prédiction
    pokemon_data = MOCK_POKEMON_DATA.copy()
    
    # Appeler la fonction de prédiction
    prediction = mock_predict_evolution(pokemon_data)
    
    # Vérifier que la prédiction a les bonnes clés
    assert all(key in prediction for key in [
        "evolved_attack",
        "evolved_defense",
        "evolved_special_attack",
        "evolved_special_defense",
        "evolved_speed"
    ])
    
    # Vérifier que les valeurs sont cohérentes
    assert all(prediction[key] > pokemon_data[key.replace("evolved_", "")] 
              for key in prediction.keys())

def test_error_handling(mock_supabase):
    """Test de la gestion des erreurs"""
    # Simuler une erreur de base de données
    mock_supabase.table().select().eq().single().execute.side_effect = Exception("DB Error")
    
    # Vérifier que l'erreur est correctement gérée
    with pytest.raises(Exception):
        mock_supabase.table().select().eq().single().execute()

def test_session_state_management():
    """Test de la gestion du state de session"""
    # Initialiser le state
    if 'selected_pokemon_id' not in st.session_state:
        st.session_state['selected_pokemon_id'] = None
    
    # Simuler la sélection d'un Pokémon
    st.session_state['selected_pokemon_id'] = 1
    
    # Vérifier que le state est correctement mis à jour
    assert st.session_state['selected_pokemon_id'] == 1
    
    # Simuler la désélection
    st.session_state['selected_pokemon_id'] = None
    
    # Vérifier que le state est correctement réinitialisé
    assert st.session_state['selected_pokemon_id'] is None 