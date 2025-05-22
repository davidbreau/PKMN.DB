import re
from playwright.sync_api import Page, expect

def test_homepage_title(page: Page):
    # Navigate to the homepage
    page.goto("http://localhost:8501")
    
    # Wait for Streamlit to load
    page.wait_for_selector("h1")
    
    # Check if the title contains "PKMN.DB"
    expect(page.locator("h1")).to_contain_text("PKMN.DB")

def test_navigation_elements(page: Page):
    page.goto("http://localhost:8501")
    
    # Check if main navigation elements are present
    expect(page.get_by_role("navigation")).to_be_visible()
    
    # Verify that the sidebar is present
    expect(page.locator("[data-testid='stSidebar']")).to_be_visible() 