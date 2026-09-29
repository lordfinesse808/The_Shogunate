"""
NotificationPage - Notification module (PRD 2.4 "Notifications").

Supports platform-wide announcements and hotel-targeted alerts. Notification
rows are clickable and open a read-only details panel (Title, Type, Media
Type, Status, Start/End Date, Audience, Created By, Message).
"""
from __future__ import annotations

from collections.abc import Iterable

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class NotificationPage(BasePage):
    PATH = "/notification"

    def __init__(self, page: Page):
        super().__init__(page)
        self.add_notification_button = page.get_by_role("button", name="Add Notification")
        self.add_notification_heading = page.get_by_role("heading", name="Add Notification")
        self.message_input = page.locator('textarea[name="message"]')
        self.type_select = page.get_by_role("combobox").nth(0)
        self.media_type_select = page.get_by_role("combobox").nth(1)
        self.select_all_hotels_option = page.get_by_text("Select All")
        self.create_button = page.get_by_role("button", name="Create")

    def expect_loaded(self) -> None:
        expect(self.filter_button).to_be_visible()

    # ------------------------- Add notification ------------------------ #
    def open_add_notification(self) -> None:
        self.add_notification_button.click()
        expect(self.add_notification_heading).to_be_visible()

    def fill_notification_form(
        self,
        title: str,
        notification_type: str,
        message: str,
        media_type: str,
        start_date: str,
        end_date: str,
    ) -> None:
        self.fill_input("title", title)
        self.type_select.select_option(notification_type)
        self.message_input.fill(message)
        self.media_type_select.select_option(media_type)
        self.fill_input("startDate", start_date)
        self.fill_input("endDate", end_date)

    def select_all_hotels(self) -> None:
        self.select_all_hotels_option.click()

    def select_hotel(self, hotel_checkbox_label: str) -> None:
        self.page.get_by_role("checkbox", name=hotel_checkbox_label).check()

    def add_notification(
        self,
        title: str,
        notification_type: str,
        message: str,
        media_type: str,
        start_date: str,
        end_date: str,
        hotels: Iterable[str] | None = None,
    ) -> None:
        """End-to-end: open form, fill it, target hotels (or Select All when
        `hotels` is omitted) and submit."""
        self.open_add_notification()
        self.fill_notification_form(title, notification_type, message, media_type, start_date, end_date)
        if hotels:
            for hotel_name in hotels:
                self.select_hotel(hotel_name)
        else:
            self.select_all_hotels()
        self.create_button.click()
        expect(self.add_notification_heading).to_be_hidden()

    # --------------------------- View details -------------------------- #
    def open_notification(self, row_name_pattern: str) -> None:
        self.row(row_name_pattern).first.click()

    def expect_details_visible(self, title: str) -> None:
        expect(self.page.get_by_role("heading", name=title)).to_be_visible()

    def close_details(self) -> None:
        self.close_modal()
