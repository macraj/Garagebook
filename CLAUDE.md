# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app (development)
uv run main.py

# Sync dependencies after changing pyproject.toml
uv sync

# Build distribution ZIPs
uv run dev/build_dist.py macos
uv run dev/build_dist.py windows
uv run dev/build_dist.py linux
uv run dev/build_dist.py all
```

No automated test suite exists — testing is manual through the UI.

## Architecture

**Stack:** Python 3.13 + NiceGUI (Quasar-based web UI) + PyWebView (native desktop window) + SQLite. Managed by `uv`.

```
main.py          → app entry point, routing, fuel stats tab
ui/              → NiceGUI page modules (one file per view)
db/database.py   → all SQL queries and data access
db/schema.sql    → table definitions and migrations
pyproject.toml   → dependencies and Python version pin
```

**Pages/routes:**
- `/` — dashboard (fleet overview, alerts)
- `/pojazdy` — vehicle management
- `/ustawienia` — settings (currency, backup)
- `/pojazd/{id}` — vehicle detail (entries, documents, stats tabs)

**Data flow:** UI calls `db/database.py` functions synchronously → SQLite → returns `sqlite3.Row` dicts → UI re-renders via `@ui.refreshable`.

**Database:** `garagebook.db` is auto-created on first run. Schema migrations use `ALTER TABLE` wrapped in try/except (safe to re-run). Foreign keys are enabled.

## Key Conventions

- UI components are functional (no classes), using `@ui.refreshable` for reactive updates.
- Dialogs are used for all add/edit forms.
- Cost entry categories are fixed strings: `Paliwo`, `Ładowanie`, `Części`, `Obsługa`, `Usterka`, `Serwis`. The `Ładowanie` category is for EV/hybrid charging (uses kWh units).
- Fuel consumption (L/100km or kWh/100km) is calculated only from entries with `full_tank=1`, using odometer deltas between consecutive full-tank fills.
- Currency symbol is stored in `settings` table under key `currency` and fetched at render time via `db.get_setting('currency')`.
- All UI text is in Polish.
- Quasar CSS utility classes are used directly (`bg-green-50`, `text-red-900`, etc.) — no custom CSS files.
- `garagebook.db`, `.venv/`, `dist/`, and `__pycache__/` are gitignored.
