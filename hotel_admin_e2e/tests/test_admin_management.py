"""
Hotel Management tests (Admin Mgt module).
Maps to TC-HA004..TC-HA007 and TC-HA033..TC-HA038.

NOTE: several flows here (edit/deactivate/delete/renew/change-subscription)
mutate real records. `existing_hotel_row` is a placeholder pattern that
should be swapped for a hotel created by a setup fixture (or a dedicated
seeded "QA Test Hotel") before these run against a shared environment.

Test order is deliberate: non-destructive checks run first, deactivate is
immediately paired with reactivate so the row is left in its original
state, and the password-gated delete runs LAST since it removes the row
every earlier test in this file depends on.
"""
import pytest

from pages.admin_management_page import AdminManagementPage

EXISTING_HOTEL_ROW = "Finesse inc"  # substring used to locate a stable seed row


@pytest.mark.smoke
def test_admin_mgt_loads_with_hotel_table(admin_management_page: AdminManagementPage) -> None:
    admin_management_page.expect_table_headers_visible()


@pytest.mark.regression
def test_edit_hotel_business_details(admin_management_page: AdminManagementPage) -> None:
    """TC-HA033 - Editing Hotel Business Details."""
    admin_management_page.edit_hotel(EXISTING_HOTEL_ROW, address="40 Akin Str, By Kil")
    admin_management_page.expect_row_visible(EXISTING_HOTEL_ROW)


@pytest.mark.regression
def test_hotel_list_search_and_pagination(admin_management_page: AdminManagementPage) -> None:
    """TC-HA036 - Search and Pagination on Hotel List."""
    admin_management_page.search(EXISTING_HOTEL_ROW)
    admin_management_page.expect_row_visible(EXISTING_HOTEL_ROW)

    admin_management_page.clear_search()
    admin_management_page.set_rows_per_page(15)
    admin_management_page.expect_table_headers_visible()


@pytest.mark.regression
def test_renew_subscription_from_hotel_record(admin_management_page: AdminManagementPage) -> None:
    """TC-HA037 - Renew Subscription from Hotel Record."""
    admin_management_page.renew_subscription(EXISTING_HOTEL_ROW, duration_option_value="1")


@pytest.mark.regression
def test_change_subscription_package_and_duration(admin_management_page: AdminManagementPage) -> None:
    """TC-HA038 - Change Subscription Package/Duration for a Hotel."""
    admin_management_page.change_subscription(
        EXISTING_HOTEL_ROW,
        duration_option_value="6",
        package_option_value="3713f129-a6f3-4ce8-942b-883ad97e6e29",
    )


@pytest.mark.regression
def test_deactivate_then_reactivate_hotel(admin_management_page: AdminManagementPage) -> None:
    """TC-HA006 - Deactivating a Business, and TC-HA034 - Reactivating a
    Deactivated Hotel. Paired in one test so the row is left Active again
    for any test that runs after it."""
    admin_management_page.deactivate_hotel(EXISTING_HOTEL_ROW)
    admin_management_page.reactivate_hotel(EXISTING_HOTEL_ROW)


@pytest.mark.regression
def test_delete_hotel_requires_password_confirmation(admin_management_page: AdminManagementPage) -> None:
    """TC-HA035 - Delete Hotel Requires Password Confirmation (also
    exercises TC-HA007's soft-delete acceptance criteria).

    Runs LAST in this file: it removes EXISTING_HOTEL_ROW, which every
    other test above depends on still being present.
    """
    from config import SUPER_ADMIN_PASSWORD

    admin_management_page.delete_hotel(EXISTING_HOTEL_ROW, SUPER_ADMIN_PASSWORD)
