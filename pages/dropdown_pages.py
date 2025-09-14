from time import sleep

from playwright.sync_api import Page, expect


class DropdownPage:
    URL = "/dropdown"

    def __init__(self, page: Page):
        self.page = page
        self._dropdown = page.locator("#dropdown")

    def goto(self):
        self.page.goto(self.URL)
        expect(self._dropdown).to_be_visible()

    def select_by_label(self, label: str):
        """
        Select option by visible text
        """
        self._dropdown.select_option(label=label)

    def select_by_value(self, value: str):
        """
        Select option by value attribute
        """
        self._dropdown.select_option(value=value)

    def get_selected_value(self) -> str:
        """
        Return the currently selected option's value
        """
        return self._dropdown.input_value()

    def get_all_options(self) -> list[str]:
        """
        Return a list of all available option texts
        """
        return [opt.inner_text() for opt in self.page.locator("dropdown option").all()]