"""
AdminRolesPage - Admin & Roles module.

Manages platform-level admin users and their roles (Super Admin, Admin,
Viewer - PRD section 3 "User Roles"). Structurally identical to the Hotel
list: a view switch (Admin / Roles), a table with a per-row action menu,
and Add/Edit/Delete flows.
"""
from __future__ import annotations

from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from pages.components.person_form import PersonForm


class AdminRolesPage(BasePage):
    PATH = "/admin-roles"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Admin & Roles")
        self.view_switcher = page.get_by_role("combobox").first

        # Add Admin: [0] toolbar button, [1] submit inside the modal.
        self.add_admin_button = page.get_by_role("button", name="Add Admin").nth(0)
        self.add_admin_submit = page.get_by_role("button", name="Add Admin").nth(1)
        self.add_admin_heading = page.get_by_role("heading", name="Add Admin")
        self.person_form = PersonForm(page)
        self.admin_role_select = page.get_by_role("combobox").nth(2)

        self.edit_admin_heading = page.get_by_role("heading", name="Edit Admin")
        # Semantic role instead of a Tailwind class selector, which breaks
        # the moment styling changes. Unverified against the live "Edit
        # Admin" dialog - if it is not exposed as a switch, check the
        # aria_snapshot.yaml written on failure and adjust.
        self.status_switch = page.get_by_role("switch")

    def expect_loaded(self) -> None:
        expect(self.heading).to_be_visible()

    def switch_view(self, view: str) -> None:
        """view: 'Admin' or 'Roles' (any case)."""
        self.view_switcher.select_option(view.capitalize())

    # ------------------------------ Add admin -------------------------- #
    def add_admin(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        password: str,
        role_option_value: str,
    ) -> None:
        self.add_admin_button.click()
        expect(self.add_admin_heading).to_be_visible()
        self.person_form.fill(first_name, last_name, email, phone, password)
        self.admin_role_select.select_option(role_option_value)
        self.add_admin_submit.click()
        expect(self.add_admin_heading).to_be_hidden()

    # ------------------------- Edit / status toggle -------------------- #
    def edit_admin(self, row_name_pattern: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_button("Edit")
        expect(self.edit_admin_heading).to_be_visible()

    def toggle_status(self) -> None:
        self.status_switch.click()

    def select_status_option(self, status: str) -> None:
        """status: 'Active' or 'Inactive'."""
        self.page.get_by_text(status, exact=True).click()

    # -------------------------------- Delete --------------------------- #
    def delete_admin(self, row_name_pattern: str) -> None:
        # Delete is a sibling of Edit in the row menu (an earlier version
        # clicked Edit first, which opened the wrong dialog).
        self.open_row_actions(row_name_pattern)
        self.click_button("Delete")  # menu item
        self.click_button("Delete")  # confirm in dialog

    def expect_delete_confirmation(self, admin_full_name: str) -> None:
        expect(self.page.get_by_text(f"delete {admin_full_name}", exact=False)).to_be_visible()
