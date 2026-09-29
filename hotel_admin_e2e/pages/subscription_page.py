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
    PATH = "/subscription"

    def __init__(self, page: Page):
        super().__init__(page)
        self.view_switcher = page.get_by_role("combobox").first
        self.add_subscription_button = page.get_by_role("button", name="Add Subscription")

    def expect_loaded(self) -> None:
        """`get_by_role("heading")` with no `name` matches *every* heading on
        the page and previously threw a strict-mode error whose captured
        snapshot showed we were still on the Dashboard (its own headings -
        "Hotels with Active Subscriptions" etc. - contain the word
        "Subscription" too). Confirming the route first removes the race;
        the Filter button then confirms the table/toolbar actually
        rendered."""
        expect(self.page).to_have_url(re.compile(self.PATH))
        expect(self.filter_button).to_be_visible()

    # ---------------------------- View switch -------------------------- #
    def switch_view(self, view: str) -> None:
        """view: 'Subscriptions' or 'Packages' (any case) - the <option>
        values are upper-case."""
        self.view_switcher.select_option(view.upper())

    # ------------------------- Add subscription ------------------------ #
    def click_add_subscription(self) -> None:
        self.add_subscription_button.click()

    # ---------------------------- Row actions -------------------------- #
    def edit_subscription(
        self,
        row_name_pattern: str,
        package_option_value: str | None = None,
        duration_option_value: str | None = None,
    ) -> None:
        """Each field is saved with its own Update click, matching how the
        recorded flow behaved (the edit panel stays open between saves)."""
        self.open_row_actions(row_name_pattern)
        self.click_button("Edit")
        comboboxes = self.page.get_by_role("combobox")
        if package_option_value:
            comboboxes.nth(1).select_option(package_option_value)
            self.click_button("Update")
        if duration_option_value:
            comboboxes.nth(2).select_option(duration_option_value)
            self.click_button("Update")

    def delete_subscription(self, row_name_pattern: str) -> None:
        # Unlike hotels, Delete lives inside the subscription's Edit panel,
        # and the confirmation dialog repeats the "Delete" label.
        self.open_row_actions(row_name_pattern)
        self.click_button("Edit")
        self.click_button("Delete")  # opens the confirmation dialog
        self.click_button("Delete")  # confirms it
