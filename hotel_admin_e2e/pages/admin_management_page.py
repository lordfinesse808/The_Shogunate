"""
AdminManagementPage - /admin-mgt

Covers PRD 2.2 "Admin Management" and the "Hotel Controls" bullet under 2.1:
add hotel, edit hotel, deactivate/reactivate, delete (soft, password-gated),
renew subscription and change subscription — all driven from a hotel row's
action menu.
"""
from __future__ import annotations

from typing import Optional

from playwright.sync_api import Page, expect

from config import BASE_URL
from pages.base_page import BasePage


class AdminManagementPage(BasePage):
    URL = f"{BASE_URL}/admin-mgt"

    def __init__(self, page: Page):
        super().__init__(page)

    def goto(self) -> "AdminManagementPage":
        self.page.goto(self.URL)
        return self

    def expect_loaded(self) -> None:
        expect(self.page.get_by_role("main")).to_be_visible()
        expect(self.page.get_by_role("main")).to_contain_text("Add Hotel")

    def expect_table_headers_visible(self) -> None:
        for header in ("Hotel Name", "Email", "Phone No", "Country", "City", "Status"):
            expect(self.page.get_by_role("columnheader", name=header)).to_be_visible()

    # ------------------------------------------------------------------ #
    # Add hotel                                                          #
    # ------------------------------------------------------------------ #
    def click_add_hotel(self) -> None:
        self.page.get_by_role("button", name="Add Hotel").click()

    def fill_add_hotel_form(self, name: str, email: str, phone: str, address: str) -> None:
        self.page.locator('input[name="name"]').fill(name)
        self.page.locator('input[name="email"]').fill(email)
        self.page.locator('input[name="phone"]').fill(phone)
        self.page.locator('input[name="address"]').fill(address)

    def submit_add_hotel(self) -> None:
        self.page.get_by_role("button", name="Add Hotel").nth(1).click()

    # ------------------------------------------------------------------ #
    # Row action menu                                                    #
    # ------------------------------------------------------------------ #
    def open_row_actions(self, row_name_pattern: str) -> None:
        # `.last` guards against rows with more than one <button> (e.g. an
        # inline status control alongside the kebab/action trigger).
        self.row(row_name_pattern).first.get_by_role("button").last.click()

    def click_edit(self) -> None:
        self.page.get_by_role("button", name="Edit").click()

    def click_deactivate(self) -> None:
        self.page.get_by_role("button", name="Deactivate").click()

    def click_reactivate(self) -> None:
        self.page.get_by_role("button", name="Reactivate").click()

    def click_delete(self) -> None:
        self.page.get_by_role("button", name="Delete").click()

    def click_renew_subscription(self) -> None:
        self.page.get_by_role("button", name="Renew Subscription").click()

    def click_change_subscription(self) -> None:
        self.page.get_by_role("button", name="Change Subscription").click()

    # ------------------------------------------------------------------ #
    # Edit hotel                                                         #
    # ------------------------------------------------------------------ #
    def expect_edit_hotel_dialog_visible(self) -> None:
        expect(self.page.get_by_role("heading", name="Edit Hotel Data")).to_be_visible()

    def set_address(self, address: str) -> None:
        address_input = self.page.locator('input[name="address"]')
        address_input.click()
        address_input.fill(address)

    def submit_update(self) -> None:
        self.page.get_by_role("button", name="Update").click()

    def edit_hotel(self, row_name_pattern: str, address: str) -> None:
        """Full flow: open row -> Edit -> change address -> Update."""
        self.open_row_actions(row_name_pattern)
        self.click_edit()
        self.expect_edit_hotel_dialog_visible()
        self.set_address(address)
        self.submit_update()

    # ------------------------------------------------------------------ #
    # Deactivate / Reactivate                                            #
    # ------------------------------------------------------------------ #
    def deactivate_hotel(self, row_name_pattern: str) -> None:
        # NOTE: previously called self.click_edit() here before
        # click_deactivate() — that was a bug. open_row_actions() opens the
        # action menu itself; Edit/Deactivate/Delete/Renew/Change are
        # sibling items in it, not nested behind "Edit".
        self.open_row_actions(row_name_pattern)
        self.click_deactivate()
        expect(self.page.get_by_role("heading", name="Deactivate Hotel")).to_be_visible()
        self.click_deactivate()  # confirm

    def reactivate_hotel(self, row_name_pattern: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_reactivate()

    # ------------------------------------------------------------------ #
    # Delete (password-gated soft delete)                                #
    # ------------------------------------------------------------------ #
    def delete_hotel(self, row_name_pattern: str, admin_password: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_delete()
        expect(self.page.get_by_role("heading", name="Delete Hotel")).to_be_visible()
        password_input = self.page.locator('input[type="password"]')
        password_input.click()
        password_input.fill(admin_password)
        self.confirm()

    # ----------------------------------------------------------------- #
    # Renew subscription                                                 #
    # ----------------------------------------------------------------- #
    def renew_subscription(self, row_name_pattern: str, duration_option_value: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_renew_subscription()
        self.page.get_by_role("combobox").select_option(duration_option_value)
        self.page.get_by_role("button", name="Renew").click()

    # ----------------------------------------------------------------- #
    # Change subscription (duration + package)                          #
    # ------------------------------------------------------------------ #
    def change_subscription(
        self,
        row_name_pattern: str,
        duration_option_value: str,
        package_option_value: str,
    ) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_change_subscription()
        self.page.get_by_role("combobox").nth(1).select_option(duration_option_value)
        self.page.get_by_role("combobox").first.select_option(package_option_value)
        self.page.get_by_role("button", name="Change").click()
