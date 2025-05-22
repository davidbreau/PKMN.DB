import pytest
from playwright.sync_api import Page, expect
import time

def test_homepage_loads(page: Page):
    """Test que la page d'accueil se charge correctement"""
    page.goto("http://localhost:8501")
    
    # Vérifier le titre
    expect(page.locator("h1")).to_contain_text("Pokédex PKMN.DB")
    
    # Vérifier la barre de recherche
    expect(page.locator("input[placeholder='Rechercher par nom ou ID…']")).to_be_visible()

def test_pokemon_search(page: Page):
    """Test de la recherche de Pokémon"""
    page.goto("http://localhost:8501")
    
    # Rechercher un Pokémon
    search_input = page.locator("input[placeholder='Rechercher par nom ou ID…']")
    search_input.fill("Bulbasaur")
    search_input.press("Enter")
    
    # Attendre que les résultats se chargent
    time.sleep(2)  # Attendre le chargement des résultats
    
    # Vérifier que Bulbasaur est dans les résultats
    expect(page.locator("text=Bulbasaur")).to_be_visible()

def test_pokemon_details(page: Page):
    """Test de l'affichage des détails d'un Pokémon"""
    page.goto("http://localhost:8501")
    
    # Cliquer sur le premier Pokémon
    first_pokemon = page.locator(".pokemon-card").first
    first_pokemon.click()
    
    # Vérifier que les détails s'affichent
    expect(page.locator(".selected-pokemon")).to_be_visible()
    
    # Vérifier que les stats sont visibles
    expect(page.locator("text=Base Stats")).to_be_visible()

def test_evolution_prediction(page: Page):
    """Test de la prédiction d'évolution"""
    page.goto("http://localhost:8501")
    
    # Sélectionner un Pokémon
    first_pokemon = page.locator(".pokemon-card").first
    first_pokemon.click()
    
    # Cliquer sur le bouton PREDICT MEGA
    predict_button = page.locator("button:has-text('PREDICT MEGA')")
    predict_button.click()
    
    # Vérifier que les stats augmentées s'affichent
    expect(page.locator(".stat-increase")).to_be_visible()

def test_pagination(page: Page):
    """Test de la pagination"""
    page.goto("http://localhost:8501")
    
    # Vérifier que les boutons de pagination sont présents
    expect(page.locator("button:has-text('←')")).to_be_visible()
    expect(page.locator("button:has-text('→')")).to_be_visible()
    
    # Cliquer sur le bouton suivant
    next_button = page.locator("button:has-text('→')")
    next_button.click()
    
    # Vérifier que la page a changé
    time.sleep(1)  # Attendre le chargement
    expect(page.locator(".pokemon-card")).to_be_visible()

def test_responsive_design(page: Page):
    """Test du design responsive"""
    # Test sur mobile
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://localhost:8501")
    
    # Vérifier que la grille s'adapte
    expect(page.locator(".pokemon-grid")).to_be_visible()
    
    # Test sur tablette
    page.set_viewport_size({"width": 768, "height": 1024})
    page.goto("http://localhost:8501")
    
    # Vérifier que la grille s'adapte
    expect(page.locator(".pokemon-grid")).to_be_visible()

def test_error_handling(page: Page):
    """Test de la gestion des erreurs"""
    page.goto("http://localhost:8501")
    
    # Rechercher un Pokémon inexistant
    search_input = page.locator("input[placeholder='Rechercher par nom ou ID…']")
    search_input.fill("PokemonInexistant123")
    search_input.press("Enter")
    
    # Vérifier le message d'erreur
    expect(page.locator("text=Aucun Pokémon trouvé")).to_be_visible() 