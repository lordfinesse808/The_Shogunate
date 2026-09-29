"""LoginPage - /login"""
from __future__ import annotations

from playwright.sync_api import Page, expect

from config import BASE_URL
from pages.base_page import BasePage


class LoginPage(BasePage):
    URL = f"{BASE_URL}/login"

    def __init__(self, page: Page):
        super().__init__(page)

    def goto(self) -> "LoginPage":
        self.page.goto(self.URL)
        return self

    def expect_loaded(self) -> None:
        expect(self.page.get_by_role("img", name="Oneflare HMS")).to_be_visible()

    @property
    def email_input(self):
        return self.page.get_by_role("textbox", name="admin@oneflare.com")

    @property
    def password_input(self):
        return self.page.get_by_role("textbox", name="••••••••")

    @property
    def sign_in_button(self):
        return self.page.get_by_role("button", name="Sign In")

    def login(self, email: str, password: str) -> None:
        self.email_input.click()
        self.email_input.fill(email)
        self.password_input.click()
        self.password_input.fill(password)
        self.sign_in_button.click()

    def expect_login_error_visible(self) -> None:
        expect(self.page.get_by_text("Invalid")).to_be_visible()
