"""Admin & Roles module tests. Maps to TC-HA001 (RBAC) and TC-HA057..TC-HA059."""
import pytest

from pages.admin_roles_page import AdminRolesPage


@pytest.mark.smoke
def test_admin_roles_page_loads(admin_roles_page: AdminRolesPage) -> None:
    admin_roles_page.expect_row_visible("Sade Akin")


@pytest.mark.regression
def test_add_new_platform_admin(admin_roles_page: AdminRolesPage) -> None:
    """TC-HA057 - Adding a New Platform Admin."""
    admin_roles_page.add_admin(
        first_name="Adigun",
        last_name="Tolani",
        email="adiguntolani@maildrop.cc",
        phone="9060145283",
        password="QaTest#Pass1",
        role_option_value="a8baebf6-192a-46c4-add7-6281ea2419de",
    )
    admin_roles_page.expect_row_visible("Adigun Tolani")


@pytest.mark.regression
def test_edit_admin_status_to_inactive(admin_roles_page: AdminRolesPage) -> None:
    """TC-HA058 - Editing Admin Status (Active/Inactive)."""
    admin_roles_page.edit_admin("Jay Julien")
    admin_roles_page.toggle_status()
    admin_roles_page.select_status_option("Inactive")
    admin_roles_page.close_modal()


@pytest.mark.regression
def test_delete_admin_with_confirmation(admin_roles_page: AdminRolesPage) -> None:
    """TC-HA059 - Deleting a Platform Admin with Confirmation."""
    admin_roles_page.delete_admin("Yusuf yousuf")
    admin_roles_page.expect_row_visible("Jay Julien")
