"""
StaffPage - Staff module (PRD 2.5 "Staff Management").

Covers: hotel-scoped staff table, role creation with page-level permission
switches, staff creation with client-side phone validation, staff editing
and status filtering.
"""
from __future__ import annotations

from collections.abc import Iterable

from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from pages.components.person_form import PersonForm

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
    PATH = "/staff"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Staff Management")
        self.hotel_scope_select = page.get_by_role("combobox").first

        # Add Staff: [0] toolbar button, [1] submit inside the modal.
        self.add_staff_button = page.get_by_role("button", name="Add Staff").nth(0)
        self.add_staff_submit = page.get_by_role("button", name="Add Staff").nth(1)
        self.add_staff_heading = page.get_by_role("heading", name="Add Staff")
        self.person_form = PersonForm(page)
        # Index 3 assumes: [0] hotel-scoping combobox (behind the modal),
        # [1]/[2] other comboboxes in the modal above this one, [3] role.
        # Unverified against the live DOM - if it picks the wrong <select>,
        # read test-results/<test>/aria_snapshot.yaml and adjust.
        self.staff_role_select = page.get_by_role("combobox").nth(3)

        self.add_role_button = page.get_by_role("button", name="Add Role")
        self.add_role_heading = page.get_by_role("heading", name="Add Role")
        self.role_name_input = page.get_by_role("textbox").nth(1)
        self.create_role_button = page.get_by_role("button", name="Create Role")

        self.edit_staff_heading = page.get_by_role("heading", name="Edit Staff")

    def expect_loaded(self) -> None:
        expect(self.heading).to_be_visible()

    # ---------------------------- Hotel scoping ------------------------ #
    def select_hotel(self, hotel_option_value: str) -> None:
        self.hotel_scope_select.select_option(hotel_option_value)

    def select_first_hotel(self) -> None:
        """Every toolbar action (Add Staff / Add Role / Filter) is gated
        behind a hotel being selected in the scoping combobox - the module
        starts with none selected. Index 0 is normally a disabled
        placeholder ("Select a hotel"), so this picks the first real
        option."""
        self.hotel_scope_select.select_option(index=1)
        # Proves the toolbar re-rendered for the chosen hotel.
        expect(self.add_staff_button).to_be_visible()

    # -------------------------------- Roles ---------------------------- #
    def add_role(self, role_name: str, modules: Iterable[str]) -> None:
        self.add_role_button.click()
        expect(self.add_role_heading).to_be_visible()
        self.role_name_input.fill(role_name)
        for module_name in modules:
            self.page.get_by_role("switch", name=module_name).click()
        self.create_role_button.click()
        expect(self.add_role_heading).to_be_hidden()

    # ------------------------------ Add staff -------------------------- #
    def open_add_staff(self) -> None:
        self.add_staff_button.click()
        expect(self.add_staff_heading).to_be_visible()

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
        self.person_form.fill(first_name, last_name, email, phone, password)
        self.staff_role_select.select_option(role_option_value)
        self.fill_input("department", department)

    def submit_add_staff(self) -> None:
        self.add_staff_submit.click()

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
        self.open_add_staff()
        self.fill_staff_form(first_name, last_name, email, phone, password, role_option_value, department)
        self.submit_add_staff()
        expect(self.add_staff_heading).to_be_hidden()

    def set_phone_number(self, phone: str) -> None:
        self.person_form.set_phone(phone)

    def expect_add_staff_dialog_open(self) -> None:
        """Used after an invalid submit: client-side validation must keep
        the dialog open."""
        expect(self.add_staff_heading).to_be_visible()

    # ------------------------------ Edit staff ------------------------- #
    def edit_staff(self, row_name_pattern: str, phone: str | None = None) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_button("Edit")
        expect(self.edit_staff_heading).to_be_visible()
        if phone:
            self.set_phone_number(phone)
        self.click_button("Update")
        expect(self.edit_staff_heading).to_be_hidden()

    # --------------------------- Filter by status ---------------------- #
    def filter_by_status(self, status: str) -> None:
        """status: 'ACTIVE' or 'INACTIVE'."""
        self.open_filter()
        self.select_filter_combobox(status, index=1)
        self.apply_filter()
