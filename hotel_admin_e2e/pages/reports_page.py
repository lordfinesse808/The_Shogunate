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

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class ReportType:
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
    def __init__(self, page: Page):
        super().__init__(page)

    def expect_loaded(self) -> None:
        expect(self.page.get_by_role("heading", name="Reports")).to_be_visible()

    def select_report(self, report_type: str) -> None:
        self.page.get_by_role("button", name=report_type, exact=True).click()

    def expect_report_heading(self, report_type: str) -> None:
        expect(self.page.get_by_role("heading", name=report_type)).to_be_visible()

    # ---------------------------- Date range ------------------------------- #
    @property
    def from_date_input(self):
        return self.page.get_by_role("textbox").nth(0)

    @property
    def to_date_input(self):
        return self.page.get_by_role("textbox").nth(1)

    def set_from_date(self, iso_date: str) -> None:
        self.from_date_input.fill(iso_date)

    def set_to_date(self, iso_date: str) -> None:
        self.to_date_input.fill(iso_date)

    def clear_date_range(self) -> None:
        self.page.get_by_role("button", name="Clear").click()

    # ---------------------------- Totals / summary --------------------------- #
    def expect_total_visible(self) -> None:
        expect(self.page.get_by_text("total", exact=False)).to_be_visible()

    def expect_summary_by_hotel_visible(self) -> None:
        expect(self.page.get_by_role("heading", name="Summary by Hotel")).to_be_visible()

    def click_visit_site(self) -> None:
        with self.page.context.expect_page() as new_page_info:
            self.page.get_by_role("link", name="Visit site").click()
        return new_page_info.value
