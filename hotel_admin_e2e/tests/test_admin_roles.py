"""Admin & Roles module tests. Maps to TC-HA001 (RBAC) and TC-HA057..TC-HA059."""
import pytest

from pages.admin_roles_page import AdminRolesPage
from test_data import (
    ADMIN_ROLE_OPTION,
    DELETABLE_ADMIN_ROW,
    EXISTING_ADMIN_ROW,
    NEW_USER_PASSWORD,
    SEARCHABLE_ADMIN_NAME,
    unique_email,
    unique_suffix,
)


@pytest.mark.smoke
def test_admin_roles_page_loads(admin_roles_page: AdminRolesPage) -> None:
    admin_roles_page.expect_row_visible(SEARCHABLE_ADMIN_NAME)


@pytest.mark.regression
@pytest.mark.testcase("TC-HA057")
def test_add_new_platform_admin(admin_roles_page: AdminRolesPage) -> None:
    """TC-HA057 - Adding a New Platform Admin."""
    last_name = f"Tolani{unique_suffix()}"
    admin_roles_page.add_admin(
        first_name="Adigun",
        last_name=last_name,
        email=unique_email("adigun.admin"),
        phone="9060145283",
        password=NEW_USER_PASSWORD,
        role_option_value=ADMIN_ROLE_OPTION,
    )
    admin_roles_page.expect_row_visible(f"Adigun {last_name}")


@pytest.mark.regression
@pytest.mark.testcase("TC-HA058")
def test_edit_admin_status_to_inactive(admin_roles_page: AdminRolesPage) -> None:
    """TC-HA058 - Editing Admin Status (Active/Inactive)."""
    admin_roles_page.edit_admin(EXISTING_ADMIN_ROW)
    admin_roles_page.toggle_status()
    admin_roles_page.select_status_option("Inactive")
    admin_roles_page.close_modal()


@pytest.mark.regression
@pytest.mark.destructive
@pytest.mark.testcase("TC-HA059")
def test_delete_admin_with_confirmation(admin_roles_page: AdminRolesPage) -> None:
    """TC-HA059 - Deleting a Platform Admin with Confirmation.

    Asserts the deleted admin is gone (the Drive version asserted an
    unrelated admin was still visible, which passes even if the delete
    silently failed).
    """
    admin_roles_page.search(DELETABLE_ADMIN_ROW)
    admin_roles_page.delete_admin(DELETABLE_ADMIN_ROW)
    admin_roles_page.expect_row_absent(DELETABLE_ADMIN_ROW)
