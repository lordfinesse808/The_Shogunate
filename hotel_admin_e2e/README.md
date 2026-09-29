# Oneflare Hotel Admin Backend: E2E Test Suite (Playwright + Page Object Model)

Automated regression suite for the Oneflare Hotel Software Admin Backend
(`https://oneflare-hotel-admin.vercel.app`). It was built from:

- **`Hotel_Admin_Backend_PRD.pdf`**: the feature spec (Dashboard, Admin
  Management, Subscription Management, Notifications, Staff Management,
  Reports, Logs).
- **`hotel_admin_playwright_e2e.py`**: the original Playwright Codegen recording,
  reverse-engineered into the Page Object classes under `pages/`.
- **`hotel_admin_test_cases_v2.xlsx`**: the test case register (TC-HA001
  onward). Every test carries `@pytest.mark.testcase("TC-HA0xx")`.

> **New to automation?** Read [`docs/LEARNING_GUIDE.md`](docs/LEARNING_GUIDE.md).
> It walks through every file and every code block, explains why each line
> exists, and lists what was changed from the original version and why.

## Structure

```
hotel_admin_e2e/
├── config.py                  # base URL / credentials / timeouts (env vars only)
├── test_data.py               # seed-row names, <option> ids, unique-data factories
├── conftest.py                # fixtures: timeouts, login, one fixture per module, failure dump
├── pytest.ini                 # markers: smoke / regression / destructive / testcase(id)
├── requirements.txt
├── docs/LEARNING_GUIDE.md     # line-by-line walkthrough
├── pages/                     # Page Object Model
│   ├── base_page.py           # shared search/filter/rows/pagination/export/modal helpers
│   ├── components/
│   │   └── person_form.py     # name/email/phone/password block reused by Staff + Admin forms
│   ├── login_page.py          # /login
│   ├── dashboard_page.py      # /dashboard: KPIs, charts, summary tables
│   ├── admin_management_page.py  # /admin-mgt: hotel CRUD, renew/change subscription
│   ├── subscription_page.py   # Subscriptions / Packages views
│   ├── notification_page.py   # add / view notifications
│   ├── staff_page.py          # roles, staff CRUD, status filter
│   ├── reports_page.py        # all 11 report types
│   ├── logs_page.py           # Hotel Logs / Admin Logs
│   └── admin_roles_page.py    # platform admin CRUD
└── tests/
    ├── test_login.py
    ├── test_dashboard.py
    ├── test_admin_management.py
    ├── test_subscription.py
    ├── test_notifications.py
    ├── test_staff.py
    ├── test_reports.py
    ├── test_logs.py
    └── test_admin_roles.py
```

## Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

Credentials are **only** read from environment variables. There are no
defaults, because this repository is public:

```bash
export HMS_ADMIN_BASE_URL="https://oneflare-hotel-admin.vercel.app"   # optional, this is the default
export HMS_SUPER_ADMIN_EMAIL="<super admin email>"
export HMS_SUPER_ADMIN_PASSWORD="<super admin password>"
```

If they are missing, every test fails immediately with
`Set HMS_SUPER_ADMIN_EMAIL and HMS_SUPER_ADMIN_PASSWORD ...` instead of
timing out on the login form.

## Running

```bash
pytest                          # everything except destructive tests
pytest -m smoke                 # fast critical path
pytest -m regression            # full regression (still excludes destructive)
pytest -m destructive           # ONLY the 3 permanent-delete tests (disposable env!)
pytest tests/test_reports.py -v # one module
pytest tests/test_staff.py --headed --slowmo 250   # watch it run
PWDEBUG=1 pytest tests/test_staff.py::test_add_staff_happy_path   # step through in the Inspector
```

On any failure, `test-results/<test name>/` gets `failure.png`,
`aria_snapshot.yaml` (the accessibility tree, the fastest way to fix a
locator) and `url.txt`.

## Data safety

- **Destructive tests** (`delete hotel`, `delete subscription`, `delete admin`)
  permanently remove seed rows that other tests depend on. They carry
  `@pytest.mark.destructive` and are **deselected by default**.
- **Mutating tests** (edit/deactivate/renew/change, add staff/admin/role/
  notification) change or create data. Everything they *create* gets a
  unique suffix (`test_data.unique_suffix()`), so re-runs never collide.
- Seed row names live in `test_data.py`. Point them at dedicated
  "QA Test ..." records before running against a shared environment.

## Still worth double-checking against the live DOM

These locators came from reasoning, not from a recorded run, and could not be
verified from here:

- `StaffPage.staff_role_select` → `get_by_role("combobox").nth(3)`
- `AdminRolesPage.status_switch` → `get_by_role("switch")`
- the Logs page "Export" button used by `test_export_logs_downloads_file`

If one fails, open `test-results/<test>/aria_snapshot.yaml` and adjust the
locator to the real role/name.
