import pytest
from playwright.sync_api import Page, expect
import os
import time

# URL de l'application déployée sur Streamlit Cloud
APP_URL = "https://pkmndb.streamlit.app"  # Remplacez par votre URL

@pytest.fixture(scope="function")
def setup_page(page: Page):
    # Ouvrir l'URL et attendre que la page soit chargée
    page.goto(APP_URL)
    # Attendre que le titre de la page soit chargé
    page.wait_for_selector("h1:has-text('Pokédex PKMN.DB')")
    return page

def test_app_loads(setup_page):
    """Vérifier que l'application se charge correctement"""
    page = setup_page
    # Vérifier que le titre est présent
    expect(page.locator("h1:has-text('Pokédex PKMN.DB')")).to_be_visible()
    # Vérifier que la barre de recherche est présente
    expect(page.locator("input[placeholder*='Rechercher']")).to_be_visible()

def test_search_pokemon(setup_page):
    """Tester la recherche de Pokémon"""
    page = setup_page
    # Entrer "Pikachu" dans la barre de recherche
    page.fill("input[placeholder*='Rechercher']", "Pikachu")
    # Appuyer sur Entrée
    page.press("input[placeholder*='Rechercher']", "Enter")
    # Attendre que les résultats s'affichent (Pikachu devrait être #025)
    page.wait_for_selector("span.pokemon-number:has-text('#025')")
    # Vérifier que Pikachu est affiché
    expect(page.locator("span.pokemon-name:has-text('Pikachu')")).to_be_visible()

def test_show_pokemon_details(setup_page):
    """Tester l'affichage des détails d'un Pokémon"""
    page = setup_page
    # Rechercher un Pokémon spécifique
    page.fill("input[placeholder*='Rechercher']", "Bulbasaur")
    page.press("input[placeholder*='Rechercher']", "Enter")
    # Attendre que les résultats s'affichent
    page.wait_for_selector("span.pokemon-name:has-text('Bulbasaur')")
    # Cliquer sur le bouton "Show Details"
    page.click("button:has-text('Show Details')")
    # Attendre que les détails s'affichent
    page.wait_for_selector("h3:has-text('Base Stats')")
    # Vérifier que les types sont affichés
    expect(page.locator("span.type-badge:has-text('Grass')")).to_be_visible()
    expect(page.locator("span.type-badge:has-text('Poison')")).to_be_visible()

def test_predict_mega_evolution(setup_page):
    """Tester la fonctionnalité PREDICT MEGA"""
    page = setup_page
    # Rechercher un Pokémon qui peut avoir une méga-évolution
    page.fill("input[placeholder*='Rechercher']", "Charizard")
    page.press("input[placeholder*='Rechercher']", "Enter")
    # Attendre que les résultats s'affichent
    page.wait_for_selector("span.pokemon-name:has-text('Charizard')")
    # Cliquer sur le bouton "Show Details"
    page.click("button:has-text('Show Details')")
    # Attendre que les détails s'affichent
    page.wait_for_selector("h3:has-text('Base Stats')")
    # Cliquer sur le bouton "PREDICT MEGA"
    page.click("button:has-text('PREDICT MEGA')")
    # Attendre que la prédiction soit chargée (attente arbitraire)
    page.wait_for_selector(".stat-increase", timeout=10000)
    # Vérifier qu'au moins une augmentation de statistique est affichée
    expect(page.locator(".stat-increase")).to_be_visible() 