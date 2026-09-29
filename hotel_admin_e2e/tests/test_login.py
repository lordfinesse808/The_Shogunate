"""Authentication tests. Maps to TC-HA001 (RBAC) / TC-HA002 (2FA)."""
import pytest
from playwright.sync_api import Page

from config import SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


@pytest.mark.smoke
def test_super_admin_can_log_in(page: Page) -> None:
    login_page = LoginPage(page)
    login_page.goto()
    login_page.expect_loaded()

    login_page.login(SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD)

    dashboard = DashboardPage(page)
    dashboard.expect_loaded()


@pytest.mark.regression
def test_login_rejects_invalid_credentials(page: Page) -> None:
    login_page = LoginPage(page)
    login_page.goto()
    login_page.expect_loaded()

    login_page.login("not-a-real-admin@maildrop.cc", "WrongPassword!")

    # Should remain on /login - the Sign In control stays visible.
    login_page.expect_loaded()
