import re

from playwright.sync_api import Page, expect


def test_home_page_tite(page):
    page.goto('https://the-internet.herokuapp.com/')
    assert 'The Internet' in page.title()

def test_home_page_title(page):
    page.goto('https://the-internet.herokuapp.com/')
    expect(page).to_have_title('The Internet')
