"""
Shared pytest fixtures for the Oneflare Hotel Admin Backend E2E suite.

Fixture chain:
    page (from pytest-playwright)
        -> logged_in_page   (navigates to /login, signs in as Super Admin)
            -> dashboard_page / admin_management_page / subscription_page /
               notification_page / staff_page / reports_page / logs_page /
               admin_roles_page   (one per module, all sharing the same
               authenticated `page`)

Every test therefore only asks for the page object(s) it needs; fixtures
guarantee it starts from an authenticated session already on the Dashboard.
"""
import pytest
from playwright.sync_api import Page, expect

from config import DEFAULT_TIMEOUT_MS, NAV_TIMEOUT_MS, SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD
from pages.admin_management_page import AdminManagementPage
from pages.admin_roles_page import AdminRolesPage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.logs_page import LogsPage
from pages.notification_page import NotificationPage
from pages.reports_page import ReportsPage
from pages.staff_page import StaffPage
from pages.subscription_page import SubscriptionPage


@pytest.fixture(scope="session", autouse=True)
def _configure_default_timeouts():
    """
    IMPORTANT: `page.set_default_timeout()` only affects *actions*
    (click/fill/etc.) and locator resolution — it does NOT change the
    default timeout used by web-first `expect(...)` assertions, which is
    5000ms regardless of that setting. Under real network/server latency
    (e.g. a slower login redirect) that 5s budget is what was causing
    "still on /login" / "still on Dashboard" flakiness in expect_loaded()
    calls across pages. This aligns both to the same configured value.
    """
    expect.set_default_timeout(DEFAULT_TIMEOUT_MS)


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """Authenticate as Super Admin and land on the Dashboard."""
    page.set_default_navigation_timeout(NAV_TIMEOUT_MS)
    login_page = LoginPage(page)
    login_page.goto()
    login_page.expect_loaded()
    login_page.login(SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD)

    # Wait for the actual SPA route change rather than relying solely on
    # expect() polling — the app shows a "Welcome back" toast slightly
    # before the client-side redirect completes.
    page.wait_for_url("**/dashboard", timeout=NAV_TIMEOUT_MS)

    dashboard = DashboardPage(page)
    dashboard.expect_loaded()
    return page


@pytest.fixture
def dashboard_page(logged_in_page: Page) -> DashboardPage:
    return DashboardPage(logged_in_page)


@pytest.fixture
def admin_management_page(logged_in_page: Page) -> AdminManagementPage:
    page_obj = AdminManagementPage(logged_in_page)
    page_obj.goto()
    page_obj.expect_loaded()
    return page_obj


@pytest.fixture
def subscription_page(logged_in_page: Page) -> SubscriptionPage:
    DashboardPage(logged_in_page).open_nav_link("Subscription")
    page_obj = SubscriptionPage(logged_in_page)
    page_obj.expect_loaded()
    return page_obj


@pytest.fixture
def notification_page(logged_in_page: Page) -> NotificationPage:
    DashboardPage(logged_in_page).open_nav_link("Notification")
    page_obj = NotificationPage(logged_in_page)
    page_obj.expect_loaded()
    return page_obj


@pytest.fixture
def staff_page(logged_in_page: Page) -> StaffPage:
    DashboardPage(logged_in_page).open_nav_link("Staff")
    page_obj = StaffPage(logged_in_page)
    page_obj.expect_loaded()
    # The Staff module's toolbar (Add Staff / Add Role / Filter) only
    # renders once a hotel is selected in the scoping combobox — every
    # Staff test in the failing run timed out waiting for those buttons
    # because no hotel had been chosen yet.
    page_obj.select_first_hotel()
    return page_obj


@pytest.fixture
def reports_page(logged_in_page: Page) -> ReportsPage:
    DashboardPage(logged_in_page).open_nav_link("Reports")
    page_obj = ReportsPage(logged_in_page)
    page_obj.expect_loaded()
    return page_obj


@pytest.fixture
def logs_page(logged_in_page: Page) -> LogsPage:
    DashboardPage(logged_in_page).open_nav_link("Logs")
    page_obj = LogsPage(logged_in_page)
    page_obj.expect_loaded()
    return page_obj


@pytest.fixture
def admin_roles_page(logged_in_page: Page) -> AdminRolesPage:
    DashboardPage(logged_in_page).open_nav_link("Admin & Roles")
    page_obj = AdminRolesPage(logged_in_page)
    page_obj.expect_loaded()
    return page_obj


# ---------------------------------------------------------------------- #
# Failure diagnostics                                                     #
# ---------------------------------------------------------------------- #
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """On any failing test, dump a screenshot + full accessibility snapshot
    to test-results/<test-name>/ so a locator mismatch (e.g. a button whose
    real accessible name differs from what a Page Object assumed) can be
    diagnosed from CI output alone, without re-running headed locally."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    page: Page = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
    if page is None:
        return

    out_dir = f"test-results/{item.name.replace('/', '_')}"
    import os

    os.makedirs(out_dir, exist_ok=True)
    try:
        page.screenshot(path=f"{out_dir}/failure.png", full_page=True)
        with open(f"{out_dir}/aria_snapshot.yaml", "w", encoding="utf-8") as f:
            f.write(page.locator("body").aria_snapshot())
        with open(f"{out_dir}/url.txt", "w", encoding="utf-8") as f:
            f.write(page.url)
    except Exception:
        pass  # best-effort diagnostics only; never mask the real failure
