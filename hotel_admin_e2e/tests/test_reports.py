"""
Reports module tests.
Maps to TC-HA015..TC-HA018 and TC-HA049..TC-HA054.

One parametrised smoke test sanity-checks that every report type in the
PRD (2.6 A-J) renders; dedicated regression tests then dig into the
filter/search/export behaviour that is unique to a handful of reports.
"""
import pytest

from pages.reports_page import ReportsPage, ReportType

ALL_REPORT_TYPES = [
    ReportType.TRANSACTION,
    ReportType.PURCHASE,
    ReportType.SUBSCRIPTION,
    ReportType.RESERVATION,
    ReportType.BOOKING,
    ReportType.WAREHOUSE,
    ReportType.CHECK_IN_CHECK_OUT,
    ReportType.INVENTORY,
    ReportType.WEBSITE,
    ReportType.OCCUPANCY,
    ReportType.QUOTATION,
]


@pytest.mark.smoke
@pytest.mark.parametrize("report_type", ALL_REPORT_TYPES)
def test_each_report_type_renders(reports_page: ReportsPage, report_type: str) -> None:
    reports_page.select_report(report_type)
    reports_page.expect_report_heading(report_type)


@pytest.mark.regression
def test_transaction_report_export_downloads_file(reports_page: ReportsPage) -> None:
    """TC-HA015 / TC-HA016 - Transaction Report generation + export."""
    reports_page.select_report(ReportType.TRANSACTION)
    reports_page.expect_summary_by_hotel_visible()
    download = reports_page.export()
    assert download.suggested_filename


@pytest.mark.regression
def test_purchase_report_filter_and_export(reports_page: ReportsPage) -> None:
    """TC-HA049 - Generate Purchase Report with Filter and Export."""
    reports_page.select_report(ReportType.PURCHASE)
    reports_page.search("metro")
    reports_page.open_filter()
    reports_page.select_filter_combobox("b6284536-4a23-42cf-8b2b-b4b084b342e7", index=0)
    reports_page.select_filter_combobox("PENDING", index=2)
    reports_page.apply_filter()
    reports_page.export()


@pytest.mark.regression
def test_reservation_report_date_range_and_clear(reports_page: ReportsPage) -> None:
    """TC-HA050 - Generate Reservation Report with Date Range and Clear Filter.

    NOTE: a "From" date filters to records dated *on/after* it, so a past
    date (e.g. 2026-01-26) never excludes today's records — that produced
    a false failure against real data. A From date safely beyond every
    seeded reservation is what actually proves the filter works.
    """
    reports_page.select_report(ReportType.RESERVATION)
    reports_page.set_from_date("2030-01-01")
    reports_page.expect_no_data()

    reports_page.clear_date_range()
    reports_page.expect_row_visible("RES2609256778")
    reports_page.export()


@pytest.mark.regression
def test_booking_report_visit_site_link(reports_page: ReportsPage) -> None:
    """TC-HA051 - Generate Booking Report and Visit Hotel Website Link."""
    reports_page.select_report(ReportType.BOOKING)
    reports_page.expect_summary_by_hotel_visible()
    new_tab = reports_page.click_visit_site()
    assert "hotel-plaza-preview" in new_tab.url


@pytest.mark.regression
def test_check_in_check_out_report_status_filter(reports_page: ReportsPage) -> None:
    """TC-HA052 - Generate Check-In/Check-Out Report Filtered by Status."""
    reports_page.select_report(ReportType.CHECK_IN_CHECK_OUT)
    reports_page.export()
    reports_page.open_filter()
    reports_page.select_filter_combobox("BOOKED", index=2)
    reports_page.apply_filter()


@pytest.mark.regression
def test_occupancy_report_export_and_pagination(reports_page: ReportsPage) -> None:
    """TC-HA053 - Generate Occupancy Report with Export and Pagination."""
    reports_page.select_report(ReportType.OCCUPANCY)
    reports_page.export()
    reports_page.next_page()


@pytest.mark.regression
def test_quotation_report_type_filter_and_counts(reports_page: ReportsPage) -> None:
    """TC-HA054 - Generate Quotation Report Filtered by Type with
    Approved/Declined counts."""
    reports_page.select_report(ReportType.QUOTATION)
    reports_page.expect_total_visible()
    reports_page.open_filter()
    reports_page.select_filter_combobox("test quotation", index=3)
    reports_page.apply_filter()


@pytest.mark.regression
def test_website_transaction_report(reports_page: ReportsPage) -> None:
    """TC-HA017 - Generate Website Transaction Report (Oneflare Earnings)."""
    reports_page.select_report(ReportType.WEBSITE)
    reports_page.expect_summary_by_hotel_visible()
