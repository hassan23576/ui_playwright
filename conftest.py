import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture
def page(pytestconfig):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(base_url=pytestconfig.getini('base_url').rstrip('/'))
        page = context.new_page()
        yield page
        context.close()
        browser.close()
