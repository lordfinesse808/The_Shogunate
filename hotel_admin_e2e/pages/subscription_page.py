"""
SubscriptionPage - Subscription module (PRD 2.3 "Subscription Management").

Renders as a single screen with a view-switcher combobox toggling between
"Subscriptions" (assigned instances) and "Packages" (plan catalogue), plus
the standard search/filter/export/pagination footer inherited from
BasePage.
"""
from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SubscriptionPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def expect_loaded(self) -> None:
        """`get_by_role("heading")` with no `name` matches *every* heading on
        the page and previously threw a strict-mode error whose captured
        snapshot showed we were still on the Dashboard (its own headings —
        "Hotels with Active Subscriptions" etc. — contain the word
        "Subscription" too). Confirming the route first removes the race;
        the Filter button then confirms the table/toolbar actually
        rendered."""
        expect(self.page).to_have_url(re.compile(r"/subscription"))
        expect(self.page.get_by_role("button", name="Filter")).to_be_visible()

    # ---------------------------- View switch -------------------------- #
    def switch_view(self, view: str) -> None:
        """view: 'Subscriptions' or 'Packages'."""
        self.page.get_by_role("combobox").select_option(view.upper())

    # ---------------------------- Add subscription ---------------------- #
    def click_add_subscription(self) -> None:
        self.page.get_by_role("button", name="Add Subscription").click()

    # ---------------------------- Row actions --------------------------- #
    def open_row_actions(self, row_name_pattern: str) -> None:
        # `.last` guards against rows that render more than one <button>
        # (e.g. an inline status pill alongside the kebab/action trigger) —
        # the action-menu opener is consistently the last button in the row.
        self.row(row_name_pattern).first.get_by_role("button").last.click()

    def edit_subscription(
        self,
        row_name_pattern: str,
        package_option_value: str | None = None,
        duration_option_value: str | None = None,
    ) -> None:
        self.open_row_actions(row_name_pattern)
        self.page.get_by_role("button", name="Edit").click()
        if package_option_value:
            self.page.get_by_role("combobox").nth(1).select_option(package_option_value)
            self.page.get_by_role("button", name="Update").click()
        if duration_option_value:
            self.page.get_by_role("combobox").nth(2).select_option(duration_option_value)
            self.page.get_by_role("button", name="Update").click()

    def delete_subscription(self, row_name_pattern: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.page.get_by_role("button", name="Edit").click()
        self.page.get_by_role("button", name="Delete").click()
        self.page.get_by_role("button", name="Delete").click()  # confirm

    def expect_edit_panel_visible(self) -> None:
        expect(self.page.get_by_role("button", name="Edit")).to_be_visible()
