"""
LogsPage - Logs module (PRD 2.7 "Logs").

Provides a system-wide audit trail with two tabs: "Hotel Logs" (default -
activity performed on/by hotels) and "Admin Logs" (platform-admin actions).
Both share search, filter-by-action-type, export and pagination.
"""
from __future__ import annotations

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LogsPage(BasePage):
    PATH = "/logs"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Logs")
        self.hotel_logs_tab = page.get_by_role("button", name="Hotel Logs")
        self.admin_logs_tab = page.get_by_role("button", name="Admin Logs")

    def expect_loaded(self) -> None:
        expect(self.heading).to_be_visible()

    def switch_to_hotel_logs(self) -> None:
        self.hotel_logs_tab.click()

    def switch_to_admin_logs(self) -> None:
        self.admin_logs_tab.click()

    def filter_by_action_type(self, action_type_value: str) -> None:
        self.open_filter()
        self.select_filter_combobox(action_type_value, index=1)
        self.apply_filter()
