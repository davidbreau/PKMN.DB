from typing import Dict

def pytest_configure(config):
    config.option.base_url = "http://localhost:8501"

def pytest_playwright_configure(config):
    config.expect_timeout = 10000  # 10 seconds
    config.viewport = {"width": 1280, "height": 720}
    config.video = "retain-on-failure"
    config.screenshot = "only-on-failure"
    
    # Browser configurations
    config.browser_configs = [
        {"name": "chromium", "headless": True},
        {"name": "firefox", "headless": True},
        # Uncomment to test with WebKit (Safari)
        # {"name": "webkit", "headless": True},
    ] 