"""DashboardPage - landing page after login, shows platform-wide KPIs,
charts and summary tables described in PRD section 2.1."""
from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from config import BASE_URL
from pages.base_page import BasePage


class DashboardPage(BasePage):
    URL = f"{BASE_URL}/dashboard"

    def __init__(self, page: Page):
        super().__init__(page)

    def expect_loaded(self) -> None:
        """Checks the URL first: `get_by_role("img", name="Oneflare")` used
        to also match the login screen's "Oneflare HMS" logo (partial name
        match), so this assertion could pass while still sitting on
        /login mid-redirect. Confirming the route, then a heading that only
        exists on the Dashboard, removes that ambiguity."""
        expect(self.page).to_have_url(re.compile(r"/dashboard"))
        expect(self.page.get_by_role("heading", name="Top Performing Hotels")).to_be_visible()

    # ---------------------------- KPIs ------------------------------- #
    def expect_kpi_visible(self, label_pattern) -> None:
        expect(self.page.locator("div").filter(has_text=label_pattern)).to_be_visible()

    def expect_total_hotels_visible(self) -> None:
        expect(self.page.get_by_text("Total Hotels")).to_be_visible()

    def expect_earnings_usd_visible(self) -> None:
        expect(self.page.get_by_text("Total Earnings (USD)")).to_be_visible()

    def expect_earnings_ngn_visible(self) -> None:
        expect(self.page.get_by_text("Total Earnings (NGN)")).to_be_visible()

    def expect_transaction_count_visible(self) -> None:
        expect(self.page.get_by_text("Total Transaction Count")).to_be_visible()

    # ---------------------------- Charts ------------------------------ #
    def expect_subscription_trends_chart_visible(self) -> None:
        expect(self.page.get_by_role("heading", name="Subscription Trends")).to_be_visible()

    def expect_hotel_activity_chart_visible(self) -> None:
        expect(self.page.get_by_role("heading", name="Hotel Activity")).to_be_visible()

    def expect_earnings_over_time_chart_visible(self) -> None:
        expect(self.page.get_by_role("heading", name="Earnings Over Time")).to_be_visible()

    def expect_chart_legend_item_visible(self, package_name: str) -> None:
        expect(self.page.get_by_text(package_name, exact=True)).to_be_visible()

    # ---------------------------- Tables ------------------------------ #
    def expect_top_performing_hotels_visible(self) -> None:
        expect(self.page.get_by_role("heading", name="Top Performing Hotels")).to_be_visible()

    def expect_recent_transactions_visible(self) -> None:
        expect(self.page.get_by_role("heading", name="Recent Transactions")).to_be_visible()

    def expect_active_subscriptions_table_visible(self) -> None:
        expect(self.page.get_by_role("heading", name="Hotels with Active Subscriptions")).to_be_visible()

    def expect_inactive_subscriptions_table_visible(self) -> None:
        expect(self.page.get_by_role("heading", name="Hotels with Inactive Subscriptions")).to_be_visible()
