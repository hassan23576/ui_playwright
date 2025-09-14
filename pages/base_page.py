def test_homepage(page):
    page.goto("https://the-internet.herokuapp.com")
    assert "The Internet" in page.title()