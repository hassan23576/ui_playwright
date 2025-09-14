from playwright.sync_api import Page, expect


class CheckboxesPage:
    URL = "/checkboxes"

    def __init__(self, page: Page):
        self.page = page
        self._checkboxes = page.locator("#checkboxes input[type='checkbox']")

    # Navigation
    def goto(self):
        self.page.goto(self.URL)
        expect(self._checkboxes).to_have_count(2)

    # Actions
    def check(self, index: int):
        self._checkboxes.nth(index).check()

    def uncheck(self, index: int):
        self._checkboxes.nth(index).uncheck()

    # State (return boolean)
    def is_checked(self, index: int) -> bool:
        return self._checkboxes.nth(index).is_checked()

