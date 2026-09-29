"""Dashboard KPI/chart/table tests. Maps to TC-HA003 and TC-HA060."""
import pytest

from pages.dashboard_page import DashboardPage


@pytest.mark.smoke
@pytest.mark.testcase("TC-HA003")
def test_dashboard_kpis_load(dashboard_page: DashboardPage) -> None:
    """TC-HA003 - Dashboard KPIs and Metrics Load."""
    dashboard_page.expect_kpis_visible()


@pytest.mark.regression
@pytest.mark.testcase("TC-HA003")
def test_dashboard_charts_are_visible(dashboard_page: DashboardPage) -> None:
    """TC-HA003 - charts for subscription trends, hotel activity and
    earnings over time render alongside the KPI tiles."""
    dashboard_page.expect_charts_visible()


@pytest.mark.regression
@pytest.mark.testcase("TC-HA060")
def test_top_performing_hotels_and_recent_transactions_visible(dashboard_page: DashboardPage) -> None:
    """TC-HA060 - Verifying Chart Legends and Top Performing Hotels Table."""
    dashboard_page.expect_activity_tables_visible()


@pytest.mark.regression
def test_subscription_summary_tables_visible(dashboard_page: DashboardPage) -> None:
    """PRD 2.1 - Hotels with active/inactive subscriptions summary tables."""
    dashboard_page.expect_subscription_tables_visible()
