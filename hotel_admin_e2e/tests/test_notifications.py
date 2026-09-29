"""Notification module tests. Maps to TC-HA013, TC-HA014, TC-HA042..TC-HA044."""
import pytest

from pages.notification_page import NotificationPage


@pytest.mark.regression
def test_create_targeted_notification_for_all_hotels(notification_page: NotificationPage) -> None:
    """TC-HA042 - Creating a Targeted Notification with Hotel Selection
    (also exercises TC-HA013's platform-wide announcement flow)."""
    notification_page.add_notification(
        title="SOS Evacuation",
        notification_type="MAINTENANCE",
        message="This is not a drill evacuate all buildings immediately",
        media_type="NONE",
        start_date="2026-09-26",
        end_date="2026-09-27",
    )
    notification_page.expect_row_visible("SOS Evacuation")


@pytest.mark.regression
def test_view_notification_details(notification_page: NotificationPage) -> None:
    """TC-HA043 - Viewing Notification Details."""
    notification_page.open_notification("Staff Payment Reminder")
    notification_page.expect_details_visible("Staff Payment Reminder")
    notification_page.close_details()


@pytest.mark.regression
def test_notification_list_pagination(notification_page: NotificationPage) -> None:
    """TC-HA044 - Notification List Pagination."""
    notification_page.set_rows_per_page(15)
    notification_page.go_to_page(1)
