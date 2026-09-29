"""Staff module tests. Maps to TC-HA023, TC-HA024 and TC-HA045..TC-HA048."""
import pytest

from pages.staff_page import StaffPage
from test_data import (
    NEW_USER_PASSWORD,
    STAFF_ROLE_OPTION,
    STAFF_ROLE_OPTION_ALT,
    unique_email,
    unique_suffix,
)


@pytest.mark.regression
@pytest.mark.testcase("TC-HA045")
def test_create_custom_role_with_selected_permissions(staff_page: StaffPage) -> None:
    """TC-HA045 - Creating a Custom Role with Page-Level Permissions."""
    staff_page.add_role(
        role_name=f"Ops Manager {unique_suffix()}",
        modules=["Dashboard", "Reservations", "Reports"],
    )


@pytest.mark.smoke
@pytest.mark.testcase("TC-HA023")
def test_add_staff_happy_path(staff_page: StaffPage) -> None:
    """TC-HA023 - Manually Creating Hotel Staff."""
    last_name = f"Just{unique_suffix()}"
    staff_page.add_staff(
        first_name="Julz",
        last_name=last_name,
        email=unique_email("julz"),
        phone="9060145283",
        password=NEW_USER_PASSWORD,
        role_option_value=STAFF_ROLE_OPTION,
    )
    staff_page.expect_row_visible(f"Julz {last_name}")


@pytest.mark.regression
@pytest.mark.testcase("TC-HA047")
def test_add_staff_rejects_invalid_phone_number(staff_page: StaffPage) -> None:
    """TC-HA047 - Phone Number Validation on Staff Creation."""
    last_name = f"Tolani{unique_suffix()}"
    staff_page.open_add_staff()
    staff_page.fill_staff_form(
        first_name="Adigun",
        last_name=last_name,
        email=unique_email("adigun"),
        phone="9089000",  # too short - invalid
        password=NEW_USER_PASSWORD,
        role_option_value=STAFF_ROLE_OPTION_ALT,
    )
    staff_page.submit_add_staff()
    # Submission is rejected: the Add Staff dialog remains open.
    staff_page.expect_add_staff_dialog_open()

    staff_page.set_phone_number("9089000000")  # valid
    staff_page.submit_add_staff()
    staff_page.expect_row_visible(f"Adigun {last_name}")


@pytest.mark.regression
@pytest.mark.testcase("TC-HA046")
def test_edit_staff_phone_number(staff_page: StaffPage) -> None:
    """TC-HA046 - Editing Staff Contact Details.

    Creates its own staff member first instead of relying on the one an
    earlier test happened to create - tests must pass in any order and in
    isolation (`pytest -k test_edit_staff_phone_number`).
    """
    last_name = f"Edit{unique_suffix()}"
    staff_page.add_staff(
        first_name="Phone",
        last_name=last_name,
        email=unique_email("phone.edit"),
        phone="9089000000",
        password=NEW_USER_PASSWORD,
        role_option_value=STAFF_ROLE_OPTION_ALT,
    )
    staff_page.edit_staff(f"Phone {last_name}", phone="9089000001")
    staff_page.expect_row_visible(f"Phone {last_name}")


@pytest.mark.regression
@pytest.mark.testcase("TC-HA048")
def test_filter_staff_by_status(staff_page: StaffPage) -> None:
    """TC-HA048 - Filtering Staff by Status."""
    staff_page.filter_by_status("INACTIVE")
    staff_page.filter_by_status("ACTIVE")
