import pytest
from pages.checkboxes_page import CheckboxesPage


def test_checkbox_can_be_checked(page):
    checkboxes = CheckboxesPage(page)
    checkboxes.goto()

    # Act
    checkboxes.check(0)

    # Assert
    assert checkboxes.is_checked(0) is True
