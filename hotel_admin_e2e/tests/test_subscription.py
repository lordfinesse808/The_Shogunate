"""Subscription module tests. Maps to TC-HA008..TC-HA012 and TC-HA039..TC-HA041."""
import pytest

from pages.subscription_page import SubscriptionPage
from test_data import (
    DURATION_OPTION_FOR_SUBSCRIPTION_EDIT,
    EXISTING_SUBSCRIPTION_ROW,
    PACKAGE_OPTION_FOR_SUBSCRIPTION_EDIT,
)


@pytest.mark.smoke
def test_subscription_page_loads(subscription_page: SubscriptionPage) -> None:
    # The fixture already ran expect_loaded(); asserting again keeps the
    # test self-explanatory when read on its own.
    subscription_page.expect_loaded()


@pytest.mark.regression
@pytest.mark.testcase("TC-HA039")
def test_edit_existing_subscription(subscription_page: SubscriptionPage) -> None:
    """TC-HA039 - Editing an Existing Subscription Record."""
    subscription_page.edit_subscription(
        EXISTING_SUBSCRIPTION_ROW,
        package_option_value=PACKAGE_OPTION_FOR_SUBSCRIPTION_EDIT,
        duration_option_value=DURATION_OPTION_FOR_SUBSCRIPTION_EDIT,
    )
    subscription_page.expect_row_visible(EXISTING_SUBSCRIPTION_ROW)


@pytest.mark.regression
@pytest.mark.testcase("TC-HA041")
def test_switch_between_subscriptions_and_packages_views(subscription_page: SubscriptionPage) -> None:
    """TC-HA041 - Switching Between Subscriptions and Packages Views."""
    subscription_page.switch_view("Packages")
    subscription_page.expect_row_visible(EXISTING_SUBSCRIPTION_ROW)

    subscription_page.search(EXISTING_SUBSCRIPTION_ROW)
    subscription_page.expect_row_visible(EXISTING_SUBSCRIPTION_ROW)
    subscription_page.clear_search()


@pytest.mark.regression
@pytest.mark.destructive
@pytest.mark.testcase("TC-HA040")
def test_delete_subscription(subscription_page: SubscriptionPage) -> None:
    """TC-HA040 - Deleting a Subscription Record.

    Removes EXISTING_SUBSCRIPTION_ROW permanently - hence `destructive`.
    """
    subscription_page.search(EXISTING_SUBSCRIPTION_ROW)
    subscription_page.delete_subscription(EXISTING_SUBSCRIPTION_ROW)
    subscription_page.expect_row_absent(EXISTING_SUBSCRIPTION_ROW)
