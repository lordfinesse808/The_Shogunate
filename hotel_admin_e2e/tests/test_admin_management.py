"""
Hotel Management tests (Admin Mgt module).
Maps to TC-HA004..TC-HA007 and TC-HA033..TC-HA038.

Several flows here (edit/deactivate/renew/change-subscription) mutate a real
seed hotel, and the delete test removes it for good - that one is marked
`destructive` and is deselected by default (see pytest.ini). Point
EXISTING_HOTEL_ROW in test_data.py at a disposable "QA Test Hotel" before
running against a shared environment.
"""
import pytest

from pages.admin_management_page import AdminManagementPage
from test_data import EXISTING_HOTEL_ROW, PACKAGE_OPTION_FOR_HOTEL_CHANGE


@pytest.mark.smoke
def test_admin_mgt_loads_with_hotel_table(admin_management_page: AdminManagementPage) -> None:
    admin_management_page.expect_table_headers_visible()


@pytest.mark.regression
@pytest.mark.testcase("TC-HA033")
def test_edit_hotel_business_details(admin_management_page: AdminManagementPage) -> None:
    """TC-HA033 - Editing Hotel Business Details."""
    admin_management_page.edit_hotel(EXISTING_HOTEL_ROW, address="40 Akin Str, By Kil")
    admin_management_page.expect_row_visible(EXISTING_HOTEL_ROW)


@pytest.mark.regression
@pytest.mark.testcase("TC-HA036")
def test_hotel_list_search_and_pagination(admin_management_page: AdminManagementPage) -> None:
    """TC-HA036 - Search and Pagination on Hotel List."""
    admin_management_page.search(EXISTING_HOTEL_ROW)
    admin_management_page.expect_row_visible(EXISTING_HOTEL_ROW)

    admin_management_page.clear_search()
    admin_management_page.set_rows_per_page(15)
    admin_management_page.expect_table_headers_visible()


@pytest.mark.regression
@pytest.mark.testcase("TC-HA037")
def test_renew_subscription_from_hotel_record(admin_management_page: AdminManagementPage) -> None:
    """TC-HA037 - Renew Subscription from Hotel Record."""
    admin_management_page.renew_subscription(EXISTING_HOTEL_ROW, duration_option_value="1")


@pytest.mark.regression
@pytest.mark.testcase("TC-HA038")
def test_change_subscription_package_and_duration(admin_management_page: AdminManagementPage) -> None:
    """TC-HA038 - Change Subscription Package/Duration for a Hotel."""
    admin_management_page.change_subscription(
        EXISTING_HOTEL_ROW,
        duration_option_value="6",
        package_option_value=PACKAGE_OPTION_FOR_HOTEL_CHANGE,
    )


@pytest.mark.regression
@pytest.mark.testcase("TC-HA006")
@pytest.mark.testcase("TC-HA034")
def test_deactivate_then_reactivate_hotel(admin_management_page: AdminManagementPage) -> None:
    """TC-HA006 - Deactivating a Business, and TC-HA034 - Reactivating a
    Deactivated Hotel. Paired in one test so the row is left Active again
    for any test that runs after it."""
    admin_management_page.deactivate_hotel(EXISTING_HOTEL_ROW)
    admin_management_page.reactivate_hotel(EXISTING_HOTEL_ROW)


@pytest.mark.regression
@pytest.mark.destructive
@pytest.mark.testcase("TC-HA035")
@pytest.mark.testcase("TC-HA007")
def test_delete_hotel_requires_password_confirmation(
    admin_management_page: AdminManagementPage,
    super_admin_credentials: tuple[str, str],
) -> None:
    """TC-HA035 - Delete Hotel Requires Password Confirmation (also
    exercises TC-HA007's soft-delete acceptance criteria).

    Removes EXISTING_HOTEL_ROW permanently, which every other test in this
    file depends on - hence `destructive`.
    """
    _, admin_password = super_admin_credentials
    admin_management_page.search(EXISTING_HOTEL_ROW)
    admin_management_page.delete_hotel(EXISTING_HOTEL_ROW, admin_password)
    admin_management_page.expect_row_absent(EXISTING_HOTEL_ROW)
