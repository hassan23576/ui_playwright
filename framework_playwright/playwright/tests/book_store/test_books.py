import logging

from playwright.sync_api import expect

from data.book_store_data import VALID_BOOK_ISBNS, INVALID_BOOK_ISBNS
from framework_playwright.playwright.pages.login_page import LoginPage


logger = logging.getLogger(__name__)

def test_user_can_see_added_books(api_user, bookstore_api, page, base_url):
    user_id = api_user['userId']
    username = api_user['username']
    password = api_user['password']

    token = bookstore_api.generate_token(username, password)
    isbns =VALID_BOOK_ISBNS

    try:
        add_books_response = bookstore_api.add_books(user_id, token, isbns)
        logger.info(f"Books added response: {add_books_response}")

        login_page = LoginPage(page, base_url)
        login_page.open_login_page()
        login_page.perform_login(username, password)

        isbn_title_map = bookstore_api.get_user_books_map(user_id, token)

        for isbn in isbns:
            book_title = isbn_title_map.get(isbn)
            assert book_title is not None
            expect(page.locator(f"text={book_title}")).to_be_visible()

    finally:
        fresh_token = bookstore_api.generate_token(username, password)
        bookstore_api.delete_all_books(user_id, fresh_token)



def test_user_cannot_add_invalid_books(api_user, bookstore_api, page, base_url):
    user_id = api_user["userId"]
    username = api_user["username"]
    password = api_user["password"]

    token = bookstore_api.generate_token(username, password)

    try:
        response = bookstore_api.add_books(
            user_id,
            token,
            INVALID_BOOK_ISBNS,
            raise_on_failure=False
        )

        assert response.status_code == 400
        assert "ISBN supplied is not available in Books Collection!" in response.text

        login_page = LoginPage(page, base_url)
        login_page.open_login_page()
        login_page.perform_login(username, password)

        expect(page.get_by_text("Page 1 of 0", exact=True)).to_be_visible()

    finally:
        fresh_token = bookstore_api.generate_token(username, password)
        bookstore_api.delete_all_books(user_id, fresh_token)

        delete_response = bookstore_api.delete_account(user_id, fresh_token)
        assert delete_response.status_code == 204


