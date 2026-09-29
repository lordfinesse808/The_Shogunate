"""DashboardPage - landing page after login, shows platform-wide KPIs,
charts and summary tables described in PRD section 2.1."""
from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage

KPI_LABELS = (
    "Total Hotels",
    "Total Earnings (USD)",
    "Total Earnings (NGN)",
    "Total Transaction Count",
)
CHART_HEADINGS = (
    "Subscription Trends",
    "Hotel Activity",
    "Earnings Over Time",
)
ACTIVITY_TABLE_HEADINGS = (
    "Top Performing Hotels",
    "Recent Transactions",
)
SUBSCRIPTION_TABLE_HEADINGS = (
    "Hotels with Active Subscriptions",
    "Hotels with Inactive Subscriptions",
)


class DashboardPage(BasePage):
    PATH = "/dashboard"

    def __init__(self, page: Page):
        super().__init__(page)
        self.top_performing_heading = page.get_by_role("heading", name="Top Performing Hotels")

    def expect_loaded(self) -> None:
        """Checks the URL first: `get_by_role("img", name="Oneflare")` used
        to also match the login screen's "Oneflare HMS" logo (partial name
        match), so that assertion could pass while still sitting on /login
        mid-redirect. Confirming the route, then a heading that only exists
        on the Dashboard, removes that ambiguity."""
        expect(self.page).to_have_url(re.compile(r"/dashboard"))
        expect(self.top_performing_heading).to_be_visible()

    # ---------------------------- KPIs ------------------------------- #
    def expect_kpis_visible(self, labels: tuple[str, ...] = KPI_LABELS) -> None:
        for label in labels:
            expect(self.page.get_by_text(label)).to_be_visible()

    # ------------------------ Charts & tables ------------------------ #
    def expect_headings_visible(self, headings: tuple[str, ...]) -> None:
        """Charts and tables are identified by their section heading - the
        canvas/SVG inside has no stable accessible name."""
        for heading in headings:
            expect(self.page.get_by_role("heading", name=heading)).to_be_visible()

    def expect_charts_visible(self) -> None:
        self.expect_headings_visible(CHART_HEADINGS)

    def expect_activity_tables_visible(self) -> None:
        self.expect_headings_visible(ACTIVITY_TABLE_HEADINGS)

    def expect_subscription_tables_visible(self) -> None:
        self.expect_headings_visible(SUBSCRIPTION_TABLE_HEADINGS)

    def expect_chart_legend_item_visible(self, package_name: str) -> None:
        expect(self.page.get_by_text(package_name, exact=True).first).to_be_visible()
