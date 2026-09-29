"""
BasePage
========
Every list/table screen in the Oneflare Hotel Admin Backend (Admin Mgt,
Subscription, Notification, Staff, Reports, Logs, Admin & Roles) shares the
same building blocks: a search box, a "Filter" popover with "Apply"/"Clear",
a per-row action menu, an "Export" download button, and a pagination footer
(◀ / ▶, "Go to Page", "Rows Per Page").

Centralising those interactions here keeps every concrete Page Object thin
and stops the same locator from being re-invented (and re-broken) in five
different files.
"""
from __future__ import annotations

from playwright.sync_api import Download, Locator, Page, expect

# Sidebar link accessible name -> the URL fragment its route settles on.
# Used to positively confirm an SPA route change completed instead of
# racing expect() against a client-side render that hasn't started yet.
NAV_PATHS = {
    "Dashboard": "/dashboard",
    "Admin Mgt": "/admin-mgt",
    "Subscription": "/subscription",
    "Notification": "/notification",
    "Staff": "/staff",
    "Reports": "/reports",
    "Logs": "/logs",
    "Admin & Roles": "/admin-roles",
}


class BasePage:
    def __init__(self, page: Page):
        self.page = page

        # Locators are lazy: declaring them here does not touch the browser.
        # They are resolved fresh every time an action or assertion uses them.
        self.search_box = page.get_by_role("textbox", name="Search")
        self.filter_button = page.get_by_role("button", name="Filter", exact=True)
        self.filter_heading = page.get_by_role("heading", name="Filter")
        self.apply_button = page.get_by_role("button", name="Apply")
        self.clear_button = page.get_by_role("button", name="Clear")
        self.export_button = page.get_by_role("button", name="Export")
        self.prev_page_button = page.get_by_role("button", name="◀")
        self.next_page_button = page.get_by_role("button", name="▶")
        self.go_to_page_input = page.get_by_role("spinbutton").nth(0)
        self.rows_per_page_input = page.get_by_role("spinbutton").nth(1)
        self.no_data_row = page.get_by_role("row", name="No data.")

    # ------------------------------------------------------------------ #
    # Generic navigation (left sidebar)                                  #
    # ------------------------------------------------------------------ #
    def open_nav_link(self, link_name: str) -> None:
        """Click a sidebar link, e.g. 'Dashboard', 'Admin Mgt', 'Subscription',
        'Notification', 'Staff', 'Reports', 'Logs', 'Admin & Roles', and wait
        for the client-side route to actually settle on the new URL before
        returning control to the caller."""
        self.page.get_by_role("link", name=link_name, exact=True).click()
        path = NAV_PATHS.get(link_name)
        if path:
            self.page.wait_for_url(f"**{path}")

    def logout(self) -> None:
        self.page.get_by_role("button", name="Logout").click()

    # ------------------------------------------------------------------ #
    # Forms                                                              #
    # ------------------------------------------------------------------ #
    def input_by_name(self, name: str) -> Locator:
        """`<input name="...">` - the form fields in this app have stable
        `name` attributes but no visible <label>, so this is the most robust
        hook available."""
        return self.page.locator(f'input[name="{name}"]')

    def fill_input(self, name: str, value: str) -> None:
        # `fill()` already focuses and clears the field; a preceding
        # `click()` (as Codegen records it) is redundant.
        self.input_by_name(name).fill(value)

    # ------------------------------------------------------------------ #
    # Search                                                             #
    # ------------------------------------------------------------------ #
    def search(self, term: str, press_enter: bool = True) -> None:
        self.search_box.fill(term)
        if press_enter:
            self.search_box.press("Enter")

    def clear_search(self) -> None:
        self.search_box.fill("")

    # ------------------------------------------------------------------ #
    # Filter popover                                                     #
    # ------------------------------------------------------------------ #
    def open_filter(self) -> None:
        self.filter_button.click()
        expect(self.filter_heading).to_be_visible()

    def apply_filter(self) -> None:
        self.apply_button.click()

    def clear_filter(self) -> None:
        self.clear_button.click()

    def select_filter_combobox(self, value: str, index: int = 0) -> None:
        """Select an <option value=...> inside the nth combobox of the open
        Filter panel (status, hotel, action type, etc. all render as
        <select> elements in this app)."""
        self.page.get_by_role("combobox").nth(index).select_option(value)

    # ------------------------------------------------------------------ #
    # Table rows                                                         #
    # ------------------------------------------------------------------ #
    def row(self, row_name_pattern: str) -> Locator:
        """Locate a table row by its accessible name (Playwright matches on
        the row's flattened text content, so a distinctive substring, e.g.
        the hotel name or S/N, is usually enough)."""
        return self.page.get_by_role("row", name=row_name_pattern)

    def open_row_actions(self, row_name_pattern: str) -> None:
        """Open the kebab / action menu of a row.

        `.first` - the pattern may match several rows; act on the first.
        `.last`  - a row can render more than one <button> (an inline status
                   control plus the kebab); the action-menu trigger is
                   consistently the last one. An un-indexed
                   get_by_role("button") threw a strict-mode "resolved to
                   2 elements" error on the Admin & Roles table.
        """
        self.row(row_name_pattern).first.get_by_role("button").last.click()

    def expect_row_visible(self, row_name_pattern: str) -> None:
        """Uses `.first` deliberately: some tables legitimately contain many
        rows sharing a substring (e.g. several log entries performed by the
        same admin name), which would otherwise trip Playwright's strict-mode
        "resolved to N elements" error on a plain visibility check. Callers
        that need to assert an *exact single* match should use `.row(...)`
        directly with their own `expect(...).to_have_count(1)`."""
        expect(self.row(row_name_pattern).first).to_be_visible()

    def expect_row_absent(self, row_name_pattern: str) -> None:
        """Assert that *no* row matches - the positive proof a delete worked.
        Search for the record first so pagination can't hide it."""
        expect(self.row(row_name_pattern)).to_have_count(0)

    def expect_no_data(self) -> None:
        expect(self.no_data_row).to_be_visible()

    # ------------------------------------------------------------------ #
    # Pagination footer                                                  #
    # ------------------------------------------------------------------ #
    def go_to_page(self, page_number: int) -> None:
        self.go_to_page_input.fill(str(page_number))

    def set_rows_per_page(self, rows: int) -> None:
        self.rows_per_page_input.fill(str(rows))

    def next_page(self) -> None:
        self.next_page_button.click()

    def prev_page(self) -> None:
        self.prev_page_button.click()

    # ------------------------------------------------------------------ #
    # Export / download                                                  #
    # ------------------------------------------------------------------ #
    def export(self) -> Download:
        """Click Export and return the resulting Download. `expect_download`
        must wrap the click: it starts listening *before* the event fires,
        so a fast download can't be missed."""
        with self.page.expect_download() as download_info:
            self.export_button.click()
        return download_info.value

    # ------------------------------------------------------------------ #
    # Modals / dialogs                                                   #
    # ------------------------------------------------------------------ #
    def expect_modal_heading(self, heading: str) -> None:
        expect(self.page.get_by_role("heading", name=heading)).to_be_visible()

    def expect_modal_closed(self, heading: str) -> None:
        """A modal that disappears after submit is the UI's signal that the
        server accepted the change (validation errors keep it open)."""
        expect(self.page.get_by_role("heading", name=heading)).to_be_hidden()

    def click_button(self, name: str) -> None:
        """Click a button by accessible name - used for row-menu items
        (Edit / Delete / ...) and modal buttons (Update / Confirm / ...)."""
        self.page.get_by_role("button", name=name).click()

    def close_modal(self) -> None:
        self.click_button("Close")

    def confirm(self, button_name: str = "Confirm") -> None:
        self.click_button(button_name)

    def cancel(self) -> None:
        self.click_button("Cancel")
