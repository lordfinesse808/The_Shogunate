"""
Test data for the E2E suite: seed-row names, <option> values, and factories
for data that must be unique per run.

Why a separate module?
    * Tests read as business scenarios instead of being littered with GUIDs.
    * When the target environment is reseeded, only this file changes.
    * Anything a test *creates* (staff, admins, notifications) gets a unique
      suffix, so the suite can be re-run without "email already exists"
      failures and two CI jobs never collide on the same record.
"""
from __future__ import annotations

import uuid
from datetime import date, timedelta

# --------------------------------------------------------------------------- #
# Seed rows that already exist in the target environment                      #
# --------------------------------------------------------------------------- #
EXISTING_HOTEL_ROW = "Finesse inc"
EXISTING_SUBSCRIPTION_ROW = "diamond test"
EXISTING_NOTIFICATION_TITLE = "Staff Payment Reminder"
EXISTING_ADMIN_ROW = "Jay Julien"
DELETABLE_ADMIN_ROW = "Yusuf yousuf"
SEARCHABLE_ADMIN_NAME = "Sade Akin"
EXISTING_RESERVATION_ID = "RES2609256778"

# --------------------------------------------------------------------------- #
# <select> option values captured from the recording (they are database ids,  #
# so give each one a readable name here)                                      #
# --------------------------------------------------------------------------- #
PACKAGE_OPTION_FOR_HOTEL_CHANGE = "3713f129-a6f3-4ce8-942b-883ad97e6e29"
PACKAGE_OPTION_FOR_SUBSCRIPTION_EDIT = "7de4a9c8-8d9e-43ef-8f3e-0f144d2d83bb"
DURATION_OPTION_FOR_SUBSCRIPTION_EDIT = "4675e063-e9e2-4fba-b062-a6482f79545a"
STAFF_ROLE_OPTION = "a8a20e9c-597f-47dc-a9d4-32c1b3a87882"
STAFF_ROLE_OPTION_ALT = "d64cb617-5e65-41e5-b944-866628619162"
ADMIN_ROLE_OPTION = "a8baebf6-192a-46c4-add7-6281ea2419de"
PURCHASE_REPORT_HOTEL_OPTION = "b6284536-4a23-42cf-8b2b-b4b084b342e7"

# Password given to the throw-away users the suite creates (not a real login).
NEW_USER_PASSWORD = "QaTest#Pass1"


# --------------------------------------------------------------------------- #
# Factories                                                                   #
# --------------------------------------------------------------------------- #
def unique_suffix() -> str:
    """Short random token, e.g. 'a3f9c1', to make created records unique."""
    return uuid.uuid4().hex[:6]


def unique_email(prefix: str) -> str:
    return f"{prefix}.{unique_suffix()}@maildrop.cc"


def iso_date(days_from_today: int = 0) -> str:
    """Date as YYYY-MM-DD relative to today - never hardcode calendar dates,
    they silently turn into 'dates in the past' and start failing validation."""
    return (date.today() + timedelta(days=days_from_today)).isoformat()
