"""
PersonForm - a *component object*.

"Add Staff" (Staff module) and "Add Admin" (Admin & Roles module) render the
same block of fields: first name, last name, email, phone, password. Instead
of copy-pasting ten lines of locators into both page objects, the block is
modelled once here and each page object *has a* PersonForm.

Rule of thumb: page object = a screen, component object = a piece of UI that
appears on several screens (a form section, a date picker, a data table).
"""
from __future__ import annotations

from playwright.sync_api import Page

# The phone field has no `name` attribute; its accessible name comes from
# the placeholder text shown in the empty input.
PHONE_PLACEHOLDER = "8012345678"


class PersonForm:
    def __init__(self, page: Page):
        self.first_name_input = page.locator('input[name="firstName"]')
        self.last_name_input = page.locator('input[name="lastName"]')
        self.email_input = page.locator('input[name="email"]')
        self.phone_input = page.get_by_role("textbox", name=PHONE_PLACEHOLDER)
        self.password_input = page.locator('input[name="password"]')

    def fill(self, first_name: str, last_name: str, email: str, phone: str, password: str) -> None:
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.email_input.fill(email)
        self.phone_input.fill(phone)
        self.password_input.fill(password)

    def set_phone(self, phone: str) -> None:
        self.phone_input.fill(phone)
