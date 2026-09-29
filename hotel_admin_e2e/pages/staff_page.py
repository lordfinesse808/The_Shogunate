"""
StaffPage - Staff module (PRD 2.5 "Staff Management").

Covers: hotel-scoped staff table, role creation with page-level permission
switches, staff creation with client-side phone validation, staff editing
and status filtering.
"""
from __future__ import annotations

from typing import Iterable

from playwright.sync_api import Page, expect

from pages.base_page import BasePage

# Module switches available on the "Add Role" / "Create Role" permission
# matrix, in the order the app renders them.
ALL_PERMISSION_MODULES = (
    "Dashboard",
    "Management",
    "Reservations",
    "Guests",
    "Rooms",
    "Inventory",
    "Warehouse",
    "Reports",
    "Settings",
    "Administration",
    "Finance",
    "Housekeeping",
    "Maintenance",
)


class StaffPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

    def expect_loaded(self) -> None:
        expect(self.page.get_by_role("heading", name="Staff Management")).to_be_visible()

    # ---------------------------- Hotel scoping --------------------------- #
    def select_hotel(self, hotel_option_value: str) -> None:
        self.page.get_by_role("combobox").first.select_option(hotel_option_value)

    def select_first_hotel(self) -> None:
        """Every toolbar action (Add Staff / Add Role / Filter) is gated
        behind a hotel being selected in the scoping combobox — the module
        starts with none selected. Index 0 is normally a disabled
        placeholder ("Select a hotel"), so this picks the first real
        option."""
        self.page.get_by_role("combobox").first.select_option(index=1)
        # Give the staff table a moment to refetch for the newly selected
        # hotel before any toolbar button is asserted/clicked.
        expect(self.page.get_by_role("button", name="Add Staff")).to_be_visible()

    # ---------------------------- Roles ------------------------------------ #
    def click_add_role(self) -> None:
        self.page.get_by_role("button", name="Add Role").click()
        expect(self.page.get_by_role("heading", name="Add Role")).to_be_visible()

    def name_role(self, role_name: str) -> None:
        self.page.get_by_role("textbox").nth(1).click()
        self.page.get_by_role("textbox").nth(1).fill(role_name)

    def toggle_permission(self, module_name: str) -> None:
        self.page.get_by_role("switch", name=module_name).click()

    def toggle_permissions(self, module_names: Iterable[str]) -> None:
        for module_name in module_names:
            self.toggle_permission(module_name)

    def submit_role(self) -> None:
        self.page.get_by_role("button", name="Create Role").click()

    def add_role(self, role_name: str, modules: Iterable[str]) -> None:
        self.click_add_role()
        self.name_role(role_name)
        self.toggle_permissions(modules)
        self.submit_role()

    # ---------------------------- Add staff --------------------------------- #
    def click_add_staff(self) -> None:
        self.page.get_by_role("button", name="Add Staff").click()
        expect(self.page.get_by_role("heading", name="Add Staff")).to_be_visible()

    def fill_staff_form(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        password: str,
        role_option_value: str,
        department: str = "All",
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
        # index 3 assumes: [0] hotel-scoping combobox (behind the modal),
        # [1]/[2] any comboboxes inside the modal above this one, [3] role.
        # Unverified against live DOM for this modal specifically — recheck
        # with `PWDEBUG=1 pytest tests/test_staff.py::test_add_staff_happy_path`
        # if this still resolves to the wrong <select>.
        self.page.get_by_role("combobox").nth(3).select_option(role_option_value)
        self.page.locator('input[name="department"]').click()
        self.page.locator('input[name="department"]').fill(department)

    def submit_add_staff(self) -> None:
        self.page.get_by_role("button", name="Add Staff").nth(1).click()

    def add_staff(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        password: str,
        role_option_value: str,
        department: str = "All",
    ) -> None:
        self.click_add_staff()
        self.fill_staff_form(first_name, last_name, email, phone, password, role_option_value, department)
        self.submit_add_staff()

    def set_phone_number(self, phone: str) -> None:
        self.page.get_by_role("textbox", name="8012345678").click()
        self.page.get_by_role("textbox", name="8012345678").fill(phone)

    # ---------------------------- Edit staff --------------------------------- #
    def open_row_actions(self, row_name_pattern: str) -> None:
        self.row(row_name_pattern).first.get_by_role("button").last.click()

    def edit_staff(self, row_name_pattern: str, phone: str | None = None) -> None:
        self.open_row_actions(row_name_pattern)
        self.page.get_by_role("button", name="Edit").click()
        expect(self.page.get_by_role("heading", name="Edit Staff")).to_be_visible()
        if phone:
            self.set_phone_number(phone)
        self.page.get_by_role("button", name="Update").click()

    # ---------------------------- Filter by status --------------------------- #
    def filter_by_status(self, status: str) -> None:
        """status: 'ACTIVE' or 'INACTIVE'."""
        self.open_filter()
        self.select_filter_combobox(status, index=1)
        self.apply_filter()
