"""
AdminRolesPage - Admin & Roles module.

Manages platform-level admin users and their roles (Super Admin, Admin,
Viewer — PRD section 3 "User Roles"). Structurally identical to the Hotel
list: a view switch (Admin / Roles), a table with a per-row action menu,
and Add/Edit/Delete flows.
"""
from __future__ import annotations

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class AdminRolesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def expect_loaded(self) -> None:
        expect(self.page.get_by_role("heading", name="Admin & Roles")).to_be_visible()

    def switch_view(self, view: str) -> None:
        """view: 'Admin' or 'Roles'."""
        self.page.get_by_role("combobox").select_option(view.capitalize())

    # ---------------------------- Add admin ------------------------------- #
    def click_add_admin(self) -> None:
        self.page.get_by_role("button", name="Add Admin").click()
        expect(self.page.get_by_role("heading", name="Add Admin")).to_be_visible()

    def fill_admin_form(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        password: str,
        role_option_value: str,
    ) -> None:
        self.page.locator('input[name="firstName"]').click()
        self.page.locator('input[name="firstName"]').fill(first_name)
        self.page.locator('input[name="lastName"]').click()
        self.page.locator('input[name="lastName"]').fill(last_name)
        self.page.locator('input[name="email"]').click()
        self.page.locator('input[name="email"]').fill(email)
        self.page.get_by_role("textbox", name="8012345678").click()
        self.page.get_by_role("textbox", name="8012345678").fill(phone)
        self.page.locator('input[name="password"]').click()
        self.page.locator('input[name="password"]').fill(password)
        self.page.get_by_role("combobox").nth(2).select_option(role_option_value)

    def submit_add_admin(self) -> None:
        self.page.get_by_role("button", name="Add Admin").nth(1).click()

    def add_admin(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        password: str,
        role_option_value: str,
    ) -> None:
        self.click_add_admin()
        self.fill_admin_form(first_name, last_name, email, phone, password, role_option_value)
        self.submit_add_admin()

    # ---------------------------- Edit / status toggle ---------------------- #
    def open_row_actions(self, row_name_pattern: str) -> None:
        # `.last`: this row renders two <button> elements (an inline status
        # control plus the kebab/action trigger) — a plain, unindexed
        # get_by_role("button").click() threw a strict-mode "resolved to 2
        # elements" error. The action-menu opener is the last one.
        self.row(row_name_pattern).first.get_by_role("button").last.click()

    def edit_admin(self, row_name_pattern: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.page.get_by_role("button", name="Edit").click()
        expect(self.page.get_by_role("heading", name="Edit Admin")).to_be_visible()

    def toggle_status(self) -> None:
        # Prefer a semantic role locator over a Tailwind-class selector,
        # which breaks the moment styling changes. Confirm this against the
        # real "Edit Admin" dialog markup — if it isn't rendered as a
        # switch role, swap this for whatever role/label it actually uses.
        self.page.get_by_role("switch").click()

    def select_status_option(self, status: str) -> None:
        """status: 'Active' or 'Inactive'."""
        self.page.get_by_text(status, exact=True).click()

    # ---------------------------- Delete ------------------------------------ #
    def delete_admin(self, row_name_pattern: str) -> None:
        # NOTE: previously clicked "Edit" here before "Delete" — same bug
        # class as AdminManagementPage: open_row_actions() already opens the
        # menu that contains Delete directly; Edit is a sibling item, not a
        # prerequisite click.
        self.open_row_actions(row_name_pattern)
        self.page.get_by_role("button", name="Delete").click()
        self.page.get_by_role("button", name="Delete").click()  # confirm in dialog

    def expect_delete_confirmation(self, admin_full_name: str) -> None:
        expect(self.page.get_by_text(f"delete {admin_full_name}", exact=False)).to_be_visible()
