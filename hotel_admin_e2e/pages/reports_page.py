"""
ReportsPage - Reports module (PRD 2.6 "Reports").

All eleven report types (Transaction, Purchase, Subscription, Reservation,
Booking, Warehouse, Check-In/Check Out, Inventory, Website, Occupancy,
Quotation) share one layout: a "Report Types" button rail, a From/To date
range, a totals strip, a "Summary by Hotel" table, then the detail table
with the familiar search/filter/export/pagination footer. One Page Object
therefore covers all of them; tests select the report they need via
`select_report(...)`.
"""
from __future__ import annotations

from enum import Enum

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ReportType(str, Enum):
    """Button labels on the Report Types rail. Subclassing `str` lets a
    member be passed anywhere a plain string is expected."""

    TRANSACTION = "Transaction Report"
    PURCHASE = "Purchase Report"
    SUBSCRIPTION = "Subscription Report"
    RESERVATION = "Reservation Report"
    BOOKING = "Booking Report"
    WAREHOUSE = "Warehouse Report"
    CHECK_IN_CHECK_OUT = "Check-In/Check Out Report"
    INVENTORY = "Inventory Report"
    WEBSITE = "Website Report"
    OCCUPANCY = "Occupancy Report"
    QUOTATION = "Quotation Report"


class ReportsPage(BasePage):
    PATH = "/reports"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Reports")
        self.from_date_input = page.get_by_role("textbox").nth(0)
        self.to_date_input = page.get_by_role("textbox").nth(1)
        self.summary_by_hotel_heading = page.get_by_role("heading", name="Summary by Hotel")
        self.visit_site_link = page.get_by_role("link", name="Visit site")

    def expect_loaded(self) -> None:
        expect(self.heading).to_be_visible()

    def select_report(self, report_type: ReportType) -> None:
        self.page.get_by_role("button", name=report_type.value, exact=True).click()

    def expect_report_heading(self, report_type: ReportType) -> None:
        expect(self.page.get_by_role("heading", name=report_type.value)).to_be_visible()

    # ----------------------------- Date range -------------------------- #
    def set_from_date(self, iso_date: str) -> None:
        self.from_date_input.fill(iso_date)

    def set_to_date(self, iso_date: str) -> None:
        self.to_date_input.fill(iso_date)

    def clear_date_range(self) -> None:
        # Same "Clear" control the Filter popover uses.
        self.clear_filter()

    # --------------------------- Totals / summary ---------------------- #
    def expect_total_visible(self) -> None:
        # Several totals render on a report ("Total", "Total Amount", ...);
        # `.first` avoids a strict-mode violation - any one proves the strip.
        expect(self.page.get_by_text("total", exact=False).first).to_be_visible()

    def expect_summary_by_hotel_visible(self) -> None:
        expect(self.summary_by_hotel_heading).to_be_visible()

    def click_visit_site(self) -> Page:
        """The link opens a new tab. `context.expect_page()` must wrap the
        click so the new Page is captured; it is returned to the caller."""
        with self.page.context.expect_page() as new_page_info:
            self.visit_site_link.click()
        return new_page_info.value
