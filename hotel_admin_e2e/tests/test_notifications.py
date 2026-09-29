"""Notification module tests. Maps to TC-HA013, TC-HA014, TC-HA042..TC-HA044."""
import pytest
from playwright.sync_api import expect

from pages.notification_page import NotificationPage
from test_data import EXISTING_NOTIFICATION_TITLE, iso_date, unique_suffix


@pytest.mark.regression
@pytest.mark.testcase("TC-HA042")
@pytest.mark.testcase("TC-HA013")
def test_create_targeted_notification_for_all_hotels(notification_page: NotificationPage) -> None:
    """TC-HA042 - Creating a Targeted Notification with Hotel Selection
    (also exercises TC-HA013's platform-wide announcement flow)."""
    title = f"SOS Evacuation {unique_suffix()}"
    notification_page.add_notification(
        title=title,
        notification_type="MAINTENANCE",
        message="This is not a drill evacuate all buildings immediately",
        media_type="NONE",
        start_date=iso_date(0),
        end_date=iso_date(1),
    )
    notification_page.search(title)
    notification_page.expect_row_visible(title)


@pytest.mark.regression
@pytest.mark.testcase("TC-HA043")
def test_view_notification_details(notification_page: NotificationPage) -> None:
    """TC-HA043 - Viewing Notification Details."""
    notification_page.open_notification(EXISTING_NOTIFICATION_TITLE)
    notification_page.expect_details_visible(EXISTING_NOTIFICATION_TITLE)
    notification_page.close_details()


@pytest.mark.regression
@pytest.mark.testcase("TC-HA044")
def test_notification_list_pagination(notification_page: NotificationPage) -> None:
    """TC-HA044 - Notification List Pagination."""
    notification_page.set_rows_per_page(15)
    expect(notification_page.rows_per_page_input).to_have_value("15")

    notification_page.go_to_page(1)
    expect(notification_page.go_to_page_input).to_have_value("1")
