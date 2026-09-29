"""
NotificationPage - Notification module (PRD 2.4 "Notifications").

Supports platform-wide announcements and hotel-targeted alerts. Notification
rows are clickable and open a read-only details panel (Title, Type, Media
Type, Status, Start/End Date, Audience, Created By, Message).
"""
from __future__ import annotations

from typing import Iterable, Optional

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class NotificationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def expect_loaded(self) -> None:
        expect(self.page.get_by_role("button", name="Filter")).to_be_visible()

    # ---------------------------- Add notification ----------------------- #
    def click_add_notification(self) -> None:
        self.page.get_by_role("button", name="Add Notification").click()
        expect(self.page.get_by_role("heading", name="Add Notification")).to_be_visible()

    def fill_notification_form(
        self,
        title: str,
        notification_type: str,
        message: str,
        media_type: str,
        start_date: str,
        end_date: str,
    ) -> None:
        self.page.locator('input[name="title"]').click()
        self.page.locator('input[name="title"]').fill(title)
        self.page.get_by_role("combobox").first.select_option(notification_type)
        self.page.locator('textarea[name="message"]').click()
        self.page.locator('textarea[name="message"]').fill(message)
        self.page.get_by_role("combobox").nth(1).select_option(media_type)
        self.page.locator('input[name="startDate"]').fill(start_date)
        self.page.locator('input[name="endDate"]').fill(end_date)

    def select_all_hotels(self) -> None:
        self.page.get_by_text("Select All").click()

    def select_hotel(self, hotel_checkbox_label: str) -> None:
        self.page.get_by_role("checkbox", name=hotel_checkbox_label).check()

    def submit_notification(self) -> None:
        self.page.get_by_role("button", name="Create").click()

    def add_notification(
        self,
        title: str,
        notification_type: str,
        message: str,
        media_type: str,
        start_date: str,
        end_date: str,
        hotels: Optional[Iterable[str]] = None,
    ) -> None:
        """End-to-end: open form, fill it, target hotels (or Select All when
        `hotels` is omitted) and submit."""
        self.click_add_notification()
        self.fill_notification_form(title, notification_type, message, media_type, start_date, end_date)
        if hotels:
            for hotel_name in hotels:
                self.select_hotel(hotel_name)
        else:
            self.select_all_hotels()
        self.submit_notification()

    # ---------------------------- View details ---------------------------- #
    def open_notification(self, row_name_pattern: str) -> None:
        self.row(row_name_pattern).click()

    def expect_details_visible(self, title: str) -> None:
        expect(self.page.get_by_role("heading", name=title)).to_be_visible()

    def close_details(self) -> None:
        self.page.get_by_role("button", name="Close").click()
