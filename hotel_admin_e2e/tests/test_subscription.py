"""Subscription module tests. Maps to TC-HA008..TC-HA012 and TC-HA039..TC-HA041."""
import pytest

from pages.subscription_page import SubscriptionPage

EXISTING_SUBSCRIPTION_ROW = "diamond test"


@pytest.mark.smoke
def test_subscription_page_loads(subscription_page: SubscriptionPage) -> None:
    subscription_page.expect_loaded()


@pytest.mark.regression
def test_edit_existing_subscription(subscription_page: SubscriptionPage) -> None:
    """TC-HA039 - Editing an Existing Subscription Record."""
    subscription_page.edit_subscription(
        EXISTING_SUBSCRIPTION_ROW,
        package_option_value="7de4a9c8-8d9e-43ef-8f3e-0f144d2d83bb",
        duration_option_value="4675e063-e9e2-4fba-b062-a6482f79545a",
    )


@pytest.mark.regression
def test_switch_between_subscriptions_and_packages_views(subscription_page: SubscriptionPage) -> None:
    """TC-HA041 - Switching Between Subscriptions and Packages Views."""
    subscription_page.switch_view("PACKAGES")
    subscription_page.expect_row_visible("diamond test")

    subscription_page.search("pro")
    subscription_page.clear_search()


@pytest.mark.regression
def test_delete_subscription(subscription_page: SubscriptionPage) -> None:
    """TC-HA040 - Deleting a Subscription Record.

    Runs LAST in this file: it removes EXISTING_SUBSCRIPTION_ROW, which
    test_edit_existing_subscription above still depends on.
    """
    subscription_page.delete_subscription(EXISTING_SUBSCRIPTION_ROW)
