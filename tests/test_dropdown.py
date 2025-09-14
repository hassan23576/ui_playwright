from pages.dropdown_pages import DropdownPage


def test_dropdown_can_be_selected(page):
    dropdown = DropdownPage(page)
    dropdown.goto()

    # Verify available options
    options = dropdown.get_all_options()
    assert options == ["Please select an option", "Option 1", "Option 2"]

    # Select "Option 1" by label
    dropdown.select_by_label('Option 1')
    assert dropdown.get_selected_value() == "1"

    # Select "Option 2" by value
    dropdown.select_by_value("2")
    assert dropdown.get_selected_value() == "2"