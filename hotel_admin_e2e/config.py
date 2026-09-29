"""
Central configuration for the Oneflare Hotel Admin Backend E2E suite.

All values are overridable via environment variables so credentials are
never hardcoded into source control. Defaults mirror the values captured
in the original Playwright recording purely as a local-dev convenience.
"""
import os

BASE_URL = os.getenv("HMS_ADMIN_BASE_URL", "https://oneflare-hotel-admin.vercel.app")

# Super Admin credentials (full access - hotel/admin/subscription CRUD)
SUPER_ADMIN_EMAIL = os.getenv("HMS_SUPER_ADMIN_EMAIL", "")
SUPER_ADMIN_PASSWORD = os.getenv("HMS_SUPER_ADMIN_PASSWORD", "")

# Optional secondary account for RBAC / permission-boundary tests
VIEWER_EMAIL = os.getenv("HMS_VIEWER_EMAIL", "")
VIEWER_PASSWORD = os.getenv("HMS_VIEWER_PASSWORD", "")

DEFAULT_TIMEOUT_MS = int(os.getenv("HMS_DEFAULT_TIMEOUT_MS", "15000"))
NAV_TIMEOUT_MS = int(os.getenv("HMS_NAV_TIMEOUT_MS", "30000"))
