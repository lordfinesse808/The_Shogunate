"""Logs module tests. Maps to TC-HA019..TC-HA022 and TC-HA055, TC-HA056."""
import pytest

from pages.logs_page import LogsPage
from test_data import SEARCHABLE_ADMIN_NAME


@pytest.mark.smoke
def test_logs_page_loads_with_hotel_logs_by_default(logs_page: LogsPage) -> None:
    logs_page.expect_row_visible("Staff Updated")


@pytest.mark.regression
@pytest.mark.testcase("TC-HA055")
def test_switch_between_hotel_logs_and_admin_logs(logs_page: LogsPage) -> None:
    """TC-HA055 - Switching Between Hotel Logs and Admin Logs."""
    logs_page.switch_to_admin_logs()
    logs_page.expect_row_visible("Update User")

    logs_page.switch_to_hotel_logs()
    logs_page.expect_row_visible("Staff Updated")


@pytest.mark.regression
@pytest.mark.testcase("TC-HA020")
def test_search_logs_by_keyword(logs_page: LogsPage) -> None:
    """TC-HA020 - Search and Filter (search variant)."""
    logs_page.switch_to_admin_logs()
    logs_page.search("sade")
    logs_page.expect_row_visible(SEARCHABLE_ADMIN_NAME)
    logs_page.clear_search()


@pytest.mark.regression
@pytest.mark.testcase("TC-HA056")
def test_filter_logs_by_action_type(logs_page: LogsPage) -> None:
    """TC-HA056 - Filtering Logs by Action Type."""
    logs_page.switch_to_admin_logs()
    logs_page.filter_by_action_type("UPDATE")
    logs_page.expect_row_visible("Update User")

    logs_page.open_filter()
    logs_page.clear_filter()


@pytest.mark.regression
@pytest.mark.testcase("TC-HA021")
def test_export_logs_downloads_file(logs_page: LogsPage) -> None:
    """TC-HA021 - Export Audit Logs (filtered to one action type first so
    the export is small and deterministic)."""
    logs_page.open_filter()
    logs_page.select_filter_combobox("CREATE:CURRENCY", index=1)
    logs_page.apply_filter()
    logs_page.expect_row_visible("Currency Added")

    download = logs_page.export()
    assert download.suggested_filename, "Export produced a download with no file name"
