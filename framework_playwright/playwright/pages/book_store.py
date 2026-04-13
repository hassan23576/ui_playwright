import logging
import re

from playwright.sync_api import Page, expect

from framework_playwright.playwright.pages.base_page import BasePage

logger = logging.getLogger(__name__)


class BookStorePage(BasePage):
    path = "/books"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)


    def open(self):
        logger.info(f"Opening Books page:{self.base_url}{self.path}")
        self.navigate_to(self.path)
        expect(self.page).to_have_url(re.compile(f"*.{self.path}$"))
        expect(self.page.locator(".book-wrapper")).to_be_visible()


    def get_book_count(self, page: Page):
        rows = page.locator("tr")
        count = rows.count()


        for i in range(count):
            row = rows.nth(i)
            title = row.locator("a")
            expect(title).to_be_visible()
