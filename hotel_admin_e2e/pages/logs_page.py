"""
LogsPage - Logs module (PRD 2.7 "Logs").

Provides a system-wide audit trail with two tabs: "Hotel Logs" (default -
activity performed on/by hotels) and "Admin Logs" (platform-admin actions).
Both share search, filter-by-action-type, and pagination.
"""
from __future__ import annotations

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LogsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def expect_loaded(self) -> None:
        expect(self.page.get_by_role("heading", name="Logs")).to_be_visible()

    def switch_to_hotel_logs(self) -> None:
        self.page.get_by_role("button", name="Hotel Logs").click()

    def switch_to_admin_logs(self) -> None:
        self.page.get_by_role("button", name="Admin Logs").click()

    def filter_by_action_type(self, action_type_value: str) -> None:
        self.open_filter()
        self.select_filter_combobox(action_type_value, index=1)
        self.apply_filter()

    def open_log_details(self, details_button_text: str) -> None:
        self.page.get_by_role("button", name=details_button_text).click()
