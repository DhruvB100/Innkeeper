"""
Selenium UI tests for Innkeeper frontend.

These tests need a running backend (port 8000) and frontend (port 3000).
Run with: pytest selenium_tests/test_ui.py

Note: you'll need Chrome and chromedriver installed.
I'm using webdriver-manager to handle the driver automatically.
"""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


FRONTEND_URL = "http://localhost:3000"


@pytest.fixture(scope="session")
def driver():
    """Set up Chrome driver for tests"""
    options = Options()
    options.add_argument("--headless")  # Run without UI (for CI)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)

    yield driver
    driver.quit()


def wait_for_element(driver, by, value, timeout=10):
    """Helper to wait for an element to be visible"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )


class TestHomePage:
    """Tests for the home page"""

    def test_home_page_loads(self, driver):
        """Home page should load without errors"""
        driver.get(FRONTEND_URL)
        # Check the navbar is there
        navbar = wait_for_element(driver, By.TAG_NAME, "nav")
        assert navbar is not None

    def test_navbar_has_login_link(self, driver):
        """Navbar should show login link when not logged in"""
        driver.get(FRONTEND_URL)
        time.sleep(1)  # wait for react to render

        # Find Login link
        login_links = driver.find_elements(By.LINK_TEXT, "Login")
        assert len(login_links) > 0, "Login link not found in navbar"

    def test_innkeeper_logo_in_navbar(self, driver):
        """The Innkeeper logo/brand should be in the navbar"""
        driver.get(FRONTEND_URL)
        time.sleep(1)

        # Look for Innkeeper text
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Innkeeper" in body_text


class TestLoginPage:
    """Tests for the login page"""

    def test_login_page_loads(self, driver):
        """Login page should have username and password fields"""
        driver.get(f"{FRONTEND_URL}/login")
        time.sleep(1)

        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        assert username_field is not None
        assert password_field is not None

    def test_login_form_validation(self, driver):
        """Submitting empty form should not crash"""
        driver.get(f"{FRONTEND_URL}/login")
        time.sleep(1)

        # Try to submit empty form
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        time.sleep(0.5)

        # Page should still be on login (not redirected away)
        assert "login" in driver.current_url or "Login" in driver.page_source

    def test_login_shows_error_for_wrong_credentials(self, driver):
        """Wrong credentials should show error message"""
        driver.get(f"{FRONTEND_URL}/login")
        time.sleep(1)

        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        username_field.send_keys("wronguser")
        password_field.send_keys("wrongpassword")

        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()

        # Wait for error message
        time.sleep(2)
        page_text = driver.find_element(By.TAG_NAME, "body").text
        # Should show some error
        assert "Invalid" in page_text or "wrong" in page_text.lower() or "error" in page_text.lower()


class TestRegisterPage:
    """Tests for registration page"""

    def test_register_page_has_required_fields(self, driver):
        """Register page should have all required fields"""
        driver.get(f"{FRONTEND_URL}/register")
        time.sleep(1)

        # Check for username, email, password fields
        assert driver.find_element(By.ID, "username") is not None
        assert driver.find_element(By.ID, "email") is not None
        assert driver.find_element(By.ID, "password") is not None

    def test_password_mismatch_shows_error(self, driver):
        """Mismatched passwords should show error"""
        driver.get(f"{FRONTEND_URL}/register")
        time.sleep(1)

        driver.find_element(By.ID, "username").send_keys("newuser123")
        driver.find_element(By.ID, "email").send_keys("new@test.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.ID, "password2").send_keys("differentpassword")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(0.5)

        # Should show error about passwords
        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert "match" in page_text.lower() or "password" in page_text.lower()


class TestPublicPostsPage:
    """Tests for viewing posts"""

    def test_home_shows_public_posts_section(self, driver):
        """Home page should show the public posts section"""
        driver.get(FRONTEND_URL)
        time.sleep(2)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        # Should show either posts or empty state message
        assert "Post" in body_text or "No" in body_text


class TestAuthorsPage:
    """Tests for the people/authors page"""

    def test_authors_page_loads(self, driver):
        """Authors page should load"""
        driver.get(f"{FRONTEND_URL}/authors")
        time.sleep(1)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "People" in body_text or "Innkeeper" in body_text

    def test_search_bar_is_present(self, driver):
        """Authors page should have a search bar"""
        driver.get(f"{FRONTEND_URL}/authors")
        time.sleep(1)

        # Check for search input
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        assert len(inputs) > 0, "No search input found on authors page"
