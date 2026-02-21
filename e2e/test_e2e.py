from playwright.sync_api import sync_playwright

BASE_URL = "http://webapp:8000"

def test_validate_number():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL)
        page.fill("#numberInput", "1234")
        page.click("#validateButton")
        page.wait_for_timeout(1000)
        assert page.inner_text("#result") == "N0úmero válido"
        browser.close()
def test_invalid_number():
     with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL)
        page.fill("#numberInput", "1123")
        page.click("#validateButton")
        page.wait_for_timeout(1000)
        assert page.inner_text("#result") == "Número inválido"
        browser.close()
        
