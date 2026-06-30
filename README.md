# Nemory

A personal maintenance journal — the simplest possible way to keep a history of
maintenance, inspections, repairs, and recurring reminders for the things you own
(house, cottage, generator, ATV, water system, roof…).

At any time it answers five questions: **what** was done, **when**, on **which
asset**, with what **details**, and **when it should be done again**.

It is intentionally *not* inventory, ERP, or asset-management software. No serial
numbers, no prices, no accounting.

## Stack

Flask · SQLite (stdlib `sqlite3`) · server-rendered Jinja2 templates · vanilla
CSS/JS. Installable PWA, dark, mobile-first. Single-user with a password.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

cp .env.example .env            # then edit SECRET_KEY and NEMORY_PASSWORD
```

Generate a real secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Run

On Windows, the simplest way (creates the DB on first run, opens the browser):

```powershell
.\run.ps1                       # http://127.0.0.1:8000
```

Or manually, on any platform:

```bash
flask --app wsgi init-db        # create the database (once)
flask --app wsgi run --debug --port 8000
```

> Port 8000 is used instead of 5000 because Windows often reserves port 5000
> (you'd see WinError 10013 / "socket access forbidden").

Production:

```bash
waitress-serve --port=8000 wsgi:app
```

## Deploy to PythonAnywhere (free)

The free **Beginner** plan runs Flask + SQLite as-is: the database is just a file in
your persistent home directory (512 MB), so data survives restarts. No code changes
needed. Paths below use the account username `danieltremblay18` — if you deploy under
a different account, swap that for your own username.

**1. Create the account** at <https://www.pythonanywhere.com> (Beginner / $0).

**2. Clone the repo** — open a **Bash console** (Consoles tab) and run:

```bash
git clone https://github.com/danieltremblay18/Nemory.git
cd Nemory
```

**3. Create a virtualenv and install dependencies:**

```bash
python3.11 -m venv ~/.venvs/nemory
source ~/.venvs/nemory/bin/activate
pip install -r requirements.txt
```

**4. Initialize the database** (creates `~/Nemory/instance/nemory.sqlite`):

```bash
flask --app wsgi init-db
```

**5. Create the web app** — go to the **Web** tab → *Add a new web app* → confirm the
domain → on the *Select a Python Web framework* screen choose **Manual configuration**
(at the bottom) → pick **Python 3.11** (must match step 3).

> ⚠️ **Do NOT pick the "Flask" framework option.** It runs a "Quickstart new Flask
> project" wizard that creates — and overwrites — a single-file sample app
> (`flask_app.py`), which does not fit Nemory's package layout. If you land on a
> *"Quickstart new Flask project / Enter a path for a Python file"* screen, click
> **Back** and choose **Manual configuration** instead. With manual configuration the
> app is created empty and you point it at the real `wsgi.py` in step 7.

**6. Point the web app at the project** — in the Web tab's *Code* section set:

- **Source code**: `/home/danieltremblay18/Nemory`
- **Working directory**: `/home/danieltremblay18/Nemory`
- **Virtualenv**: `/home/danieltremblay18/.venvs/nemory`

**7. Edit the WSGI file** — click the *WSGI configuration file* link in the Web tab,
delete its contents, and replace with the following (also available ready-to-paste in
[`deploy/pythonanywhere_wsgi.py`](deploy/pythonanywhere_wsgi.py)). This is where the
secrets live, kept out of git:

```python
import sys

project = "/home/danieltremblay18/Nemory"
if project not in sys.path:
    sys.path.insert(0, project)

import os
os.environ["NEMORY_ENV"] = "production"                   # enables the secret-safety guard
os.environ["SECRET_KEY"] = "paste-a-generated-key-here"   # python -c "import secrets; print(secrets.token_hex(32))"
os.environ["NEMORY_PASSWORD"] = "your-login-password"

from wsgi import app as application
```

> Only `SECRET_KEY` and `NEMORY_PASSWORD` are placeholders — fill them in. The paths
> are already correct for the `danieltremblay18` account. `NEMORY_ENV=production`
> makes the app **refuse to start** if you leave the default secrets in place, so a
> startup error here means you still need to set a real key/password.

**8. (Optional) Serve static files faster** — in the Web tab's *Static files* section
add a mapping: URL `/static/` → Directory `/home/danieltremblay18/Nemory/app/static`.

**9. Reload** the web app (green button), then open
`https://danieltremblay18.pythonanywhere.com` and log in with `NEMORY_PASSWORD`.

### Updating later

```bash
cd ~/Nemory && git pull
source ~/.venvs/nemory/bin/activate && pip install -r requirements.txt   # if deps changed
```

Then hit **Reload** in the Web tab.

### Free-plan notes

- **Renew every 3 months**: log in and click the "Run until 3 months from today"
  button on the Web tab, or the app is paused. **Your data is not deleted.**
- Database backup: just download `~/Nemory/instance/nemory.sqlite` from the Files tab.
- The free plan allows outbound internet only to a whitelist; Nemory makes no external
  calls, so this has no effect.

## Tests

```bash
pytest                # all tests
pytest tests/test_reminders.py::test_add_months_clamps_end_of_month
```

## Project layout

```
app/
  __init__.py          app factory, template filters, error handlers
  config.py (../)      env-driven configuration
  db.py                sqlite3 connection + `flask init-db`
  schema.sql           assets + activities tables
  auth.py              single-user password login, @login_required
  main.py              home (overdue / upcoming / recent) + search + /sw.js
  assets.py            asset CRUD
  activities.py        activity CRUD + form parsing
  services/
    reminders.py       next-reminder-date calculation (the only tricky logic)
  templates/           Jinja2 views
  static/              css, js, PWA manifest + service worker, icon
wsgi.py                entry point
tests/                 pytest suite
```
