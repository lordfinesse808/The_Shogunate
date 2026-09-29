"""
Central configuration for the Oneflare Hotel Admin Backend E2E suite.

Every value is read from an environment variable so nothing environment-
specific (and above all no credential) lives in source control. Only
non-secret values have defaults; credentials must be exported before a run
(see README "Setup"). `conftest.py` fails fast with a clear message when
they are missing instead of letting every test time out on the login form.
"""
import os

BASE_URL = os.getenv("HMS_ADMIN_BASE_URL", "https://oneflare-hotel-admin.vercel.app")

# Super Admin credentials (full access - hotel/admin/subscription CRUD).
# Intentionally no defaults: this repository is public.
SUPER_ADMIN_EMAIL = os.getenv("HMS_SUPER_ADMIN_EMAIL", "")
SUPER_ADMIN_PASSWORD = os.getenv("HMS_SUPER_ADMIN_PASSWORD", "")

# Optional secondary account for RBAC / permission-boundary tests
VIEWER_EMAIL = os.getenv("HMS_VIEWER_EMAIL", "")
VIEWER_PASSWORD = os.getenv("HMS_VIEWER_PASSWORD", "")

# Budget for actions (click/fill) AND web-first assertions (expect(...)).
DEFAULT_TIMEOUT_MS = int(os.getenv("HMS_DEFAULT_TIMEOUT_MS", "15000"))
# Budget for page loads / URL changes (goto, wait_for_url).
NAV_TIMEOUT_MS = int(os.getenv("HMS_NAV_TIMEOUT_MS", "30000"))
