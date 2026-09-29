# Learning E2E Test Automation with the Hotel Admin Project

A step-by-step, line-by-line guide to this suite. It explains **what** every
code block does, **why** it is written that way, and which alternatives were
rejected. Work through it with the code open beside you.

**Contents**

1. [How to study this guide](#1-how-to-study-this-guide)
2. [The big picture: what happens when you type `pytest`](#2-the-big-picture)
3. [Review verdict: is it a well-optimised POM?](#3-review-verdict)
4. [Core concepts you must know first](#4-core-concepts)
5. [File-by-file walkthrough](#5-file-by-file-walkthrough)
   - 5.1 [`requirements.txt`](#51-requirementstxt)
   - 5.2 [`pytest.ini`](#52-pytestini)
   - 5.3 [`config.py`](#53-configpy)
   - 5.4 [`test_data.py`](#54-test_datapy)
   - 5.5 [`conftest.py`](#55-conftestpy)
   - 5.6 [`pages/base_page.py`](#56-pagesbase_pagepy)
   - 5.7 [`pages/components/person_form.py`](#57-pagescomponentsperson_formpy)
   - 5.8 [`pages/login_page.py`](#58-pageslogin_pagepy)
   - 5.9 [`pages/dashboard_page.py`](#59-pagesdashboard_pagepy)
   - 5.10 [`pages/admin_management_page.py`](#510-pagesadmin_management_pagepy)
   - 5.11 [`pages/subscription_page.py`](#511-pagessubscription_pagepy)
   - 5.12 [`pages/notification_page.py`](#512-pagesnotification_pagepy)
   - 5.13 [`pages/staff_page.py`](#513-pagesstaff_pagepy)
   - 5.14 [`pages/reports_page.py`](#514-pagesreports_pagepy)
   - 5.15 [`pages/logs_page.py`](#515-pageslogs_pagepy)
   - 5.16 [`pages/admin_roles_page.py`](#516-pagesadmin_roles_pagepy)
   - 5.17 [The tests (`tests/*.py`)](#517-the-tests)
6. [Everything that was changed, and why](#6-everything-that-was-changed-and-why)
7. [Exercises to cement the learning](#7-exercises)

---

## 1. How to study this guide

1. Run the suite once, headed and slowed down, so you *see* what the code does:
   `pytest tests/test_dashboard.py --headed --slowmo 500`
2. Read section 2 to understand the flow, then section 4 for vocabulary.
3. Walk section 5 **in order**. Each file builds on the previous one:
   config → fixtures → base page → concrete pages → tests.
4. After each file, try the matching exercise in section 7.
5. Use `git diff 977f8ec -- hotel_admin_e2e/` to compare the original Drive
   version with the refined one. Section 6 explains every difference.

---

## 2. The big picture

```
you type:  pytest -m smoke
             │
             ▼
pytest reads pytest.ini ──► finds tests/ ──► imports conftest.py (fixtures)
             │
             ▼  for each test function, e.g. test_dashboard_kpis_load(dashboard_page)
pytest sees it needs the fixture `dashboard_page`
   └─ which needs `logged_in_page`
        └─ which needs `page`  (provided by the pytest-playwright plugin:
                                 launches Chromium, opens a fresh context + tab)
        └─ and `super_admin_credentials` (reads env vars, fails fast if empty)
   logged_in_page: LoginPage.goto() → login() → wait for /dashboard
   dashboard_page: wraps that page in a DashboardPage object
             │
             ▼
test body runs:  dashboard_page.expect_kpis_visible()
             │
             ▼
teardown: pytest-playwright closes the context (cookies, storage gone)
if the test failed: our hook saves screenshot + accessibility tree
```

Three layers, each with one job:

| Layer | Files | Job | Knows about |
|---|---|---|---|
| **Tests** | `tests/*.py` | *What* the business scenario is and what must be true afterwards | Page-object methods only, no locators |
| **Page objects** | `pages/*.py` | *How* to operate one screen: locators + actions + checks | Playwright API, the DOM |
| **Fixtures / config** | `conftest.py`, `config.py`, `test_data.py` | *Where to start*: environment, login, navigation, data | Everything, glue only |

That separation is the whole point of the **Page Object Model (POM)**. When
the UI changes, you fix one page object and every test that uses it is fixed
too. When the business rule changes, you edit one test.

---

## 3. Review verdict

**Short answer:** the architecture was a solid POM. The *implementation* had
one bug that stopped every test from running, plus several patterns that
undercut the POM's benefits. All of these are fixed in this version.

### What was already good (keep doing this)

- One page object per sidebar module, mirroring the PRD's sections, so a PRD
  change maps to one file.
- A `BasePage` holding widgets shared by every list screen (search, filter,
  pagination, export, modals).
- Fixtures own login and navigation, so tests read like business scenarios.
- Role-based locators (`get_by_role`) almost everywhere, which is the most
  resilient kind.
- Traceability to test case IDs, a failure-diagnostics hook, and good
  explanatory comments.

### What was not optimised (and is now fixed)

| # | Problem | Why it matters | Fix |
|---|---|---|---|
| 1 | **`expect.set_default_timeout()` does not exist** in Playwright for Python | The autouse session fixture raised `AttributeError`, so **all tests errored during setup**. Reproduced against a mock app. | `expect.set_options(timeout=...)` |
| 2 | Real super-admin password committed as a default in `config.py` (and in the README) | The repo is public; the docstring even said credentials are "never hardcoded" | No credential defaults; env vars only; fail-fast fixture |
| 3 | `open_row_actions` copy-pasted into 4 page objects | Violates DRY, the thing POM exists to prevent | One copy in `BasePage` |
| 4 | Same 10-line name/email/phone/password block in Staff and Admin pages | Same | `PersonForm` **component object** |
| 5 | Locators rebuilt inline in every method (`self.page.locator('input[name="firstName"]')` twice per field) | Hard to find, hard to change, noisy | Locators declared once in `__init__` |
| 6 | `click()` before every `fill()` (a Codegen habit) | Doubles the actions; `fill()` already focuses | Removed |
| 7 | `BasePage.__init__` silently called `page.set_default_timeout()` | Hidden side effect every time a page object is built | Moved to an explicit fixture |
| 8 | **~15 tests had no assertion**: renew, change subscription, deactivate, delete, edit subscription, pagination, exports... | A test that asserts nothing can only fail on a crash; it passes even when the feature is broken | Every mutating flow now waits for its modal to close; deletes assert the row is gone; exports assert a file was received |
| 9 | `test_export_logs_downloads_file` never clicked Export | Test name promised something the body did not check | Now exports and checks the download |
| 10 | `test_delete_admin_with_confirmation` asserted an *unrelated* admin was still visible | Passes even if the delete silently failed | Asserts the deleted admin is **absent** |
| 11 | Hardcoded dates (`2026-09-26`) and fixed emails/names for created records | Dates rot into "in the past"; second run fails with "email already exists" | `iso_date()`, `unique_email()`, `unique_suffix()` |
| 12 | `test_edit_staff_phone_number` edited a staff member created by a *different* test | Fails when run alone or in another order | Test creates its own record |
| 13 | Delete tests wiped seed rows the rest of the file needs, and relied on file order | Second run of the suite fails everywhere | `destructive` marker, deselected by default |
| 14 | Magic GUIDs inline in tests | Unreadable; reseeding means hunting through files | Named constants in `test_data.py` |
| 15 | `testcase(id)` marker declared but never used | Traceability only in free-text docstrings | Every mapped test carries `@pytest.mark.testcase(...)` |
| 16 | Helpers that could never pass: `expect_kpi_visible` (`locator("div").filter(...)` matches dozens of nested divs → strict-mode error), `expect_page_indicator` (`get_by_text("Page")` matches "Go to Page" *and* "Rows Per Page"), `expect_total_visible` | Traps for the next person | Removed or fixed with `.first` |
| 17 | Unused imports (`Optional`) and dead methods | Noise | Removed |

---

## 4. Core concepts

Learn these words first. The walkthrough uses them constantly.

**Locator.** A *recipe* for finding elements, not the element itself. Creating
one (`page.get_by_role("button", name="Save")`) touches nothing. The browser
is only queried when you act (`.click()`) or assert (`expect(...)`), and it is
re-queried every time. That is why declaring locators in `__init__` is safe
even before the page has loaded.

**Locator priority** (most to least resilient):
1. `get_by_role(role, name=...)` finds by what a screen-reader user perceives
   (button "Save"). Survives CSS/markup refactors.
2. `get_by_label`, `get_by_placeholder`, `get_by_text`
3. `get_by_test_id` needs `data-testid` attributes (ask your devs for them!)
4. CSS/XPath (`input[name="email"]`), tied to implementation details
5. Position (`.nth(3)`) is the most brittle and breaks when anything is added
   above it.

**Accessible name matching.** `name="Delete"` matches *case-insensitively as a
substring* by default, so it also matches "Delete Hotel". Add `exact=True`
when that is a problem.

**Strict mode.** Actions and assertions on a locator that matches **more than
one** element throw `strict mode violation: resolved to N elements`. This is a
feature: it stops you clicking the wrong thing. Resolve it by narrowing the
locator, or deliberately with `.first`, `.last` or `.nth(i)`.

**Auto-waiting.** Before `click()`, Playwright waits until the element is
attached, visible, stable, enabled and receives events. So you almost never
need `sleep()`.

**Web-first assertions.** `expect(locator).to_be_visible()` *retries* until
true or until the timeout expires. Compare with
`assert locator.is_visible()`, which checks once, immediately, and is flaky.
**Always prefer `expect`.**

**Fixture.** A function pytest runs *before* a test to provide something
(browser page, logged-in session...). Tests request fixtures by naming them
as parameters. `scope="session"` means once per run; the default,
`"function"`, means once per test. `autouse=True` means every test gets it
without asking.

**Marker.** A tag on a test (`@pytest.mark.smoke`) used to select subsets:
`pytest -m smoke`.

**Browser context.** An isolated, incognito-like profile. pytest-playwright
gives every test a fresh one, so no cookies leak between tests.

---

## 5. File-by-file walkthrough

### 5.1 `requirements.txt`

```text
pytest>=8.0.0
pytest-playwright>=0.5.0
playwright>=1.45.0
```

| Line | Why |
|---|---|
| `pytest` | The test runner: discovers `test_*` functions, runs fixtures, reports results. |
| `pytest-playwright` | Plugin that provides the `page`, `context` and `browser` fixtures and CLI flags (`--headed`, `--browser`, `--slowmo`, `--base-url`, `--tracing`). |
| `playwright` | The browser automation library itself. After installing it, run `playwright install chromium` to download the browser binary it drives. |

`>=` means "this version or newer". For CI stability you would normally pin
exact versions (`==`) or use a lock file, so a new release can't break a run
overnight.

---

### 5.2 `pytest.ini`

```ini
[pytest]
testpaths = tests
```
`[pytest]` marks this as pytest's config section. `testpaths` tells pytest
where to look when you run plain `pytest`, which is faster and avoids
accidentally collecting files from `venv/`.

```ini
markers =
    testcase(id): maps a test function to a Test case ID in hotel_admin_test_cases_v2.xlsx
    smoke: fast critical-path checks safe to run on every deploy
    regression: full regression coverage, run on a schedule / before release
    destructive: permanently deletes seed data - deselected by default ...
```
Registers every custom marker with a description (`pytest --markers` lists
them). Registering is required because of `--strict-markers` below.

```ini
addopts = -ra --strict-markers -m "not destructive"
```
`addopts` = arguments added to every `pytest` invocation.
- `-ra`: print a short summary of all non-passing outcomes at the end.
- `--strict-markers`: a typo like `@pytest.mark.smok` becomes an *error*
  instead of a silently ignored marker.
- `-m "not destructive"`: safe default that skips the three permanent-delete
  tests. Any `-m` you type yourself replaces it (the last `-m` wins), so
  `pytest -m destructive` runs them deliberately.

---

### 5.3 `config.py`

```python
import os
```
`os.getenv` reads environment variables.

```python
BASE_URL = os.getenv("HMS_ADMIN_BASE_URL", "https://oneflare-hotel-admin.vercel.app")
```
`os.getenv(NAME, default)`: use the env var if set, else the default. A
default is fine here because a URL is **not secret**, and it lets you point
the same suite at staging or production without code changes
(`HMS_ADMIN_BASE_URL=https://staging... pytest`).

```python
SUPER_ADMIN_EMAIL = os.getenv("HMS_SUPER_ADMIN_EMAIL", "")
SUPER_ADMIN_PASSWORD = os.getenv("HMS_SUPER_ADMIN_PASSWORD", "")
```
**No real default.** Secrets never go in source control, and this repo is
public. An empty string means "not configured"; `conftest.py` turns that into
a clear error message.

```python
VIEWER_EMAIL = os.getenv("HMS_VIEWER_EMAIL", "")
VIEWER_PASSWORD = os.getenv("HMS_VIEWER_PASSWORD", "")
```
Reserved for future RBAC tests (log in as a low-privilege Viewer and assert
that admin buttons are hidden). Not used yet; a good exercise (section 7).

```python
DEFAULT_TIMEOUT_MS = int(os.getenv("HMS_DEFAULT_TIMEOUT_MS", "15000"))
NAV_TIMEOUT_MS = int(os.getenv("HMS_NAV_TIMEOUT_MS", "30000"))
```
Env vars are always strings, so `int(...)` converts them. Two budgets:
- **Default** (15 s): how long an action (`click`, `fill`) or an `expect`
  keeps retrying. Playwright's built-in defaults are 30 s for actions and
  only 5 s for `expect`. 15 s for both suits a Vercel app with cold starts.
- **Navigation** (30 s): `goto` / `wait_for_url`, where full page loads are
  slower.

---

### 5.4 `test_data.py`

```python
from __future__ import annotations
```
Lets you write type hints like `str | None` on older Python versions and
stops annotations being evaluated at import time. It appears at the top of
every module in this project for consistency.

```python
import uuid
from datetime import date, timedelta
```
`uuid` generates random unique ids; `date`/`timedelta` do date arithmetic.

```python
EXISTING_HOTEL_ROW = "Finesse inc"
EXISTING_SUBSCRIPTION_ROW = "diamond test"
...
EXISTING_RESERVATION_ID = "RES2609256778"
```
**Seed data**: records that must already exist in the environment. They are
kept in one place because when the database is reseeded, only this block
changes. `DELETABLE_ADMIN_ROW` is deliberately separate from
`EXISTING_ADMIN_ROW`, so a destructive test never deletes a record a
non-destructive test relies on.

```python
PACKAGE_OPTION_FOR_HOTEL_CHANGE = "3713f129-a6f3-4ce8-942b-883ad97e6e29"
...
```
`<select>` dropdowns are driven by the `value` attribute of their
`<option>` elements, which here are database GUIDs. A named constant turns
`"3713f129-..."` into something a reader understands.
*Improvement idea:* select by visible label instead
(`select_option(label="Gold")`), which survives reseeding.

```python
NEW_USER_PASSWORD = "QaTest#Pass1"
```
Password for the throw-away users the suite *creates*. Not a login to
anything real, but it must satisfy the app's password rules.

```python
def unique_suffix() -> str:
    return uuid.uuid4().hex[:6]
```
`uuid4()` is random; `.hex` gives 32 hex characters; `[:6]` keeps six (16.7
million combinations, plenty for test data). Appending it to names makes
every run's records unique, so re-runs and parallel CI jobs don't collide.

```python
def unique_email(prefix: str) -> str:
    return f"{prefix}.{unique_suffix()}@maildrop.cc"
```
Sign-up forms reject duplicate emails, so a fixed email passes once and then
fails forever. `maildrop.cc` is a disposable inbox service.

```python
def iso_date(days_from_today: int = 0) -> str:
    return (date.today() + timedelta(days=days_from_today)).isoformat()
```
Returns e.g. `"2026-09-29"`. The original notification test hardcoded
`2026-09-26`, which became a date in the past three days after it was
recorded. Relative dates never rot.

---

### 5.5 `conftest.py`

pytest automatically imports any file named `conftest.py` and makes its
fixtures available to all tests below that folder. No import is needed in
the tests.

```python
from pathlib import Path
from typing import TypeVar
```
`Path` gives object-oriented file paths (`out_dir / "failure.png"`).
`TypeVar` is used for a generic type hint, explained at `_open_module`.

```python
import pytest
from playwright.sync_api import Page, expect
```
`sync_api` is Playwright's synchronous (non-`async`) API, which is simpler
and is what pytest-playwright uses. `Page` is one browser tab; `expect` is
the web-first assertion entry point.

```python
from config import (BASE_URL, DEFAULT_TIMEOUT_MS, ...)
from pages.admin_management_page import AdminManagementPage
...
PageObject = TypeVar("PageObject", bound=BasePage)
```
Imports every page object for the fixtures below. `PageObject` means "some
subclass of BasePage", which lets `_open_module` promise it returns the same
type it was given.

#### Block 1: global assertion timeout

```python
@pytest.fixture(scope="session", autouse=True)
def _configure_expect_timeout() -> None:
    expect.set_options(timeout=DEFAULT_TIMEOUT_MS)
```
- `@pytest.fixture` makes this a fixture.
- `scope="session"` means run once for the whole test run, because the
  setting is global.
- `autouse=True` means apply it without any test asking for it.
- The leading `_` is a convention for "infrastructure, don't request me".
- `expect.set_options(timeout=...)` raises `expect`'s retry budget from 5 s
  to 15 s.

> **The bug that was here.** The Drive version called
> `expect.set_default_timeout(...)`. No such method exists on `expect`
> (JavaScript configures it with `expect.configure(...)` or the config file;
> Python uses `expect.set_options(...)`). The result was `AttributeError: 'Expect' object has no attribute
> 'set_default_timeout'` during setup of *every* test. It was reproduced by
> running the original code against a mock app: 6 of 6 tests errored in
> 0.05 s. **Lesson:** after "fixing" something, run it. A fix that was never
> executed is a guess.

#### Block 2: base URL

```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {"base_url": BASE_URL, **browser_context_args}
```
pytest-playwright builds every browser context from a fixture named
`browser_context_args`. Defining a fixture with the **same name** overrides
it, and requesting it as a parameter hands you the plugin's original value.
We add `base_url`, so page objects can write `page.goto("/login")` instead
of gluing full URLs together.

`**browser_context_args` unpacks the plugin's dict *after* ours, so a
`--base-url` typed on the command line (which the plugin puts in that dict)
overrides our default. Order in a dict literal = later wins.

#### Block 3: per-page timeouts

```python
@pytest.fixture(autouse=True)
def _configure_page_timeouts(page: Page) -> None:
    page.set_default_timeout(DEFAULT_TIMEOUT_MS)
    page.set_default_navigation_timeout(NAV_TIMEOUT_MS)
```
Function-scoped (the default) because every test gets a new `page`.
Requesting `page` as a parameter is how a fixture receives another fixture.
Autouse fixtures run *before* the ones a test requests, so the timeouts are
in place before login starts.

Previously this lived in `BasePage.__init__`, so constructing any page object
silently changed global state. Explicit is better than hidden.

#### Block 4: credentials guard

```python
@pytest.fixture(scope="session")
def super_admin_credentials() -> tuple[str, str]:
    if not (SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASSWORD):
        pytest.fail("Set HMS_SUPER_ADMIN_EMAIL and HMS_SUPER_ADMIN_PASSWORD ...", pytrace=False)
    return SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD
```
**Fail fast with a clear message.** Without it, a missing env var turns into
15 s timeouts on the login form and a confusing error. `pytrace=False` hides
the Python traceback because the message says everything. Session scope
means it is checked once.

#### Block 5: logging in

```python
@pytest.fixture
def logged_in_page(page: Page, super_admin_credentials: tuple[str, str]) -> Page:
    login_page = LoginPage(page)
    login_page.goto()
    login_page.expect_loaded()
    login_page.login(*super_admin_credentials)
    page.wait_for_url("**/dashboard")
    DashboardPage(page).expect_loaded()
    return page
```
Line by line:
1. Wrap the raw tab in a `LoginPage` object.
2. `goto()` navigates to `/login`.
3. `expect_loaded()` proves the form rendered *before* typing into it.
4. `*super_admin_credentials` unpacks the `(email, password)` tuple into
   two arguments.
5. `wait_for_url("**/dashboard")` blocks until the SPA's client-side redirect
   actually changes the URL. `**` is a glob wildcard for "any prefix". The
   app shows a "Welcome back" toast *before* redirecting, so waiting on the
   URL avoids asserting too early.
6. `DashboardPage(page).expect_loaded()` gives positive proof the dashboard
   rendered.
7. `return page` hands the *authenticated* tab to whoever requested it.

**Optimisation idea (exercise):** logging in through the UI for every test
is slow. Playwright can log in once, save cookies and localStorage with
`context.storage_state(path="auth.json")`, and start later contexts from
that file.

#### Block 6: module fixtures

```python
def _open_module(page: Page, nav_link: str, page_class: type[PageObject]) -> PageObject:
    DashboardPage(page).open_nav_link(nav_link)
    page_obj = page_class(page)
    page_obj.expect_loaded()
    return page_obj
```
The original had eight nearly identical fixtures of four lines each. This
helper captures the pattern once: click the sidebar link → build the page
object → **prove it loaded** → return it. `page_class` is a *class* passed as
a value (Python allows that), and `page_class(page)` instantiates it.

```python
@pytest.fixture
def admin_management_page(logged_in_page: Page) -> AdminManagementPage:
    return _open_module(logged_in_page, "Admin Mgt", AdminManagementPage)
```
Every module fixture is now one line. A test that asks for
`admin_management_page` gets a logged-in tab already on Admin Mgt.

```python
@pytest.fixture
def staff_page(logged_in_page: Page) -> StaffPage:
    page_obj = _open_module(logged_in_page, "Staff", StaffPage)
    page_obj.select_first_hotel()
    return page_obj
```
Staff is special: its toolbar only appears after a hotel is chosen. The
fixture handles that precondition so no Staff test has to.

#### Block 7: failure diagnostics hook

```python
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
```
A **hook** is a function pytest calls at defined moments. This one runs while
pytest builds the pass/fail report for each phase (`setup`, `call`,
`teardown`). `hookwrapper=True` + `yield` means "let pytest build the report,
then give me the result". We only act on a failure in `call`, the test body
itself.

```python
    page: Page | None = item.funcargs.get("page")
    if page is None:
        return
```
`item.funcargs` holds the fixture values the test received (including
indirect ones like `page` behind `staff_page`). Non-browser tests are
skipped.

```python
    out_dir = Path("test-results") / item.name.replace("/", "_")
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=out_dir / "failure.png", full_page=True)
        (out_dir / "aria_snapshot.yaml").write_text(page.locator("body").aria_snapshot(), encoding="utf-8")
        (out_dir / "url.txt").write_text(page.url, encoding="utf-8")
    except Exception:
        pass
```
Saves three artefacts per failing test:
- **`failure.png`** is what the screen looked like.
- **`aria_snapshot.yaml`** is the accessibility tree: every role and name
  Playwright sees. When a `get_by_role(..., name=...)` locator fails, this
  file tells you the *real* name. During this review it immediately showed
  that a mock page served `â€¢â€¢` instead of `••` (a charset bug).
- **`url.txt`** tells you whether you were even on the right page.

`try/except: pass` is normally a code smell, but here it is intentional:
diagnostics are best-effort and must never hide the real failure.

---

### 5.6 `pages/base_page.py`

The parent class of every page object. Anything that looks the same on more
than one screen lives here.

```python
NAV_PATHS = {"Dashboard": "/dashboard", "Admin Mgt": "/admin-mgt", ...}
```
Maps each sidebar link's visible name to the URL path its route lands on.
Used to confirm navigation really finished (see `open_nav_link`).

```python
class BasePage:
    def __init__(self, page: Page):
        self.page = page
```
Every page object *has a* Playwright `Page` (composition). Subclasses call
`super().__init__(page)` to run this.

```python
        self.search_box = page.get_by_role("textbox", name="Search")
        self.filter_button = page.get_by_role("button", name="Filter", exact=True)
        self.filter_heading = page.get_by_role("heading", name="Filter")
        self.apply_button = page.get_by_role("button", name="Apply")
        self.clear_button = page.get_by_role("button", name="Clear")
        self.export_button = page.get_by_role("button", name="Export")
        self.prev_page_button = page.get_by_role("button", name="◀")
        self.next_page_button = page.get_by_role("button", name="▶")
        self.go_to_page_input = page.get_by_role("spinbutton").nth(0)
        self.rows_per_page_input = page.get_by_role("spinbutton").nth(1)
        self.no_data_row = page.get_by_role("row", name="No data.")
```
**Locators declared once, as attributes.** This is the heart of a clean POM:
- Every selector for a shared widget lives in one place; if "Export" is
  renamed "Download", you change one line.
- Tests and methods can use them directly
  (`expect(page_obj.rows_per_page_input).to_have_value("15")`).
- It is safe because locators are lazy (section 4).

Details worth noticing:
- `name="Filter", exact=True`: without `exact`, "Filter" would also match
  any button whose name *contains* "Filter".
- `"spinbutton"` is the ARIA role of `<input type="number">`. There are two
  in the footer, so `.nth(0)`/`.nth(1)` pick them by position (acceptable
  because the footer layout is fixed).

```python
    def open_nav_link(self, link_name: str) -> None:
        self.page.get_by_role("link", name=link_name, exact=True).click()
        path = NAV_PATHS.get(link_name)
        if path:
            self.page.wait_for_url(f"**{path}")
```
Clicks a sidebar link, then waits for the URL to change. In a single-page
app, clicking a link doesn't trigger a real page load, so without the URL
wait the next assertion could run against the *old* screen. That was the
cause of the original "still on Dashboard" flakiness. `exact=True` stops a
short link name from also matching a longer one that contains it (e.g. a
"Logs" link vs. a "Hotel Logs" link). `.get()` returns `None`
for unknown links, so the method still works for links not in the map.

```python
    def input_by_name(self, name: str) -> Locator:
        return self.page.locator(f'input[name="{name}"]')

    def fill_input(self, name: str, value: str) -> None:
        self.input_by_name(name).fill(value)
```
The app's form inputs have no `<label>`, so role/label locators can't find
them. The `name` attribute is the most stable hook left. `fill()` focuses the
field, clears it and types the value, so the `click()` Codegen puts before
it is redundant.

```python
    def search(self, term: str, press_enter: bool = True) -> None:
        self.search_box.fill(term)
        if press_enter:
            self.search_box.press("Enter")

    def clear_search(self) -> None:
        self.search_box.fill("")
```
Some tables search as you type, others on Enter; the flag covers both.
Filling an empty string clears the box.

```python
    def open_filter(self) -> None:
        self.filter_button.click()
        expect(self.filter_heading).to_be_visible()
```
**Action + proof.** After opening a popover, assert it opened, so the next
step (selecting an option) doesn't race an animation.

```python
    def select_filter_combobox(self, value: str, index: int = 0) -> None:
        self.page.get_by_role("combobox").nth(index).select_option(value)
```
A native `<select>` has role `combobox`. `select_option(value)` picks the
`<option value="...">` (you can also pass `label=` or `index=`).
Positional `nth(index)` is brittle: scoping to the filter panel
(`self.page.get_by_role("dialog").get_by_role("combobox")`) would be better
once the panel's real role is confirmed.

```python
    def row(self, row_name_pattern: str) -> Locator:
        return self.page.get_by_role("row", name=row_name_pattern)
```
A table row's accessible name is its text content flattened together, so any
distinctive substring (a hotel name, an ID) finds it.

```python
    def open_row_actions(self, row_name_pattern: str) -> None:
        self.row(row_name_pattern).first.get_by_role("button").last.click()
```
Read it left to right, like a sentence:
*find rows matching the pattern → take the first → inside it, find buttons
→ take the last → click it.*
- `.first`: the pattern might match several rows (strict mode would
  throw).
- **Chaining** `row(...).get_by_role("button")` searches *inside* the row,
  not the whole page. Scoping like this is one of the most important
  locator skills.
- `.last`: rows can have a status button *and* the kebab menu button; the
  kebab is always last.

This method used to be copy-pasted in four page objects. Now it's here once.

```python
    def expect_row_visible(self, row_name_pattern: str) -> None:
        expect(self.row(row_name_pattern).first).to_be_visible()

    def expect_row_absent(self, row_name_pattern: str) -> None:
        expect(self.row(row_name_pattern)).to_have_count(0)
```
`expect_row_visible` uses `.first` because many rows can legitimately match
(e.g. several log lines by the same admin).
`expect_row_absent` is the **positive proof a delete worked**:
`to_have_count(0)` retries until no row matches. Tests search first, so a
row on page 2 can't make the check pass by accident.

```python
    def go_to_page(self, page_number: int) -> None:
        self.go_to_page_input.fill(str(page_number))
    def set_rows_per_page(self, rows: int) -> None:
        self.rows_per_page_input.fill(str(rows))
    def next_page(self) -> None: self.next_page_button.click()
    def prev_page(self) -> None: self.prev_page_button.click()
```
Thin wrappers. `fill` needs a string, hence `str(...)`.

```python
    def export(self) -> Download:
        with self.page.expect_download() as download_info:
            self.export_button.click()
        return download_info.value
```
**Event-waiting pattern.** `expect_download()` starts listening *before* the
click. If you clicked first and then started listening, a fast download
could fire in between and be missed. The `with` block waits until a download
starts; `.value` is a `Download` object (`suggested_filename`,
`save_as(...)`, `path()`). The same pattern handles new tabs
(`expect_page`), popups and network responses (`expect_response`).

```python
    def expect_modal_heading(self, heading: str) -> None:
        expect(self.page.get_by_role("heading", name=heading)).to_be_visible()

    def expect_modal_closed(self, heading: str) -> None:
        expect(self.page.get_by_role("heading", name=heading)).to_be_hidden()
```
`expect_modal_closed` is how mutating flows now **assert success** without
knowing toast texts. On a validation or server error the modal stays open,
the assertion times out, and the test fails as it should.

```python
    def click_button(self, name: str) -> None:
        self.page.get_by_role("button", name=name).click()
    def close_modal(self) -> None: self.click_button("Close")
    def confirm(self, button_name: str = "Confirm") -> None: self.click_button(button_name)
    def cancel(self) -> None: self.click_button("Cancel")
```
One generic helper plus intention-revealing names. `confirm()` reads better
in a flow than `click_button("Confirm")`.

---

### 5.7 `pages/components/person_form.py`

```python
PHONE_PLACEHOLDER = "8012345678"

class PersonForm:
    def __init__(self, page: Page):
        self.first_name_input = page.locator('input[name="firstName"]')
        self.last_name_input = page.locator('input[name="lastName"]')
        self.email_input = page.locator('input[name="email"]')
        self.phone_input = page.get_by_role("textbox", name=PHONE_PLACEHOLDER)
        self.password_input = page.locator('input[name="password"]')

    def fill(self, first_name, last_name, email, phone, password) -> None:
        self.first_name_input.fill(first_name)
        ...
    def set_phone(self, phone: str) -> None:
        self.phone_input.fill(phone)
```
**Component objects** are the next step after page objects. "Add Staff" and
"Add Admin" share this block of fields. Rather than duplicate it, both page
objects hold `self.person_form = PersonForm(page)`, which is *composition*
("has a"), not inheritance ("is a").

The phone field has no `name` attribute, so its accessible name comes from
its **placeholder** (`8012345678`). That's fragile (a new placeholder breaks
it), so the value is a named constant with a comment. Asking developers to
add `name="phone"` or a `data-testid` is the real fix.

---

### 5.8 `pages/login_page.py`

```python
class LoginPage(BasePage):
    PATH = "/login"
```
`PATH` is a **class attribute**, shared by all instances. It's relative
because the context's `base_url` supplies the host.

```python
    def __init__(self, page: Page):
        super().__init__(page)
        self.logo = page.get_by_role("img", name="Oneflare HMS")
        self.email_input = page.get_by_role("textbox", name="admin@oneflare.com")
        self.password_input = page.get_by_role("textbox", name="••••••••")
        self.sign_in_button = page.get_by_role("button", name="Sign In")
```
`super().__init__(page)` runs `BasePage.__init__` so `self.page` and the
shared locators exist. The image's accessible name is its `alt` text. The
inputs are found by their placeholders (there are no labels), which is why
the password field's "name" is eight bullet characters. Playwright treats
`<input type="password">` as a `textbox`.

```python
    def goto(self) -> LoginPage:
        self.page.goto(self.PATH)
        return self
```
Returning `self` enables **method chaining**:
`login_page = LoginPage(page).goto()`.

```python
    def expect_loaded(self) -> None:
        expect(self.logo).to_be_visible()
        expect(self.sign_in_button).to_be_visible()
```
Every page object has an `expect_loaded()`, a contract that fixtures call
before handing the object to a test.

```python
    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.sign_in_button.click()
```
A **business-level action**. Tests say `login(email, pw)`, not "fill field
A, fill field B, click C".

```python
    def expect_still_on_login(self) -> None:
        expect(self.page).to_have_url(re.compile(r"/login"))
        expect(self.sign_in_button).to_be_visible()
```
`expect(page).to_have_url(...)` is a *page-level* web-first assertion.
`re.compile(r"/login")` matches any URL *containing* `/login`. The original
invalid-login test only re-checked the logo, which could still be visible
mid-redirect, so it didn't prove the login was rejected.

---

### 5.9 `pages/dashboard_page.py`

```python
KPI_LABELS = ("Total Hotels", "Total Earnings (USD)", "Total Earnings (NGN)", "Total Transaction Count")
CHART_HEADINGS = ("Subscription Trends", "Hotel Activity", "Earnings Over Time")
ACTIVITY_TABLE_HEADINGS = ("Top Performing Hotels", "Recent Transactions")
SUBSCRIPTION_TABLE_HEADINGS = ("Hotels with Active Subscriptions", "Hotels with Inactive Subscriptions")
```
**Data-driven checks.** The original had ten one-line methods like
`expect_total_hotels_visible()`. Now the *what* is data (tuples) and the
*how* is one loop. Adding a KPI means adding a string, not a method.
Tuples rather than lists because they're constants and immutable.

```python
    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(r"/dashboard"))
        expect(self.top_performing_heading).to_be_visible()
```
Two-step proof: *right route* + *content unique to this page*. An earlier
version checked an image named "Oneflare", which by substring matching also
matched the login page's "Oneflare HMS" logo, so it passed while still on
`/login`.

```python
    def expect_kpis_visible(self, labels: tuple[str, ...] = KPI_LABELS) -> None:
        for label in labels:
            expect(self.page.get_by_text(label)).to_be_visible()

    def expect_headings_visible(self, headings: tuple[str, ...]) -> None:
        for heading in headings:
            expect(self.page.get_by_role("heading", name=heading)).to_be_visible()
```
Charts are canvas/SVG with no useful accessible name, so they're identified
by their section heading. The default argument lets a test check a subset:
`expect_kpis_visible(("Total Hotels",))`.

```python
    def expect_chart_legend_item_visible(self, package_name: str) -> None:
        expect(self.page.get_by_text(package_name, exact=True).first).to_be_visible()
```
Legend text can appear both in the chart and in a table, hence `.first`.

---

### 5.10 `pages/admin_management_page.py`

```python
TABLE_HEADERS = ("Hotel Name", "Email", "Phone No", "Country", "City", "Status")
```
Column headers the hotel table must show, as data.

```python
        self.add_hotel_button = page.get_by_role("button", name="Add Hotel").nth(0)
        self.add_hotel_submit = page.get_by_role("button", name="Add Hotel").nth(1)
```
Once the modal is open there are **two** "Add Hotel" buttons: the toolbar one
and the modal's submit. Naming both makes that visible. A cleaner locator
would scope the submit to the dialog:
`page.get_by_role("dialog").get_by_role("button", name="Add Hotel")`.

```python
        self.password_confirm_input = page.locator('input[type="password"]')
```
The delete dialog's password field. It's the only password input on that
screen, so the CSS selector is unambiguous.

```python
    def expect_loaded(self) -> None:
        expect(self.main).to_contain_text("Add Hotel")
```
`to_contain_text` on the `<main>` landmark proves the module content (not
just the shell) rendered.

```python
    def expect_table_headers_visible(self) -> None:
        for header in TABLE_HEADERS:
            expect(self.page.get_by_role("columnheader", name=header)).to_be_visible()
```
`columnheader` is the role of `<th>`.

```python
    def add_hotel(self, name, email, phone, address) -> None:
        self.add_hotel_button.click()
        self.fill_input("name", name)
        ...
        self.add_hotel_submit.click()
```
Not used by a test yet: TC-HA004 "add hotel" is an open gap (exercise).

```python
    def edit_hotel(self, row_name_pattern: str, address: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_button("Edit")
        self.expect_modal_heading("Edit Hotel Data")
        self.fill_input("address", address)
        self.update_button.click()
        self.expect_modal_closed("Edit Hotel Data")
```
The canonical **flow method** shape: open → act → prove opened → change →
submit → prove closed (= accepted). Each step's proof makes a failure point
to the exact step that broke.

```python
    def deactivate_hotel(self, row_name_pattern: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_button("Deactivate")  # menu item
        self.expect_modal_heading("Deactivate Hotel")
        self.click_button("Deactivate")  # confirm button inside the modal
        self.expect_modal_closed("Deactivate Hotel")
```
The same label appears twice, first as the menu item and then as the confirm
button. The heading assertion in between guarantees the second click lands
in the dialog.

```python
    def delete_hotel(self, row_name_pattern: str, admin_password: str) -> None:
        ...
        self.password_confirm_input.fill(admin_password)
        self.confirm()
        self.expect_modal_closed("Delete Hotel")
```
PRD rule: deleting a hotel requires re-entering the admin password.

```python
    def renew_subscription(self, row_name_pattern: str, duration_option_value: str) -> None:
        ...
        renew = self.page.get_by_role("button", name="Renew")
        renew.click()
        expect(renew).to_be_hidden()
```
Storing the locator in a variable and asserting on *the same locator* after
clicking is a neat trick: once the modal closes it resolves to nothing, which
satisfies `to_be_hidden()`.

```python
    def change_subscription(self, row_name_pattern, duration_option_value, package_option_value) -> None:
        ...
        comboboxes = self.page.get_by_role("combobox")
        comboboxes.nth(1).select_option(duration_option_value)
        comboboxes.nth(0).select_option(package_option_value)
```
Keeping the base locator in a variable avoids repeating it; `.nth()` derives
children from it.

---

### 5.11 `pages/subscription_page.py`

```python
        self.view_switcher = page.get_by_role("combobox").first
```
The Subscriptions/Packages toggle is the first `<select>` on the screen.

```python
    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(self.PATH))
        expect(self.filter_button).to_be_visible()
```
Reuses the inherited `filter_button` locator from `BasePage`. The docstring
records a real debugging story: `get_by_role("heading")` *without a name*
matched every heading on the page (strict-mode error), and the Dashboard's
headings also contained "Subscription".

```python
    def switch_view(self, view: str) -> None:
        self.view_switcher.select_option(view.upper())
```
The `<option>` values are upper-case (`PACKAGES`); normalising means callers
can write "Packages".

```python
    def edit_subscription(self, row_name_pattern, package_option_value=None, duration_option_value=None) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_button("Edit")
        comboboxes = self.page.get_by_role("combobox")
        if package_option_value:
            comboboxes.nth(1).select_option(package_option_value)
            self.click_button("Update")
        if duration_option_value:
            comboboxes.nth(2).select_option(duration_option_value)
            self.click_button("Update")
```
**Optional parameters** (`= None`) let one method update the package, the
duration, or both. `if value:` skips a field when not given.

```python
    def delete_subscription(self, row_name_pattern: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_button("Edit")
        self.click_button("Delete")  # opens the confirmation dialog
        self.click_button("Delete")  # confirms it
```
Unlike hotels, subscription Delete lives *inside* the Edit panel (that's how
it was recorded), so here clicking Edit first is correct. Comments on the
repeated `Delete` clicks prevent someone "fixing" an apparent duplicate.

---

### 5.12 `pages/notification_page.py`

```python
from collections.abc import Iterable
```
`Iterable[str]` accepts a list, tuple, set or generator of strings. It's the
most flexible type for "something I will loop over".

```python
        self.message_input = page.locator('textarea[name="message"]')
        self.type_select = page.get_by_role("combobox").nth(0)
        self.media_type_select = page.get_by_role("combobox").nth(1)
        self.select_all_hotels_option = page.get_by_text("Select All")
        self.create_button = page.get_by_role("button", name="Create")
```
The message is a `<textarea>`, not an `<input>`, so it can't use
`fill_input`.

```python
    def fill_notification_form(self, title, notification_type, message, media_type, start_date, end_date) -> None:
        self.fill_input("title", title)
        self.type_select.select_option(notification_type)
        self.message_input.fill(message)
        self.media_type_select.select_option(media_type)
        self.fill_input("startDate", start_date)
        self.fill_input("endDate", end_date)
```
`<input type="date">` accepts `fill("YYYY-MM-DD")` directly; no date-picker
clicking needed.

```python
    def add_notification(self, ..., hotels: Iterable[str] | None = None) -> None:
        self.open_add_notification()
        self.fill_notification_form(...)
        if hotels:
            for hotel_name in hotels:
                self.select_hotel(hotel_name)
        else:
            self.select_all_hotels()
        self.create_button.click()
        expect(self.add_notification_heading).to_be_hidden()
```
One method covers both PRD cases: a *targeted* alert (pass `hotels=[...]`)
and a *platform-wide* one (omit it → Select All).

```python
    def select_hotel(self, hotel_checkbox_label: str) -> None:
        self.page.get_by_role("checkbox", name=hotel_checkbox_label).check()
```
`.check()` is idempotent: it only clicks if the box is unchecked, unlike
`.click()`, which toggles.

```python
    def open_notification(self, row_name_pattern: str) -> None:
        self.row(row_name_pattern).first.click()
```
Rows here are clickable and open a details panel.

---

### 5.13 `pages/staff_page.py`

```python
ALL_PERMISSION_MODULES = ("Dashboard", "Management", ...)
```
Documents the permission switches in render order. Useful for a future test
that toggles all of them.

```python
        self.hotel_scope_select = page.get_by_role("combobox").first
        self.add_staff_button = page.get_by_role("button", name="Add Staff").nth(0)
        self.add_staff_submit = page.get_by_role("button", name="Add Staff").nth(1)
        self.add_staff_heading = page.get_by_role("heading", name="Add Staff")
        self.person_form = PersonForm(page)
        self.staff_role_select = page.get_by_role("combobox").nth(3)
```
- `self.person_form = PersonForm(page)` uses the component from 5.7.
- `nth(3)` is the weakest locator in the suite (its comment says so). It
  assumes exactly three `<select>`s come before the role picker. If the form
  gains a field, it silently picks the wrong one. Verify against the live DOM
  via `aria_snapshot.yaml`, then scope it to the dialog.

```python
        self.role_name_input = page.get_by_role("textbox").nth(1)
```
Textbox 0 is the page's Search box; 1 is the role name in the modal.

```python
    def select_first_hotel(self) -> None:
        self.hotel_scope_select.select_option(index=1)
        expect(self.add_staff_button).to_be_visible()
```
`index=1` skips the placeholder option at index 0 ("Select a hotel"). The
assertion proves the toolbar re-rendered, which is the precondition for
every Staff test. Before this existed, every Staff test timed out waiting
for "Add Staff".

```python
    def add_role(self, role_name: str, modules: Iterable[str]) -> None:
        self.add_role_button.click()
        expect(self.add_role_heading).to_be_visible()
        self.role_name_input.fill(role_name)
        for module_name in modules:
            self.page.get_by_role("switch", name=module_name).click()
        self.create_role_button.click()
        expect(self.add_role_heading).to_be_hidden()
```
`switch` is the ARIA role of toggle switches. The loop turns on each
requested permission.

```python
    def fill_staff_form(self, first_name, last_name, email, phone, password, role_option_value, department="All") -> None:
        self.person_form.fill(first_name, last_name, email, phone, password)
        self.staff_role_select.select_option(role_option_value)
        self.fill_input("department", department)
```
Reuses the component, then fills the staff-only fields. `department="All"`
is a default argument, so callers can omit it.

```python
    def submit_add_staff(self) -> None:
        self.add_staff_submit.click()

    def add_staff(self, ...) -> None:
        self.open_add_staff()
        self.fill_staff_form(...)
        self.submit_add_staff()
        expect(self.add_staff_heading).to_be_hidden()
```
There are two **granularities** on purpose: `add_staff` is the one-call
happy path, while `open_add_staff` / `fill_staff_form` / `submit_add_staff`
let a *negative* test stop halfway and check validation. Good page objects
offer both.

```python
    def expect_add_staff_dialog_open(self) -> None:
        expect(self.add_staff_heading).to_be_visible()
```
Replaces the original `staff_page.page.get_by_role(...).wait_for()` inside
the test. Tests should not reach through the page object to raw locators.

```python
    def edit_staff(self, row_name_pattern: str, phone: str | None = None) -> None:
        ...
        if phone:
            self.set_phone_number(phone)
        self.click_button("Update")
        expect(self.edit_staff_heading).to_be_hidden()
```

```python
    def filter_by_status(self, status: str) -> None:
        self.open_filter()
        self.select_filter_combobox(status, index=1)
        self.apply_filter()
```
Composed entirely from `BasePage` building blocks.

---

### 5.14 `pages/reports_page.py`

```python
class ReportType(str, Enum):
    TRANSACTION = "Transaction Report"
    ...
```
An **Enum** is a fixed set of named values. Benefits over bare strings:
typos become `AttributeError`s at import time, your IDE autocompletes
`ReportType.`, and `list(ReportType)` gives all eleven, which feeds the
parametrised smoke test. Mixing in `str` makes each member *also* a string.
`.value` is the label (`"Transaction Report"`); `.name` is the key
(`"TRANSACTION"`).

```python
        self.from_date_input = page.get_by_role("textbox").nth(0)
        self.to_date_input = page.get_by_role("textbox").nth(1)
```
Positional again, carried over from the recording. If the report screen has
a Search box before the dates, these would be wrong. Worth verifying.

```python
    def select_report(self, report_type: ReportType) -> None:
        self.page.get_by_role("button", name=report_type.value, exact=True).click()
```
`exact=True` matters: without it a report name is matched as a substring,
so any other button whose label *contains* it (e.g. an "Export Transaction
Report" button) would collide and trigger a strict-mode error.

```python
    def clear_date_range(self) -> None:
        self.clear_filter()
```
Same button as the filter's Clear. The method keeps the *intention* readable
in tests while reusing the locator.

```python
    def expect_total_visible(self) -> None:
        expect(self.page.get_by_text("total", exact=False).first).to_be_visible()
```
Without `.first` this was a guaranteed strict-mode error (many "Total ..."
labels).

```python
    def click_visit_site(self) -> Page:
        with self.page.context.expect_page() as new_page_info:
            self.visit_site_link.click()
        return new_page_info.value
```
A link with `target="_blank"` opens a new tab, which is a new `Page` in the
same **context**. Same listen-then-act pattern as `export()`. The return type
was `None` in the original even though it returned a page; type hints should
tell the truth.

---

### 5.15 `pages/logs_page.py`

```python
        self.hotel_logs_tab = page.get_by_role("button", name="Hotel Logs")
        self.admin_logs_tab = page.get_by_role("button", name="Admin Logs")

    def filter_by_action_type(self, action_type_value: str) -> None:
        self.open_filter()
        self.select_filter_combobox(action_type_value, index=1)
        self.apply_filter()
```
The smallest page object, because `BasePage` already does most of the work.
That is the sign of a healthy base class.

---

### 5.16 `pages/admin_roles_page.py`

```python
        self.person_form = PersonForm(page)
        self.admin_role_select = page.get_by_role("combobox").nth(2)
```
The same component as Staff, a different role `<select>` index.

```python
        self.status_switch = page.get_by_role("switch")
```
The comment explains why a role locator was preferred over the Tailwind
class selector the recording produced (`.bg-green-500...`). Styling classes
change whenever a designer tweaks a colour; roles change only when behaviour
changes.

```python
    def switch_view(self, view: str) -> None:
        self.view_switcher.select_option(view.capitalize())
```
Here option values are "Admin"/"Roles" (capitalised), unlike Subscriptions'
upper-case values. Each page object hides its own quirk.

```python
    def delete_admin(self, row_name_pattern: str) -> None:
        self.open_row_actions(row_name_pattern)
        self.click_button("Delete")  # menu item
        self.click_button("Delete")  # confirm in dialog
```

---

### 5.17 The tests

Every test follows **Arrange → Act → Assert**:
- *Arrange* is done by the fixture (logged in, on the right module).
- *Act* is one or more page-object calls.
- *Assert* uses `expect_*` methods or a plain `assert` on returned data.

#### Anatomy of a test (from `test_admin_management.py`)

```python
@pytest.mark.regression
@pytest.mark.testcase("TC-HA033")
def test_edit_hotel_business_details(admin_management_page: AdminManagementPage) -> None:
    """TC-HA033 - Editing Hotel Business Details."""
    admin_management_page.edit_hotel(EXISTING_HOTEL_ROW, address="40 Akin Str, By Kil")
    admin_management_page.expect_row_visible(EXISTING_HOTEL_ROW)
```
| Line | Meaning |
|---|---|
| `@pytest.mark.regression` | Selected by `pytest -m regression`. |
| `@pytest.mark.testcase("TC-HA033")` | Links to the spreadsheet row. Find all tests for a case with `pytest --collect-only -q -m testcase` + grep, or write a small plugin that reports coverage per ID. |
| `def test_...(admin_management_page: ...)` | The name starts with `test_` so pytest collects it. The parameter name **is** the fixture request; the type hint is for your IDE. |
| docstring | Human-readable purpose; shows in reports. |
| body | Two lines of business language, no selectors. **This is what a POM buys you.** |

#### `test_login.py`
- `test_super_admin_can_log_in` uses the raw `page` fixture (not
  `logged_in_page`), because logging in *is* the thing under test.
- `test_login_rejects_invalid_credentials` is a **negative test**: wrong
  credentials → `expect_still_on_login()` (URL + button).

#### `test_dashboard.py`
Each test is one line calling a data-driven check. Smoke covers KPIs;
regression covers charts and tables.

#### `test_admin_management.py`
- `test_hotel_list_search_and_pagination`: search → row visible → clear →
  15 rows per page → table still renders.
- `test_deactivate_then_reactivate_hotel`: deactivation and reactivation
  are **paired** so the seed row is left as it was found (self-cleaning test).
- `test_delete_hotel_requires_password_confirmation` requests *two*
  fixtures: the page and `super_admin_credentials` (for the password).
  `_, admin_password = ...` unpacks the tuple and ignores the email (`_` is
  the "don't care" name). Marked `destructive`.

#### `test_subscription.py`
`test_switch_between_subscriptions_and_packages_views` now searches for a
known package and asserts it's visible. The original searched "pro" and
asserted nothing.

#### `test_notifications.py`
```python
    title = f"SOS Evacuation {unique_suffix()}"
    notification_page.add_notification(..., start_date=iso_date(0), end_date=iso_date(1))
    notification_page.search(title)
    notification_page.expect_row_visible(title)
```
Unique title + relative dates = repeatable. Search-then-assert avoids being
fooled by pagination or by an identically-named notification from an earlier
run.

```python
    notification_page.set_rows_per_page(15)
    expect(notification_page.rows_per_page_input).to_have_value("15")
```
`to_have_value` checks an input's current value; values are always strings.

#### `test_staff.py`
- **Happy path** (`test_add_staff_happy_path`): unique last name and email,
  then assert the new row.
- **Negative + recovery** (`test_add_staff_rejects_invalid_phone_number`):
  a 7-digit phone must keep the dialog open, then correcting it must
  succeed. One test proves both the validation and that the form stays
  usable afterwards.
- **Independent** (`test_edit_staff_phone_number`) creates its own staff
  member before editing it. Rule: *any test must pass when run alone*
  (`pytest -k test_edit_staff_phone_number`) and in any order.

#### `test_reports.py`
```python
def assert_downloaded(download: Download) -> None:
    assert download.suggested_filename, "Export produced a download with no file name"
```
A tiny **custom assertion helper** with a readable failure message. It's used
by five tests.

```python
@pytest.mark.smoke
@pytest.mark.parametrize("report_type", list(ReportType), ids=lambda r: r.name.lower())
def test_each_report_type_renders(reports_page: ReportsPage, report_type: ReportType) -> None:
```
**Parametrisation**: pytest generates 11 tests from one function, one per
enum member. `ids=` gives them readable names
(`test_each_report_type_renders[chromium-occupancy]`) so a failure report
says *which* report broke.

`test_reservation_report_date_range_and_clear` shows **choosing test data
that proves the feature**: a From-date of 2030 must produce "No data." A
past date proves nothing, because older records are *included* by a From
filter.

`test_booking_report_visit_site_link` asserts on the new tab's URL returned
by `click_visit_site()`.

#### `test_logs.py`
`test_export_logs_downloads_file` now matches its name: filter → row
visible → **export** → file received.

#### `test_admin_roles.py`
`test_delete_admin_with_confirmation` searches, deletes, then asserts the
**deleted** admin is absent. The original asserted a *different* admin was
visible. Always assert the effect of the action you performed.

---

## 6. Everything that was changed, and why

See the table in section 3 for the reasoning. File by file:

| File | Change |
|---|---|
| `config.py` | Removed default super-admin email/password; documented both timeouts. |
| `test_data.py` | **New.** Seed names, named option ids, `unique_suffix/unique_email/iso_date`. |
| `conftest.py` | `expect.set_options` (bug fix); `browser_context_args` base URL; explicit page-timeout fixture; credentials fail-fast; `_open_module` helper; `pathlib` + top-level imports in the hook. |
| `pytest.ini` | `testpaths`; `destructive` marker; deselect destructive by default. |
| `pages/base_page.py` | Locators in `__init__`; `open_row_actions`, `fill_input`, `click_button`, `expect_row_absent`, `expect_modal_closed` added; removed timeout side effect, redundant clicks, broken `expect_page_indicator`, unused `click_row_action_button` and `Optional` import. |
| `pages/components/person_form.py` | **New** component object shared by Staff + Admin forms. |
| `pages/login_page.py` | Relative `PATH`; locators in `__init__`; `expect_still_on_login`; unverified `expect_login_error_visible` removed. |
| `pages/dashboard_page.py` | Ten single-purpose methods → data tuples + loops; broken `expect_kpi_visible` removed. |
| `pages/admin_management_page.py` | Uses inherited helpers; every flow ends with a success check; duplicate `open_row_actions` removed. |
| `pages/subscription_page.py` | Inherited helpers; duplicate `open_row_actions` and misleading `expect_edit_panel_visible` removed. |
| `pages/notification_page.py` | Locators in `__init__`; modal-closed check after Create. |
| `pages/staff_page.py` | `PersonForm`; split open/fill/submit; `expect_add_staff_dialog_open`; success checks. |
| `pages/reports_page.py` | `ReportType` → `Enum`; `.first` fix; correct return type on `click_visit_site`. |
| `pages/logs_page.py` | Locators in `__init__`; unused `open_log_details` removed. |
| `pages/admin_roles_page.py` | `PersonForm`; locators in `__init__`; success check after Add. |
| `tests/*` | `testcase` markers; `destructive` markers; unique data; relative dates; assertions added to ~15 tests; export test fixed; delete-admin assertion fixed; edit-staff test made independent. |

**How the changes were verified.** The real site isn't reachable from the
review environment, so:
1. The *original* suite was run against a local mock of the login and
   dashboard screens: all tests errored with the `AttributeError`.
2. The *refined* `test_login.py` and `test_dashboard.py` were run against
   the same mock through the real fixtures: 6/6 passed.
3. The shared helpers (`open_row_actions`, `click_button`,
   `expect_row_absent`, `export`, `PersonForm`, `expect_modal_closed`) were
   exercised in Chromium against a mock table and modal.
4. `pyflakes` is clean; all 53 tests collect (50 by default, 3 destructive).

The remaining module tests still need a first run against the real app.
Locators flagged "unverified" in the README are the first suspects if
anything fails.

---

## 7. Exercises

1. **Watch a failure diagnose itself.** Change `KPI_LABELS[0]` to
   `"Total Hotelz"`, run `pytest tests/test_dashboard.py -k kpis`, and read
   `test-results/.../aria_snapshot.yaml`. Revert.
2. **Explore locators live.** `PWDEBUG=1 pytest tests/test_staff.py -k happy`
   opens the Playwright Inspector. Use "Pick locator" on the role `<select>`
   and replace `combobox().nth(3)` with something scoped to the dialog.
3. **Close a coverage gap.** Write `test_add_hotel` (TC-HA004) using
   `AdminManagementPage.add_hotel` with unique data, then assert the row via
   search.
4. **RBAC test.** Add a `viewer_page` fixture that logs in with
   `VIEWER_EMAIL`, then assert the "Add Hotel" button is **not** visible
   (`to_be_hidden()`).
5. **Speed up login.** Log in once per session, save
   `context.storage_state(path=...)`, and override `browser_context_args`
   to pass `storage_state=` so tests start already authenticated. Measure
   the time saved.
6. **Select by label.** Change one `select_option("<guid>")` to
   `select_option(label="...")` and remove the GUID from `test_data.py`.
7. **Record, then refactor.** Run `playwright codegen <app url>`, record a
   small flow, and turn the generated script into page-object methods using
   the rules in this guide: locators once in `__init__`, no click-before-fill,
   action + proof, and an assertion at the end.
8. **Traces.** Run `pytest --tracing retain-on-failure` and open the result
   with `playwright show-trace test-results/.../trace.zip` to step through
   every action with DOM snapshots.
