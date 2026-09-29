"""
BasePage
========
Every list/table screen in the Oneflare Hotel Admin Backend (Admin Mgt,
Subscription, Notification, Staff, Reports, Logs, Admin & Roles) shares the
same building blocks: a search box, a "Filter" popover with "Apply"/"Clear",
row action buttons, an "Export" download button, and a pagination footer
(◀ / ▶, "Go to Page", "Rows Per Page").

Centralising those interactions here keeps every concrete Page Object thin
and stops the same locator from being re-invented (and re-broken) in five
different files.
"""
from __future__ import annotations

from typing import Optional

from playwright.sync_api import Download, Locator, Page, expect

from config import DEFAULT_TIMEOUT_MS, NAV_TIMEOUT_MS

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
        self.page.set_default_timeout(DEFAULT_TIMEOUT_MS)

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
            self.page.wait_for_url(f"**{path}", timeout=NAV_TIMEOUT_MS)

    def logout(self) -> None:
        self.page.get_by_role("button", name="Logout").click()

    # ------------------------------------------------------------------ #
    # Search                                                             #
    # ------------------------------------------------------------------ #
    @property
    def search_box(self) -> Locator:
        return self.page.get_by_role("textbox", name="Search")

    def search(self, term: str, press_enter: bool = True) -> None:
        self.search_box.click()
        self.search_box.fill(term)
        if press_enter:
            self.search_box.press("Enter")

    def clear_search(self) -> None:
        self.search_box.fill("")

    # ------------------------------------------------------------------ #
    # Filter popover                                                     #
    # ------------------------------------------------------------------ #
    def open_filter(self) -> None:
        self.page.get_by_role("button", name="Filter", exact=True).click()
        expect(self.page.get_by_role("heading", name="Filter")).to_be_visible()

    def apply_filter(self) -> None:
        self.page.get_by_role("button", name="Apply").click()

    def clear_filter(self) -> None:
        self.page.get_by_role("button", name="Clear").click()

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

    def click_row_action_button(self, row_name_pattern: str, button_index: int = 0) -> None:
        """Open the kebab / action button for a given row."""
        self.row(row_name_pattern).get_by_role("button").nth(button_index).click()

    def expect_row_visible(self, row_name_pattern: str) -> None:
        """Uses `.first` deliberately: some tables legitimately contain many
        rows sharing a substring (e.g. several log entries performed by the
        same admin name), which previously tripped Playwright's strict-mode
        "resolved to N elements" error on a plain visibility check. Callers
        that need to assert an *exact single* match should use `.row(...)`
        directly with their own `expect(...).to_have_count(1)`."""
        expect(self.row(row_name_pattern).first).to_be_visible()

    def expect_no_data(self) -> None:
        expect(self.page.get_by_role("row", name="No data.")).to_be_visible()

    # ------------------------------------------------------------------ #
    # Pagination footer                                                  #
    # ------------------------------------------------------------------ #
    @property
    def prev_page_button(self) -> Locator:
        return self.page.get_by_role("button", name="◀")

    @property
    def next_page_button(self) -> Locator:
        return self.page.get_by_role("button", name="▶")

    @property
    def go_to_page_input(self) -> Locator:
        return self.page.get_by_role("spinbutton").nth(0)

    @property
    def rows_per_page_input(self) -> Locator:
        return self.page.get_by_role("spinbutton").nth(1)

    def go_to_page(self, page_number: int) -> None:
        self.go_to_page_input.click()
        self.go_to_page_input.fill(str(page_number))

    def set_rows_per_page(self, rows: int) -> None:
        self.rows_per_page_input.click()
        self.rows_per_page_input.fill(str(rows))

    def next_page(self) -> None:
        self.next_page_button.click()

    def prev_page(self) -> None:
        self.prev_page_button.click()

    def expect_page_indicator(self, text_pattern) -> None:
        expect(self.page.get_by_text("Page")).to_contain_text(text_pattern)

    # ------------------------------------------------------------------ #
    # Export / download                                                  #
    # ------------------------------------------------------------------ #
    def export(self) -> Download:
        with self.page.expect_download() as download_info:
            self.page.get_by_role("button", name="Export").click()
        return download_info.value

    # ------------------------------------------------------------------ #
    # Modals / dialogs                                                   #
    # ------------------------------------------------------------------ #
    def expect_modal_heading(self, heading: str) -> None:
        expect(self.page.get_by_role("heading", name=heading)).to_be_visible()

    def close_modal(self) -> None:
        self.page.get_by_role("button", name="Close").click()

    def confirm(self, button_name: str = "Confirm") -> None:
        self.page.get_by_role("button", name=button_name).click()

    def cancel(self) -> None:
        self.page.get_by_role("button", name="Cancel").click()
