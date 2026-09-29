"""Staff module tests. Maps to TC-HA023, TC-HA024 and TC-HA045..TC-HA048."""
import pytest

from pages.staff_page import StaffPage


@pytest.mark.regression
def test_create_custom_role_with_selected_permissions(staff_page: StaffPage) -> None:
    """TC-HA045 - Creating a Custom Role with Page-Level Permissions."""
    staff_page.add_role(
        role_name="Ops Manager",
        modules=["Dashboard", "Reservations", "Reports"],
    )


@pytest.mark.smoke
def test_add_staff_happy_path(staff_page: StaffPage) -> None:
    """TC-HA023 - Manually Creating Hotel Staff."""
    staff_page.add_staff(
        first_name="Julz",
        last_name="Just",
        email="qa.staff.julz@maildrop.cc",
        phone="9060145283",
        password="QaTest#Pass1",
        role_option_value="a8a20e9c-597f-47dc-a9d4-32c1b3a87882",
    )
    staff_page.expect_row_visible("Julz Just")


@pytest.mark.regression
def test_add_staff_rejects_invalid_phone_number(staff_page: StaffPage) -> None:
    """TC-HA047 - Phone Number Validation on Staff Creation."""
    staff_page.click_add_staff()
    staff_page.fill_staff_form(
        first_name="Adigun",
        last_name="Tolani",
        email="adigunbadmus@maildrop.cc",
        phone="9089000",  # too short - invalid
        password="QaTest#Pass1",
        role_option_value="d64cb617-5e65-41e5-b944-866628619162",
    )
    staff_page.submit_add_staff()
    # Submission is rejected: the Add Staff dialog remains open.
    staff_page.page.get_by_role("heading", name="Add Staff").wait_for()

    staff_page.set_phone_number("9089000000")  # valid
    staff_page.submit_add_staff()
    staff_page.expect_row_visible("Adigun Tolani")


@pytest.mark.regression
def test_edit_staff_phone_number(staff_page: StaffPage) -> None:
    """TC-HA046 - Editing Staff Contact Details."""
    staff_page.edit_staff("Adigun Tolani", phone="9089000001")


@pytest.mark.regression
def test_filter_staff_by_status(staff_page: StaffPage) -> None:
    """TC-HA048 - Filtering Staff by Status."""
    staff_page.filter_by_status("INACTIVE")
    staff_page.filter_by_status("ACTIVE")
