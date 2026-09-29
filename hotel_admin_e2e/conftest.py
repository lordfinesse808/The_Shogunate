"""
Shared pytest fixtures for the Oneflare Hotel Admin Backend E2E suite.

Fixture chain:
    page (from pytest-playwright, one fresh browser context per test)
        -> logged_in_page   (navigates to /login, signs in as Super Admin)
            -> dashboard_page / admin_management_page / subscription_page /
               notification_page / staff_page / reports_page / logs_page /
               admin_roles_page   (one per module, all sharing the same
               authenticated `page`)

Every test therefore only asks for the page object(s) it needs; fixtures
guarantee it starts from an authenticated session already on that module.
"""
from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import pytest
from playwright.sync_api import Page, expect

from config import (
    BASE_URL,
    DEFAULT_TIMEOUT_MS,
    NAV_TIMEOUT_MS,
    SUPER_ADMIN_EMAIL,
    SUPER_ADMIN_PASSWORD,
)
from pages.admin_management_page import AdminManagementPage
from pages.admin_roles_page import AdminRolesPage
from pages.base_page import BasePage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.logs_page import LogsPage
from pages.notification_page import NotificationPage
from pages.reports_page import ReportsPage
from pages.staff_page import StaffPage
from pages.subscription_page import SubscriptionPage

PageObject = TypeVar("PageObject", bound=BasePage)


# --------------------------------------------------------------------------- #
# Global Playwright configuration                                              #
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session", autouse=True)
def _configure_expect_timeout() -> None:
    """`page.set_default_timeout()` only covers *actions* (click/fill/...);
    web-first `expect(...)` assertions have their own 5s default. Align the
    assertion budget with the action budget once for the whole session.

    (The Drive version called `expect.set_default_timeout()`, which does not
    exist in the Python API - it raised AttributeError and errored every
    test during setup. `expect.set_options(timeout=...)` is the real call.)
    """
    expect.set_options(timeout=DEFAULT_TIMEOUT_MS)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """Give every browser context a base URL so page objects can navigate
    with relative paths (`page.goto("/login")`). A `--base-url` passed on
    the command line still wins because it is unpacked last."""
    return {"base_url": BASE_URL, **browser_context_args}


@pytest.fixture(autouse=True)
def _configure_page_timeouts(page: Page) -> None:
    """Set per-page timeouts once, here, instead of as a hidden side effect
    of constructing every page object."""
    page.set_default_timeout(DEFAULT_TIMEOUT_MS)
    page.set_default_navigation_timeout(NAV_TIMEOUT_MS)


@pytest.fixture(scope="session")
def super_admin_credentials() -> tuple[str, str]:
    if not (SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASSWORD):
        pytest.fail(
            "Set HMS_SUPER_ADMIN_EMAIL and HMS_SUPER_ADMIN_PASSWORD before running the suite.",
            pytrace=False,
        )
    return SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD


# --------------------------------------------------------------------------- #
# Authentication                                                               #
# --------------------------------------------------------------------------- #
@pytest.fixture
def logged_in_page(page: Page, super_admin_credentials: tuple[str, str]) -> Page:
    """Authenticate as Super Admin and land on the Dashboard."""
    login_page = LoginPage(page)
    login_page.goto()
    login_page.expect_loaded()
    login_page.login(*super_admin_credentials)

    # Wait for the actual SPA route change rather than relying solely on
    # expect() polling - the app shows a "Welcome back" toast slightly
    # before the client-side redirect completes.
    page.wait_for_url("**/dashboard")
    DashboardPage(page).expect_loaded()
    return page


# --------------------------------------------------------------------------- #
# One fixture per sidebar module                                               #
# --------------------------------------------------------------------------- #
def _open_module(page: Page, nav_link: str, page_class: type[PageObject]) -> PageObject:
    """Click a sidebar link, build the matching page object and prove the
    module rendered before a test is allowed to touch it."""
    DashboardPage(page).open_nav_link(nav_link)
    page_obj = page_class(page)
    page_obj.expect_loaded()
    return page_obj


@pytest.fixture
def dashboard_page(logged_in_page: Page) -> DashboardPage:
    return DashboardPage(logged_in_page)


@pytest.fixture
def admin_management_page(logged_in_page: Page) -> AdminManagementPage:
    return _open_module(logged_in_page, "Admin Mgt", AdminManagementPage)


@pytest.fixture
def subscription_page(logged_in_page: Page) -> SubscriptionPage:
    return _open_module(logged_in_page, "Subscription", SubscriptionPage)


@pytest.fixture
def notification_page(logged_in_page: Page) -> NotificationPage:
    return _open_module(logged_in_page, "Notification", NotificationPage)


@pytest.fixture
def staff_page(logged_in_page: Page) -> StaffPage:
    page_obj = _open_module(logged_in_page, "Staff", StaffPage)
    # The Staff toolbar (Add Staff / Add Role / Filter) only renders once a
    # hotel is chosen in the scoping combobox.
    page_obj.select_first_hotel()
    return page_obj


@pytest.fixture
def reports_page(logged_in_page: Page) -> ReportsPage:
    return _open_module(logged_in_page, "Reports", ReportsPage)


@pytest.fixture
def logs_page(logged_in_page: Page) -> LogsPage:
    return _open_module(logged_in_page, "Logs", LogsPage)


@pytest.fixture
def admin_roles_page(logged_in_page: Page) -> AdminRolesPage:
    return _open_module(logged_in_page, "Admin & Roles", AdminRolesPage)


# --------------------------------------------------------------------------- #
# Failure diagnostics                                                          #
# --------------------------------------------------------------------------- #
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """On any failing test, dump a screenshot + full accessibility snapshot
    to test-results/<test-name>/ so a locator mismatch (e.g. a button whose
    real accessible name differs from what a Page Object assumed) can be
    diagnosed from CI output alone, without re-running headed locally."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    page: Page | None = item.funcargs.get("page")
    if page is None:
        return

    out_dir = Path("test-results") / item.name.replace("/", "_")
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=out_dir / "failure.png", full_page=True)
        (out_dir / "aria_snapshot.yaml").write_text(page.locator("body").aria_snapshot(), encoding="utf-8")
        (out_dir / "url.txt").write_text(page.url, encoding="utf-8")
    except Exception:
        pass  # best-effort diagnostics only; never mask the real failure
