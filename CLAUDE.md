# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What Nemory is (and is not)

Nemory is a **single-user PWA: a personal maintenance journal** for personal assets
(house, cottage, generator, ATV, water system, etc.). Its entire purpose is to let
the user answer five questions: what was done, when, on which asset, with what
details, and when it should be done again.

It is **deliberately not** an inventory system, ERP, enterprise asset management,
accounting, or project-management tool. This constraint is load-bearing: if a
proposed feature does not directly serve those five questions, push back and explain
why before implementing it. An Asset has **no** serial number, purchase date, price,
or depreciation — just a name. The full product spec lives in `docs/story-000001.txt`.

> Note: the original story specified a React + Cloudflare Workers/D1 stack. The
> project was instead built as a **Flask** app (per the owner's instruction). The
> story still governs the *functional* requirements, vision, data model, and UX.

## Stack

Flask · standard-library `sqlite3` (no ORM) · server-rendered Jinja2 templates ·
vanilla CSS/JS · installable PWA (manifest + service worker), dark, mobile-first.
Dependencies are kept deliberately minimal (`Flask`, `python-dotenv`, `waitress`).

## Commands

```bash
# setup
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # set SECRET_KEY and NEMORY_PASSWORD

# database (creates instance/nemory.sqlite; idempotent)
flask --app wsgi init-db

# run
flask --app wsgi run --debug    # dev, http://127.0.0.1:5000
waitress-serve --port=8000 wsgi:app   # production

# tests
pytest
pytest tests/test_reminders.py::test_add_months_clamps_end_of_month   # single test
```

The venv lives in `.venv`; on Windows invoke it as `.venv/Scripts/python.exe`.

## Architecture

App-factory pattern: `create_app()` in `app/__init__.py` wires config, the database
lifecycle, auth, and four blueprints, plus two Jinja filters (`pretty_date`,
`days_until`) and a 404 handler.

- **`app/db.py`** — one `sqlite3` connection per request, cached on `g`, row factory
  set to `sqlite3.Row`. `flask init-db` runs `app/schema.sql`. Foreign keys are
  enabled per connection.
- **`app/auth.py`** — single-user auth with **no user table**. `NEMORY_PASSWORD` is
  hashed once at startup (`init_app`) and only the hash is held in memory; login
  state lives in the signed session cookie. `@login_required` guards every view.
- **`app/main.py`** — home page (overdue / upcoming-30-days / recent, all driven by
  `next_reminder_date`), search (LIKE across asset name + title + description), and
  serves `/sw.js` from the root so the service-worker scope covers the whole app.
- **`app/assets.py`** / **`app/activities.py`** — CRUD. Form validation/normalization
  for activities is centralized in `_parse_form`.
- **`app/services/reminders.py`** — the only non-trivial logic. `next_reminder_date`
  is **always derived**, never user-entered: `compute_next_reminder_date` returns
  `None` unless both a positive interval and a valid unit (`days`/`months`/`years`)
  are given, and `add_interval` clamps month/year math to the end of the month
  (e.g. Jan 31 + 1 month → Feb 28). When touching this, keep the test cases in
  `tests/test_reminders.py` green.

**Keep business logic out of templates and route handlers** — it belongs in
`services/`. Templates extend `templates/base.html` (app bar, bottom nav, FAB);
activity rows render through the `_activity_card.html` partial, which expects each
row to expose `asset_name` (so list queries JOIN assets and alias the name).

## Data model (`app/schema.sql`)

- **assets**: `id`, `name`, `created_at`, `updated_at`
- **activities**: `id`, `asset_id` (FK, `ON DELETE CASCADE`), `title`, `description`,
  `activity_date` (ISO `YYYY-MM-DD`), `reminder_interval`, `reminder_unit`,
  `next_reminder_date`, `created_at`, `updated_at`

Dates are stored as ISO strings, which sort and compare correctly in SQLite — the
home-page overdue/upcoming queries rely on string comparison against `date.today()`.
Design new schema additions so existing data is not broken.

## UX constraints (from the spec)

Native-feeling mobile app: dark, minimalistic, very few screens/clicks. Adding an
activity must take **under 30 seconds** (the new-activity form defaults the date to
today and pre-selects the asset when reached from an asset page). The home page shows
only overdue reminders, upcoming reminders (next 30 days), and recent activities —
nothing else.

## Decision priorities

Simplicity → User Experience → Maintainability → Performance → Extensibility. Pick
the simplest solution that stays clean. Avoid overengineering, unnecessary
dependencies, and feature creep. Out of scope for v1: push/email notifications,
photo/PDF attachments, cloud sync, multiple users, tags, statistics, AI suggestions.
