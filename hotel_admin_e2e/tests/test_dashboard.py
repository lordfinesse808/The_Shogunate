"""Dashboard KPI/chart/table tests. Maps to TC-HA003 and TC-HA060."""
import pytest

from pages.dashboard_page import DashboardPage


@pytest.mark.smoke
def test_dashboard_kpis_load(dashboard_page: DashboardPage) -> None:
    """TC-HA003 - Dashboard KPIs and Metrics Load."""
    dashboard_page.expect_total_hotels_visible()
    dashboard_page.expect_earnings_usd_visible()
    dashboard_page.expect_earnings_ngn_visible()
    dashboard_page.expect_transaction_count_visible()


@pytest.mark.regression
def test_dashboard_charts_are_visible(dashboard_page: DashboardPage) -> None:
    """TC-HA003 - charts for subscription trends, hotel activity and
    earnings over time render alongside the KPI tiles."""
    dashboard_page.expect_subscription_trends_chart_visible()
    dashboard_page.expect_hotel_activity_chart_visible()
    dashboard_page.expect_earnings_over_time_chart_visible()


@pytest.mark.regression
def test_top_performing_hotels_and_recent_transactions_visible(dashboard_page: DashboardPage) -> None:
    """TC-HA060 - Verifying Chart Legends and Top Performing Hotels Table."""
    dashboard_page.expect_top_performing_hotels_visible()
    dashboard_page.expect_recent_transactions_visible()


@pytest.mark.regression
def test_subscription_summary_tables_visible(dashboard_page: DashboardPage) -> None:
    """PRD 2.1 - Hotels with active/inactive subscriptions summary tables."""
    dashboard_page.expect_active_subscriptions_table_visible()
    dashboard_page.expect_inactive_subscriptions_table_visible()
