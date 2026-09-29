"""Authentication tests. Maps to TC-HA001 (RBAC) / TC-HA002 (2FA)."""
import pytest
from playwright.sync_api import Page

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


@pytest.mark.smoke
@pytest.mark.testcase("TC-HA001")
def test_super_admin_can_log_in(page: Page, super_admin_credentials: tuple[str, str]) -> None:
    login_page = LoginPage(page).goto()
    login_page.expect_loaded()

    login_page.login(*super_admin_credentials)

    DashboardPage(page).expect_loaded()


@pytest.mark.regression
@pytest.mark.testcase("TC-HA001")
def test_login_rejects_invalid_credentials(page: Page) -> None:
    login_page = LoginPage(page).goto()
    login_page.expect_loaded()

    login_page.login("not-a-real-admin@maildrop.cc", "WrongPassword!")

    login_page.expect_still_on_login()
