"""LoginPage - /login"""
from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    # Relative: resolved against the context's base_url (see conftest.py).
    PATH = "/login"

    def __init__(self, page: Page):
        super().__init__(page)
        self.logo = page.get_by_role("img", name="Oneflare HMS")
        # The inputs have no <label>; their accessible names come from the
        # placeholder text ("admin@oneflare.com" and eight bullet characters).
        self.email_input = page.get_by_role("textbox", name="admin@oneflare.com")
        self.password_input = page.get_by_role("textbox", name="••••••••")
        self.sign_in_button = page.get_by_role("button", name="Sign In")

    def goto(self) -> LoginPage:
        self.page.goto(self.PATH)
        return self

    def expect_loaded(self) -> None:
        expect(self.logo).to_be_visible()
        expect(self.sign_in_button).to_be_visible()

    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.sign_in_button.click()

    def expect_still_on_login(self) -> None:
        """A rejected login must not navigate away from /login."""
        expect(self.page).to_have_url(re.compile(r"/login"))
        expect(self.sign_in_button).to_be_visible()
