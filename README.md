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

```bash
flask --app wsgi init-db        # create the database (once)
flask --app wsgi run --debug    # http://127.0.0.1:5000
```

Production:

```bash
waitress-serve --port=8000 wsgi:app
```

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
