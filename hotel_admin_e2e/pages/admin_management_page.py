"""
AdminManagementPage - /admin-mgt

Covers PRD 2.2 "Admin Management" and the "Hotel Controls" bullet under 2.1:
add hotel, edit hotel, deactivate/reactivate, delete (soft, password-gated),
renew subscription and change subscription - all driven from a hotel row's
action menu.
"""
from __future__ import annotations

from playwright.sync_api import Page, expect

from pages.base_page import BasePage

TABLE_HEADERS = ("Hotel Name", "Email", "Phone No", "Country", "City", "Status")


class AdminManagementPage(BasePage):
    PATH = "/admin-mgt"

    def __init__(self, page: Page):
        super().__init__(page)
        self.main = page.get_by_role("main")
        # "Add Hotel" appears twice once the modal is open: [0] toolbar
        # button, [1] the modal's submit button.
        self.add_hotel_button = page.get_by_role("button", name="Add Hotel").nth(0)
        self.add_hotel_submit = page.get_by_role("button", name="Add Hotel").nth(1)
        self.update_button = page.get_by_role("button", name="Update")
        self.password_confirm_input = page.locator('input[type="password"]')

    def goto(self) -> AdminManagementPage:
        self.page.goto(self.PATH)
        return self

    def expect_loaded(self) -> None:
        expect(self.main).to_contain_text("Add Hotel")

    def expect_table_headers_visible(self) -> None:
        for header in TABLE_HEADERS:
            expect(self.page.get_by_role("columnheader", name=header)).to_be_visible()

    # ------------------------------------------------------------------ #
    # Add hotel                                                          #
    # ------------------------------------------------------------------ #
    def add_hotel(self, name: str, email: str, phone: str, address: str) -> None:
        self.add_hotel_button.click()
        self.fill_input("name", name)
        self.fill_input("email", email)
        self.fill_input("phone", phone)
        self.fill_input("address", address)
        self.add_hotel_submit.click()

    # ------------------------------------------------------------------ #
    # Edit hotel                                                         #
    # ------------------------------------------------------------------ #
    def edit_hotel(self, row_name_pattern: str, address: str) -> None:
        """Full flow: open row -> Edit -> change address -> Update."""
        self.open_row_actions(row_name_pattern)
        self.click_button("Edit")
        self.expect_modal_heading("Edit Hotel Data")
        self.fill_input("address", address)
        self.update_button.click()
        self.expect_modal_closed("Edit Hotel Data")

    # ------------------------------------------------------------------ #
    # Deactivate / Reactivate                                            #
    # ------------------------------------------------------------------ #
    def deactivate_hotel(self, row_name_pattern: str) -> None:
        # Edit/Deactivate/Delete/Renew/Change are sibling items in the row
        # menu - an earlier version clicked "Edit" first, which opened the
        # Edit modal instead and hid the Deactivate item.
        self.open_row_actions(row_name_pattern)
        self.click_button("Deactivate")  # menu item
        self.expect_modal_heading("Deactivate Hotel")
        self.click_button("Deactivate")  # confirm button inside the modal
        self.expect_modal_closed("Deactivate Hotel")

    def reactivate_hotel(self, row_name_pattern: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_button("Reactivate")

    # ------------------------------------------------------------------ #
    # Delete (password-gated soft delete)                                #
    # ------------------------------------------------------------------ #
    def delete_hotel(self, row_name_pattern: str, admin_password: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_button("Delete")
        self.expect_modal_heading("Delete Hotel")
        self.password_confirm_input.fill(admin_password)
        self.confirm()
        self.expect_modal_closed("Delete Hotel")

    # ------------------------------------------------------------------ #
    # Subscription changes                                               #
    # ------------------------------------------------------------------ #
    def renew_subscription(self, row_name_pattern: str, duration_option_value: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_button("Renew Subscription")
        self.page.get_by_role("combobox").select_option(duration_option_value)
        renew = self.page.get_by_role("button", name="Renew")
        renew.click()
        # Same locator that was just clicked: once the modal is gone it
        # resolves to nothing, which is exactly what to_be_hidden() wants.
        expect(renew).to_be_hidden()

    def change_subscription(
        self,
        row_name_pattern: str,
        duration_option_value: str,
        package_option_value: str,
    ) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_button("Change Subscription")
        comboboxes = self.page.get_by_role("combobox")
        comboboxes.nth(1).select_option(duration_option_value)
        comboboxes.nth(0).select_option(package_option_value)
        change = self.page.get_by_role("button", name="Change")
        change.click()
        expect(change).to_be_hidden()
