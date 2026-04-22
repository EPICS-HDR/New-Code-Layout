# Standing Rock Water Data Dashboard — Developer & Operator Guide

A Django web application that aggregates water quality, climate, and dam-operations data for the Standing Rock Nation and surrounding areas in North and South Dakota. Data is pulled from three federal/state sources (COCORAHS precipitation, DANR water quality, USACE dam operations), stored in a single SQLite database, and exposed through an interactive Mapbox map, a custom graph dashboard, and a role-based admin panel.

This guide is the single source of truth for running, debugging, and modifying the project. It assumes a technical reader comfortable with Python, Django, SQL, and the command line.

---

## Table of Contents

1. [Setup & Running](#1-setup--running)
2. [Project Structure](#2-project-structure)
3. [Database Schema](#3-database-schema)
4. [URL Routes](#4-url-routes)
5. [Configuration Files](#5-configuration-files)
6. [Frontend Pages](#6-frontend-pages)
7. [Admin Dashboard](#7-admin-dashboard)
8. [Admin API Reference](#8-admin-api-reference)
9. [Data Pipeline (Source Files)](#9-data-pipeline-source-files)
10. [Custom Graph Rendering System](#10-custom-graph-rendering-system)
11. [Interactive Map Rendering System](#11-interactive-map-rendering-system)
12. [Common Tasks: Adding a Location, Metric, or Data Source](#12-common-tasks)
13. [Debugging & Troubleshooting](#13-debugging--troubleshooting)
14. [Deployment](#14-deployment)
15. [Known Bugs & Limitations](#15-known-bugs--limitations)

---

## 1. Setup & Running

### Prerequisites

- Python 3.10+
- `pip`
- A copy of `database.db` at the repository root (the DB is gitignored for size reasons; contact the team if missing)

### Local Development

```bash
# 1. Navigate to project root
cd /path/to/New-Code-Layout

# 2. Create and activate virtual environment
python3 -m venv env
source env/bin/activate        # Mac/Linux
env\Scripts\activate           # Windows

# 3. Install dependencies
pip install django plotly pandas whitenoise numpy xlsxwriter sqlite-utils matplotlib requests

# 4. Run Django migrations (creates db.sqlite3 for auth/sessions)
python manage.py migrate

# 5. Create an admin account
python manage.py createsuperuser

# 6. Start the dev server
python manage.py runserver
```

URLs once running:

| Page | URL |
|------|-----|
| Home | http://127.0.0.1:8000/ |
| Interactive Map | http://127.0.0.1:8000/map/ |
| Custom Graphs | http://127.0.0.1:8000/maptabs/ |
| Admin login | http://127.0.0.1:8000/admin/login/ |

### Database Path Resolution

The measurement database is `database.db` at the repository root. The code finds it via this priority order:

1. `MEASUREMENTS_DB_PATH` environment variable (explicit override)
2. Django `settings.BASE_DIR / database.db` (falls back to nothing in this project since BASE_DIR is `FrontEnd/`)
3. Repo root detected by walking up from `BackEnd/custom_graph.py` looking for a folder named `New-Code-Layout`
4. `BackEnd/../database.db`

If you deploy under a different folder name or keep the DB elsewhere, set:

```bash
export MEASUREMENTS_DB_PATH=/absolute/path/to/database.db
```

### Common Startup Errors

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'django'` | Activate your venv first |
| `ModuleNotFoundError: No module named 'plotly' / 'whitenoise' / 'pandas'` | `pip install <module>` |
| `OperationalError: no such table: auth_user` | Run `python manage.py migrate` |
| `database.db not found` warning at import time | Ensure the DB file exists at the repo root, or set `MEASUREMENTS_DB_PATH` |
| Port 8000 in use | `python manage.py runserver 8080` or `lsof -ti:8000 \| xargs kill` |
| `SyntaxError` from `BackEnd/SourceFiles/config.py` | Merge conflict in config.py — fix the conflict markers. `FrontEnd/services/views.py` has a fallback that keeps the app running, but metric/location mappings may be incomplete |

---

## 2. Project Structure

```
New-Code-Layout/
├── manage.py                         # Django entry point
├── database.db                       # Measurement data (COCORAHS, DANR, USACE tables)
├── db.sqlite3                        # Django auth DB (users, sessions)
├── firebase.json / .firebaserc       # Firebase hosting config (static hosting only)
│
├── BackEnd/
│   ├── commands.py                   # Command stubs called by admin "Run Updates" button
│   ├── custom_graph.py               # DB path detection, query helpers, Plotly graph rendering
│   ├── log.txt                       # System activity log (admin console reads this)
│   └── SourceFiles/
│       ├── config.py                 # DB_PATH, LOCATION_TO_TABLE, SQL_CONVERSION, per-source API configs
│       ├── _COCORAHS.py              # CoCoRaHS precipitation fetcher (ACIS API)
│       ├── _DANR.py                  # SD DANR water-quality fetcher
│       └── _USACE.py                 # USACE Missouri River dam-ops fetcher
│
├── FrontEnd/
│   ├── 404.html, index.html          # Static placeholders (used by Firebase hosting, not Django)
│   ├── config/
│   │   ├── settings.py               # Django settings: DEBUG, ALLOWED_HOSTS, DBs, static, middleware
│   │   ├── urls.py                   # Root URL routes + API routes
│   │   ├── wsgi.py / asgi.py         # Server entry points
│   │   ├── api_config.py             # API settings (currently empty / reserved)
│   │   └── info.py                   # Email credentials (imported by settings.py)
│   │
│   ├── services/                     # Public-facing app
│   │   ├── views.py                  # Page views, graph endpoints, JSON APIs, TABLE_SCHEMA
│   │   └── templates/
│   │       ├── HTML/                 # Public templates
│   │       │   ├── homepage.html
│   │       │   ├── navbar.html       # Partial — included via {% include %}, no <html> wrapper
│   │       │   ├── interactiveMap.html
│   │       │   ├── maptabs.html      # Custom graph dashboard
│   │       │   ├── graphdisplay.html # Server-rendered graph fragment for maptabs
│   │       │   ├── about.html
│   │       │   └── contactus.html
│   │       ├── admin_dashboard/      # Admin templates
│   │       │   ├── login.html
│   │       │   └── dashboard.html
│   │       └── graphing/
│   │           └── test.html         # Legacy test page at /homep/
│   │
│   ├── admin_dashboard/              # Admin app
│   │   ├── views.py                  # Auth, console log API, data-insert API, user CRUD API
│   │   └── urls.py                   # /admin/* routes
│   │
│   └── static/
│       ├── css/                      # 13 stylesheets
│       ├── js/
│       │   ├── map.js                # Mapbox init
│       │   ├── openModals.js         # Builds markers + modals from window.mapLocations
│       │   ├── updateGraphs.js       # Calls /api/timeseries/ and renders Plotly in modal
│       │   ├── admin_dashboard.js    # Admin dashboard client logic
│       │   ├── maptabs.js            # (legacy, not referenced)
│       │   ├── mapgraphs.js          # (legacy, not referenced)
│       │   ├── statistics.js         # (legacy, not referenced)
│       │   ├── selectchecks.js       # (legacy, not referenced)
│       │   ├── checkboxes.js         # (legacy, not referenced)
│       │   └── service-worker.js     # (legacy PWA worker)
│       ├── graphs/                   # 200+ pre-generated HTML graph files (LEGACY — no longer used at runtime)
│       └── images/
```

### Files That Matter Most

| File | Role |
|------|------|
| [FrontEnd/config/settings.py](FrontEnd/config/settings.py) | Django config: DEBUG, ALLOWED_HOSTS, DB path, static files, middleware |
| [FrontEnd/config/urls.py](FrontEnd/config/urls.py) | All URL routes |
| [FrontEnd/services/views.py](FrontEnd/services/views.py) | Page views, graph endpoints, JSON APIs, `TABLE_SCHEMA` dictionary |
| [FrontEnd/admin_dashboard/views.py](FrontEnd/admin_dashboard/views.py) | Admin auth, console/log APIs, data-insert API, user CRUD API |
| [BackEnd/SourceFiles/config.py](BackEnd/SourceFiles/config.py) | `DB_PATH`, `LOCATION_TO_TABLE`, `SQL_CONVERSION`, per-source `*Config` dicts |
| [BackEnd/custom_graph.py](BackEnd/custom_graph.py) | DB path resolution + `query_data()`, `get_time_format()`, `get_latest_datetime()`, `_prepare_df_for_plot()` |
| [BackEnd/log.txt](BackEnd/log.txt) | Activity log surfaced in the admin console |
| [FrontEnd/static/js/admin_dashboard.js](FrontEnd/static/js/admin_dashboard.js) | Admin client (tabs, log polling, data entry, user CRUD) |
| [FrontEnd/static/js/openModals.js](FrontEnd/static/js/openModals.js) + [updateGraphs.js](FrontEnd/static/js/updateGraphs.js) | Interactive map: build markers, fetch `/api/timeseries/`, render Plotly |

---

## 3. Database Schema

**`database.db`** contains only three real tables plus a staging table. The public frontend and admin panel both read from this file.

### `COCORAHS` — Citizen-observer precipitation network

| Column | Type | Notes |
|---|---|---|
| unique_id | TEXT | Hash of row, used for upsert deduplication |
| meta.uid | INTEGER | Source-side UID |
| meta.state | TEXT | |
| meta.elev | FLOAT | |
| **meta.name** | **TEXT** | **Location name** (e.g. `BISMARCK 1.3 WNW`) |
| **date** | **TEXT** | **Datetime** (YYYY-MM-DD) |
| v1 | TEXT | Max Temperature (degrees F) |
| v2 | TEXT | Min Temperature |
| v3 | TEXT | Average Temperature |
| v4 | TEXT | Observed Temperature |
| v5 | TEXT | Precipitation (inches) |
| v6 | TEXT | Snowfall |
| v7 | TEXT | Snow Depth |
| latitude | FLOAT | **Stored swapped** — column holds longitude |
| longitude | FLOAT | **Stored swapped** — column holds latitude |
| sid1, sid2 | TEXT | Station IDs |

The `v1`–`v7` semantics, the lat/lon swap, and the alternate `meta.name` location column are all handled by `TABLE_SCHEMA['COCORAHS']` in [views.py](FrontEnd/services/views.py).

### `DANR` — South Dakota water quality samples

| Column | Type | Notes |
|---|---|---|
| unique_id | TEXT | Upsert hash |
| id | FLOAT | |
| station_ID | TEXT | |
| aU_ID | TEXT | |
| **sampleDate** | **TEXT** | **Datetime (ISO 8601)** |
| sampleDepth | TEXT | |
| transparency, waterTemperature, dissolvedOxygen, pH, specificConductance | TEXT | Field measurements |
| tss, tkn, ammonia, nitrateNitrite, tp, eColi, chlorophyllAlpha | TEXT | Lab results |
| station.objectID | INTEGER | |
| **station.stationId** | **TEXT** | **Location identifier** (e.g. `SWLAZZZ2411A`, `460740`) |
| station.latitude, station.longitude | FLOAT | Proper ordering (not swapped) |
| station.auId, station.waterbodyName, station.primaryType, station.type | TEXT | |

Roughly 330 unique stations, 87k+ sample rows. Numeric fields are stored as TEXT and coerced by `pd.to_numeric(..., errors='coerce')` in `_load_direct_series()`.

### `USACE` — Missouri River dam hourly operations

| Column | Type | Notes |
|---|---|---|
| unique_id | TEXT | Upsert hash |
| **DateTime** | **TEXT** | **Datetime (`YYYY-MM-DD HH:MM`)** |
| Temp_Air, Temp_Water | TEXT | °F |
| Flow_Out, Flow_Spill, Flow_Powerhouse | TEXT | cfs |
| Elev, Elev_Tailwater | TEXT | feet |
| Energy | TEXT | MWh |
| **Station** | **TEXT** | **Station code** (currently only `GARR` = Garrison Dam) |

Latitude/longitude are **not stored in the table**. Coordinates for the map come from `TABLE_SCHEMA['USACE']['hardcoded_coords']`, which currently only has `GARR: (47.4988, -101.4194)`.

### `temp_staging`

Scratch table used by each source file's `_process()` step. Safe to delete between runs; recreated automatically.

### Key Point on Schemas

The tables use **different column names for the same logical concepts** (location, datetime). This is why [views.py](FrontEnd/services/views.py) declares a `TABLE_SCHEMA` dictionary that maps each real table to its `location_col`, `datetime_col`, `lat_col`, `lon_col`, and `data_cols` (display-name → SQL-column mapping). Any code that needs to query these tables should look up the schema via `_get_location_col(table_name)` / `_get_datetime_col(table_name)` rather than hardcoding `location` / `datetime`.

---

## 4. URL Routes

### Public Routes — [FrontEnd/config/urls.py](FrontEnd/config/urls.py)

| URL | Method | View | Purpose |
|-----|--------|------|---------|
| `/` or `/home/` | GET | `homepage` | Landing page |
| `/about/` | GET | `about` | About page |
| `/contactus/` | GET | `contactus` | Contact form (no backend handler — see Known Bugs) |
| `/forecast/` | GET | `forecast` | Placeholder, not implemented |
| `/map/` | GET | `interactiveMap` | Mapbox map — injects DB-derived location list as `window.mapLocations` |
| `/maptabs/` | GET | `maptabs` | Custom graph dashboard |
| `/health` | GET | `health` | Returns `"OK"` — use for uptime checks |
| `/homep/` | GET | `test` | Legacy test template at `graphing/test.html` |
| `/generate_maptab_graph/` | POST | `generate_maptab_graph` | Server-rendered Plotly graph + stats table for the maptabs form |
| `/get_latest_date/` | POST | `get_latest_date` | Returns the most recent DB datetime for a location/metric |
| `/api/map_locations/` | GET | `api_map_locations` | JSON list of all mappable locations + metadata |
| `/api/timeseries/?location=X&dataset=Y` | GET | `api_timeseries` | JSON time-series for a location + dataset, used by the map modal |

### Legacy Graph Endpoints

These exist but are broken because the tables they query (`gauge`, `mesonet`, `cocorahs`-lowercase, `shadehill`, `noaa_weather`) **no longer exist in `database.db`**. They will silently return an empty graph:

- `/customgaugegraph/` → `customgaugegraph`
- `/customcocograph/` → `customcocograph`
- `/custommesonetgraph/` → `custommesonetgraph`
- `/customnoaagraph/` → `customnoaagraph`
- `/customshadehillgraph/` → `customshadehillgraph`

Either re-point these to the current `COCORAHS`/`DANR`/`USACE` tables via `TABLE_SCHEMA`, or remove the routes and views entirely. The custom graph dashboard routes everything through `/generate_maptab_graph/` now.

### Admin Routes — [FrontEnd/admin_dashboard/urls.py](FrontEnd/admin_dashboard/urls.py) (mounted under `/admin/`)

| URL | Method | View | Access |
|-----|--------|------|--------|
| `/admin/login/` | GET, POST | `admin_login` | Public |
| `/admin/logout/` | GET | `admin_logout` | Authenticated |
| `/admin/` | GET | `admin_dashboard` | Admin or Data Moderator |
| `/admin/api/logs/?lines=N` | GET | `api_logs` | Admin or Data Moderator |
| `/admin/api/run-script/` | POST | `api_run_script` | Admin only |
| `/admin/api/tables/` | GET | `api_tables` | Admin or Data Moderator |
| `/admin/api/tables/<name>/columns/` | GET | `api_table_columns` | Admin or Data Moderator |
| `/admin/api/insert/` | POST | `api_insert` | Admin or Data Moderator |
| `/admin/api/users/` | GET, POST | `api_users_list` | Admin only |
| `/admin/api/users/<id>/` | PUT, DELETE | `api_user_detail` | Admin only |

Note: `api_commands` is defined and wired in the frontend (`admin_dashboard.js` calls `/admin/api/commands/`) but the route is **not registered** in `urls.py`. The frontend gracefully falls back to hard-coded commands when this 404s.

---

## 5. Configuration Files

### [FrontEnd/config/settings.py](FrontEnd/config/settings.py)

| Setting | What to know |
|---|---|
| `DEBUG = True` | Dev default. Set `False` for production. |
| `ALLOWED_HOSTS` | Lists all Azure domains + `127.0.0.1` + `localhost`. Add any new deploy domain here. |
| `CSRF_TRUSTED_ORIGINS` | Must include the `https://` form of any production domain. |
| `DATABASES['default']` | Points to `db.sqlite3` at repo root for **Django auth only** (users, sessions). Not the measurement DB. |
| `INSTALLED_APPS` | Includes `FrontEnd.services` (public) and `FrontEnd.admin_dashboard`. |
| `MIDDLEWARE` | Uses `WhiteNoiseMiddleware` — required for serving static files in production. |
| `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT` | Source at `FrontEnd/static/`, collected to `FrontEnd/staticfiles/`. Run `collectstatic` before deploying. |
| `SECRET_KEY` | Hardcoded and insecure. For production, replace with an env-var read. |
| `LOGIN_URL = '/admin/login/'` | Where `@login_required` redirects unauthenticated users. |

### [FrontEnd/config/info.py](FrontEnd/config/info.py)

Holds Gmail SMTP credentials imported into `settings.py`. Currently committed to the repo with real-looking credentials — **should be moved to environment variables before any public release**.

### [BackEnd/SourceFiles/config.py](BackEnd/SourceFiles/config.py)

Centralized config for backend data pulls and display-name mappings:

| Symbol | Purpose |
|---|---|
| `DB_PATH` | Absolute path to `database.db`, computed relative to this file |
| `LOCATION_TO_TABLE` | Fallback location → table mapping used when dynamic DB scan can't resolve a posted location |
| `SQL_CONVERSION` | Display metric name → legacy SQL column name. Primary lookup in `_display_metric_to_sql_column()`; `TABLE_SCHEMA.data_cols` takes precedence for the three current tables |
| `DANRConfig` | `baseURL`, `stationList` (330+ station IDs), `dateTimeFormat` |
| `COCORAHSConfig` | `baseURL`, `stationList` (54 station→code+start-date dict), `Elements` (7 data fields) |
| `USACEConfig` | `baseURL`, `stationList` (currently only `["GARR"]`), `ColumnNames` (9 columns) |

**To add a station**, edit the appropriate `*Config['stationList']` and re-run that source file's `update()`.

### [FrontEnd/services/views.py](FrontEnd/services/views.py) — `TABLE_SCHEMA`

This is the single most important schema-mapping dictionary in the codebase. Every schema-aware query in `views.py` looks up table metadata here:

```python
TABLE_SCHEMA = {
    'COCORAHS': {
        'location_col': 'meta.name',
        'datetime_col': 'date',
        'lat_col': 'latitude',   # Note: physically swapped in DB
        'lon_col': 'longitude',
        'lat_lon_swapped': True,
        'data_cols': {
            'Max Temperature': 'v1', 'Min Temperature': 'v2',
            'Average Temperature': 'v3', 'Observed Temperature': 'v4',
            'Precipitation': 'v5', 'Snowfall': 'v6', 'Snow Depth': 'v7',
        },
    },
    'DANR': { ... 'location_col': 'station.stationId', 'datetime_col': 'sampleDate', ... },
    'USACE': { ... 'location_col': 'Station', 'datetime_col': 'DateTime',
               'hardcoded_coords': {'GARR': (47.4988, -101.4194)}, ... },
}
```

Adding a new table without `location` / `datetime` columns? Add an entry here. Helpers `_get_location_col(table)` and `_get_datetime_col(table)` default to `'location'` / `'datetime'` when no entry exists.

### User Roles

Implemented via Django's built-in auth:

| Role | Backed by | Access |
|---|---|---|
| **Admin** | `User.is_staff = True` | Everything: console, data entry, user CRUD, script execution |
| **Data Moderator** | Member of the `"Data Moderator"` `Group` | Console log + data entry. No user CRUD. No script execution. |
| **User** (neither) | — | Cannot log into the admin panel. |

Helpers in [admin_dashboard/views.py](FrontEnd/admin_dashboard/views.py):
- `_get_user_role(user)` returns `'admin'`, `'data_moderator'`, or `None`
- `_has_dashboard_access(user)` — allows admin + moderator
- `@_dashboard_required` — decorator for admin + moderator endpoints
- `@_admin_only` — decorator for admin-only endpoints

---

## 6. Frontend Pages

### Home — `/`
Hero section, "Goals" and "What We Do" sections with CDN-hosted Builder.io images, two service cards (Interactive Map, Custom Graphs), and a footer email link. No dynamic data.

### Interactive Map — `/map/`
Mapbox map centered on `[-100.5, 46.5]` with bounds locked roughly to ND/SD/MT. The view function `interactiveMap()` in [views.py](FrontEnd/services/views.py):

1. Calls `_scan_location_table_map(conn)` to find every location present in any DB table with a known location column.
2. For each location, pulls lat/lon from either:
   - `TABLE_SCHEMA[table]['hardcoded_coords']` (USACE only), or
   - the schema's `lat_col` / `lon_col` (applying the lat/lon swap for COCORAHS).
3. Serializes `{name, lat, lon, table, datasets}` into `window.mapLocations`.

[openModals.js](FrontEnd/static/js/openModals.js) builds a Mapbox marker per location, colored by source table:

| Table | Marker color | Hex |
|---|---|---|
| DANR | red | `#f91d1d` |
| COCORAHS | green | `#057c37` |
| USACE | blue | `#140ceb` |

**Note:** The on-screen legend in [interactiveMap.html](FrontEnd/services/templates/HTML/interactiveMap.html) only shows two entries (DANR, COCORAHS). USACE markers appear on the map but are missing from the legend.

Clicking a marker:
- Opens a modal containing a heading, a dataset `<select>` (if the station has multiple datasets), and a graph container.
- Calls `fetchAndUpdateGraph(loc, dataset, modalId)` from [updateGraphs.js](FrontEnd/static/js/updateGraphs.js), which fetches `/api/timeseries/` and renders a Plotly `scatter` chart inside the modal.
- Scrolls the modal into view.

The 200+ pre-generated HTML files in [static/graphs/](FrontEnd/static/graphs/) are **leftover from an older rendering model** and are not used by the current map.

### Custom Graph Dashboard — `/maptabs/`
Location chips populated from `_scan_location_table_map()`, filtered to skip purely numeric location codes. Clicking a chip populates the data-type dropdown from `TABLE_SCHEMA[table]['data_cols']` (for the 3 real tables) or a heuristic column scan otherwise.

Workflow:
1. User selects location → metric → date range.
2. Form POSTs to `/generate_maptab_graph/` (which calls `_render_posted_graph()` → `_render_graph_response()`).
3. Response is an HTML fragment ([graphdisplay.html](FrontEnd/services/templates/HTML/graphdisplay.html)) containing a Plotly `div` + a statistics table (mean, SD, median, min, max, range).
4. Client-side JS in [maptabs.html](FrontEnd/services/templates/HTML/maptabs.html) sandboxes the response in an iframe and auto-resizes.

Quick-range chips: `Last 7 days`, `Last 30 days`, `YTD`, `Last 1 year`, `Clear`. The "Recent Data" button POSTs to `/get_latest_date/` to pick up the newest available data for a location/metric, then auto-generates a graph.

### About — `/about/`
Two sections (Standing Rock Sioux Tribe and EPICS HDR team at Purdue) with external links. Static content only.

### Contact Us — `/contactus/`
Name, Email, Category (`Comment`/`Concern`), Message. Submit button enables only when all fields are filled. **The form has no action URL and no backend handler — submitting does nothing.** See Known Bugs.

---

## 7. Admin Dashboard

### Password Storage & Encryption

Django's built-in authentication handles all password storage. **No plaintext passwords are ever stored.**

- **Algorithm:** PBKDF2 with SHA-256 (Django default — no custom `PASSWORD_HASHERS` configured in `settings.py`)
- **Format stored in DB:** `<algorithm>$<iterations>$<salt>$<hash>` (e.g. `pbkdf2_sha256$870000$<salt>$<hash>`)
- **Iterations:** Django 4.x defaults to 870,000 rounds — automatically increased on each Django upgrade
- **Salt:** Randomly generated per password; stored alongside the hash in the same field
- **Where stored:** `auth_user.password` column in `database.db` (Django's built-in user table)
- **How passwords are set:** `user.set_password(raw_password)` ([views.py:453](FrontEnd/admin_dashboard/views.py#L453)) — Django hashes before saving; the raw password is never written to disk
- **How passwords are checked:** `django.contrib.auth.authenticate()` ([views.py:93](FrontEnd/admin_dashboard/views.py#L93)) — Django re-hashes the submitted password and compares; the stored hash is never decrypted

**Password validators** (configured in `settings.py` lines 101–112):
- Must not be too similar to the username
- Minimum length enforced
- Must not be a commonly-used password
- Must not be entirely numeric

To create or change a password outside the admin UI: `python manage.py createsuperuser` or `python manage.py changepassword <username>`.

### Login Page — `/admin/login/`
Simple username + password form. On success, redirects to `/admin/` (or `?next=` URL). Rejects users who lack both `is_staff=True` and `Data Moderator` group membership.

### Dashboard — `/admin/`
Three-tab SPA, all logic in [admin_dashboard.js](FrontEnd/static/js/admin_dashboard.js). The current role is passed in via the `data-role` attribute on `.dash-content` (read into `USER_ROLE` on boot). Moderators don't see the "Run Updates" button or the "User Control" tab.

#### Console Log Tab
- Auto-polls `/admin/api/logs/` every 2 seconds (`setInterval(fetchLogs, 2000)`) — this is NOT manual-only despite what older docs claimed.
- Displays the last 200 lines of [BackEnd/log.txt](BackEnd/log.txt) + any in-memory script output buffered since the last run.
- Error lines (matching `/error|✗|exception|traceback/i`) get a highlight class.
- Status dot: grey "Idle" → green "Finished Successfully" → red "Finished with Errors (Exit N)" → blue "Script running…".
- **Command dropdown** is populated from `/admin/api/commands/`, which **does not exist** as a URL route. The frontend catches this, falls back to hard-coded `listAllSources` and `listStations`. The `dashboard.html` template also statically lists `"Sync All Sources"` as an option — these three IDs must match functions in `BackEnd/commands.py` for Run to work.
- **Run Updates** (admin only): POSTs `{command: <id>}` to `/admin/api/run-script/`, which spawns a subprocess `python -c "import BackEnd.commands as cmds; cmds.<id>()"`. Output streams into the in-memory buffer.

#### Data Entry Tab
1. Dropdown populated from `/admin/api/tables/` — lists every table in `database.db` except `sqlite_*` and `temp_*`.
2. Selecting a table fetches `/admin/api/tables/<name>/columns/` and renders an input per column (with an inferred HTML input type: number for INT/REAL/FLOAT, `datetime-local` for a column literally named `datetime`, text otherwise).
3. `Insert Row` POSTs to `/admin/api/insert/` with `{table, data}`. Only non-empty fields are sent. The backend filters to known columns and `INSERT`s. Success and errors are logged to `log.txt`.
4. Feedback banner auto-dismisses after 6 seconds.

**Caveats:**
- No edit/delete from the UI. Corrections require direct SQL.
- Column types shown are whatever SQLite has stored (often `TEXT` for everything since `_DANR.py` / `_COCORAHS.py` don't cast values).
- The form lets you insert into `temp_staging` or other internal tables if they aren't filtered — `api_tables` excludes names starting with `temp_`, so you should be safe.

#### User Control Tab (admin only)
Full CRUD for Django users. Roles, active status, join date. Modal dialogs for Add/Edit. Self-mutation guards:
- Cannot change **your own** role (`api_user_detail` PUT returns 400).
- Cannot deactivate or delete **yourself**.
- Role `admin` maps to `is_staff=True`, role `data_moderator` maps to `is_staff=False` + Data Moderator Group membership.

---

## 8. Admin API Reference

All admin APIs accept JSON bodies and return JSON responses. CSRF token required for POST/PUT/DELETE (the frontend reads it from the `csrftoken` cookie automatically).

### `GET /admin/api/logs/?lines=N`
```json
{
  "lines": ["[2026-04-09 10:22:01] DATA INSERT by admin: table=\"DANR\" …", …],
  "running": false,
  "exit_code": 0
}
```
Defaults to `lines=200`. Combines file log + in-memory script buffer.

### `POST /admin/api/run-script/`
Body: `{"command": "<id>"}`. If a script is already running, returns `{"status": "already_running"}`. Otherwise spawns a subprocess and returns `{"status": "started", "command": "<id>", "label": "<human-readable>"}`.

### `GET /admin/api/tables/`
```json
{ "tables": ["COCORAHS", "DANR", "USACE"] }
```

### `GET /admin/api/tables/<name>/columns/`
```json
{
  "table": "DANR",
  "columns": [
    {"name": "unique_id", "type": "TEXT", "notnull": false, "pk": false},
    {"name": "pH", "type": "TEXT", "notnull": false, "pk": false},
    …
  ]
}
```

### `POST /admin/api/insert/`
Body: `{"table": "DANR", "data": {"pH": "7.2", "station_ID": "SWLAZZZ2411A", ...}}`.
Returns `{"status": "ok", "inserted": {...filtered...}}` on success. Every insert (and every failure) is logged to `log.txt`.

### `GET /admin/api/users/`
```json
{ "users": [{"id": 1, "username": "admin", "email": "", "role": "admin", "is_active": true, "date_joined": "2026-01-01T…"}, …] }
```

### `POST /admin/api/users/`
Body: `{"username": "...", "password": "...", "email": "...", "role": "admin"|"data_moderator"}`. Password required; email optional.

### `PUT /admin/api/users/<id>/`
Body may include any of `email`, `role`, `is_active`, `password`. Leaving `password` blank preserves the current hash.

### `DELETE /admin/api/users/<id>/`
Returns `{"status": "deleted"}`. 400 if the target is yourself.

---

## 9. Data Pipeline (Source Files)

Each source file in `BackEnd/SourceFiles/` follows the same four-function pattern:

```python
def _pull(debug=False)   # fetch from external API, return raw data
def _process(data)       # parse into pandas DataFrame, write to temp_staging
def _push()              # upsert from temp_staging into the real table via sqlite_utils
def update()             # orchestrate _pull → _process → _push
```

`sqlite_utils.upsert_all(..., hash_id="unique_id")` hashes each row and inserts only new ones, enabling idempotent re-runs.

### [_COCORAHS.py](BackEnd/SourceFiles/_COCORAHS.py)
- Source: RCC-ACIS StnData API (`data.rcc-acis.org`)
- Per-station GET with JSON params. 10-second sleep between calls to avoid rate limiting. 3 / 27 s connect / read timeouts.
- Writes to table `COCORAHS`.

### [_DANR.py](BackEnd/SourceFiles/_DANR.py)
- Source: `apps.sd.gov/NR92WQMAP/api/station/<id>` (SD DANR Water Quality Map)
- GET per station, JSON response is normalized with `pd.json_normalize(..., record_path='parameters', meta=...)`.
- Writes to table `DANR`. ~330 stations currently configured.

### [_USACE.py](BackEnd/SourceFiles/_USACE.py)
- Source: `nwd-mr.usace.army.mil/rcc/programs/data/<CODE>`
- Uses `curl` via `subprocess.run` (their SSL cert may fail Python's verification). Parses fixed-width tabular response with pandas (skipping 4 lines, regex separator).
- Writes to table `USACE`. Currently only pulls `GARR` but the endpoint supports `GARR, OAHE, BEND, FTRA, GAPT, FTPK`.

### [commands.py](BackEnd/commands.py)
Command stubs that the admin "Run Updates" button invokes:

```python
def listAllSources():  # returns list of _*.py files in SourceFiles (has a bug — see below)
def listStations(source):  # stub — pass
def updateAll():  # stub — pass
```

**Bug:** `listAllSources` does `sources += file.name.replace('.py','')`, which **iterates characters** rather than appending strings, producing junk output. It should be `sources.append(file.name.replace('.py',''))`. Also, `os.chdir` is a global side effect that breaks subsequent code. Rewrite this function before relying on it.

To wire a real data-refresh command into the admin UI:
1. Add a function like `sync_all_sources()` in `commands.py` that calls each source file's `update()`.
2. Optionally add a `get_command_catalog()` function returning `[{'id', 'label', 'description'}, ...]` for a nicer UI listing (the frontend already probes `/admin/api/commands/` and falls back gracefully).

---

## 10. Custom Graph Rendering System

Entry point: `/generate_maptab_graph/` → `generate_maptab_graph()` → `_render_posted_graph()` → `_render_graph_response()`.

### Algorithm

1. **Parse form inputs:** `location` list, `data2see` (display metric name), `start-date`, `end-date`.
2. **Resolve each location name:** `_normalize_posted_location()` strips trailing state abbreviations (`ND`/`SD`). `_resolve_location_name()` does case-insensitive matching against the dynamic location → table map.
3. **Look up the table:** via `location_table_map[loc]` or fallback to `LOCATION_TO_TABLE.get(loc, 'gauge')`.
4. **Convert display metric → SQL column:** `_display_metric_to_sql_column()` checks `SQL_CONVERSION` first, then every table's `TABLE_SCHEMA.data_cols`, then falls back to `metric.lower().replace(' ', '_')`.
5. **Load data:**
   - If `table_name in TABLE_SCHEMA`, call `_load_direct_series()` (schema-aware, uses the alt `datetime_col`/`location_col`, renames them to `datetime`/`location` for downstream code).
   - Otherwise call `custom_graph.query_data()` (generic, assumes `location`/`datetime` column names).
6. **Fallback windows** (in order):
   - If the user's window has no data and `fallback_to_closest_window` is enabled, `_closest_window_epochs()` finds the nearest available 30-day window for that location+metric and re-queries.
   - If `fallback_to_recent_window` is enabled (the maptabs endpoint uses this), missing dates trigger a 30-day window ending at `get_latest_datetime()`.
7. **Clean:** `custom_graph._prepare_df_for_plot()` normalizes datetimes (handles `YYYY-MM-DDTHH:MM:SS 00:00:00` duplicated suffixes and Mesonet `24:00:00` rollover), drops NaNs, de-dupes datetimes, sorts ascending.
8. **Render:** Build `plotly.graph_objs.Scatter` traces, wrap in an offline Plotly `div`, compute stats table, return [graphdisplay.html](FrontEnd/services/templates/HTML/graphdisplay.html).

### Key Helpers

| Helper | Purpose |
|---|---|
| `_scan_location_table_map(conn)` | Scans every non-internal table for its location column and builds `{loc: table_name}`. Handles both `location` and `TABLE_SCHEMA[*]['location_col']`. Deterministic (keeps first table encountered per location). |
| `_canonical_location_name(s)` | Lowercase + strip commas + strip trailing state names, for fuzzy matching. |
| `_parse_db_datetime(v)` | Handles epoch ints, ISO strings, duplicated time fragments, and `24:00:00` → next day. |
| `_closest_window_epochs(conn, table, col, loc, target)` | Finds the nearest existing datetime to a target, returns a 30-day window ending there. |
| `_load_direct_series(conn, table, col, loc, start, end)` | Schema-aware query; renames alt columns back to `datetime`/`location` for consistency downstream. |
| `custom_graph.query_data(conn, table, start_epoch, end_epoch)` | Simple `SELECT *` with a `datetime BETWEEN` clause. Detects epoch vs string format by sampling the first row. Returns pandas DataFrame. |
| `custom_graph.get_latest_datetime(conn, table, col)` | Returns newest datetime where `col IS NOT NULL`. |

---

## 11. Interactive Map Rendering System

Two-part flow:

1. **Server side ([views.py::interactiveMap](FrontEnd/services/views.py)):** builds `window.mapLocations` — a list of `{name, lat, lon, table, datasets}` objects for every location with resolvable coordinates. Also serves as a JSON endpoint at `/api/map_locations/` for clients that prefer to fetch dynamically.
2. **Client side ([openModals.js](FrontEnd/static/js/openModals.js)):** creates a Mapbox marker per entry. On click, builds (once) a modal with a dataset selector, then calls `fetchAndUpdateGraph(loc, dataset, modalId)` from [updateGraphs.js](FrontEnd/static/js/updateGraphs.js), which hits `/api/timeseries/?location=X&dataset=Y` and renders a Plotly scatter in the modal's graph container.

### `/api/timeseries/` response shape

```json
{
  "times": ["2025-10-01T00:00:00", "2025-10-02T00:00:00", ...],
  "values": [12.3, 14.7, ...],
  "location": "BISMARCK 1.3 WNW",
  "dataset": "Max Temperature"
}
```

Non-numeric values (e.g. CoCoRaHS's `"M"` for missing, `"T"` for trace) are silently dropped via `float()` try/except. Dates unparseable by `_parse_db_datetime` are also dropped.

### Hardcoded Mapbox Access Token

Located in [map.js:7](FrontEnd/static/js/map.js). If the token expires or is revoked, the map will silently fail to load. Move to an env var + Django template variable if this becomes a problem.

---

## 12. Common Tasks

### Add a new station to an existing source (COCORAHS / DANR / USACE)

1. Open [BackEnd/SourceFiles/config.py](BackEnd/SourceFiles/config.py).
2. Add the station ID to the appropriate `*Config['stationList']`.
3. Re-run that source's `update()` — either directly (`cd BackEnd/SourceFiles && python _COCORAHS.py`) or via the admin dashboard once `commands.py` is wired up.
4. Verify the new rows appear: `sqlite3 database.db "SELECT COUNT(*) FROM COCORAHS WHERE \"meta.name\" = 'NEW STATION';"`.

### Add a new dataset / metric to an existing table

1. Ensure the column exists in the DB (add via `ALTER TABLE` or through the source file's upsert — `sqlite_utils.upsert_all(alter=True, ...)` auto-adds new columns).
2. Add a display-name → SQL-column entry to the relevant `TABLE_SCHEMA[table]['data_cols']` in [views.py](FrontEnd/services/views.py).
3. The metric will automatically appear in the Custom Graph Dashboard dropdown for locations in that table, and in the map modal's dataset selector.

### Add a brand-new data source (new table)

1. Create `BackEnd/SourceFiles/_NEWSOURCE.py` mirroring the `_pull / _process / _push / update` pattern.
2. Add the `NEWSOURCECONFIG` dict to [config.py](BackEnd/SourceFiles/config.py).
3. In [views.py](FrontEnd/services/views.py), add a `TABLE_SCHEMA['NEWSOURCE'] = { ... }` entry with `location_col`, `datetime_col`, `lat_col`, `lon_col`, `lat_lon_swapped`, `data_cols`, and optionally `hardcoded_coords` if lat/lon aren't stored per row.
4. Add a marker color to `markerColor()` in [openModals.js](FrontEnd/static/js/openModals.js) and a legend entry in [interactiveMap.html](FrontEnd/services/templates/HTML/interactiveMap.html).
5. Run `update()` once to populate the DB.

### Reset an admin password from the command line

```bash
python manage.py changepassword <username>
```

Or via shell:

```python
python manage.py shell
>>> from django.contrib.auth.models import User
>>> u = User.objects.get(username='admin'); u.set_password('new'); u.save()
```

### Create a Data Moderator

```python
python manage.py shell
>>> from django.contrib.auth.models import User, Group
>>> u = User.objects.create_user('moderator1', password='secure!')
>>> g, _ = Group.objects.get_or_create(name='Data Moderator')
>>> u.groups.add(g); u.save()
```

### Inspect the measurement database

```bash
sqlite3 database.db

.tables
.schema COCORAHS

SELECT DISTINCT "meta.name" FROM COCORAHS;
SELECT DISTINCT "station.stationId" FROM DANR;
SELECT MIN("DateTime"), MAX("DateTime") FROM USACE WHERE "Station" = 'GARR';
SELECT COUNT(*) FROM DANR WHERE "pH" IS NOT NULL;
```

---

## 13. Debugging & Troubleshooting

### Server won't start

| Symptom | Cause & fix |
|---|---|
| `ImportError: No module named 'django'` | Activate your venv first |
| `SyntaxError` in `config.py` during import | Git merge conflict in [BackEnd/SourceFiles/config.py](BackEnd/SourceFiles/config.py). [views.py](FrontEnd/services/views.py) has a `try/except SyntaxError` fallback that loads a hardcoded mock config — the app will still run, but metric mappings may be incomplete. Fix the conflict markers. |
| Port 8000 already in use | `lsof -ti:8000 \| xargs kill` |
| `OperationalError: no such table: auth_user` | Run `python manage.py migrate` |

### Admin Data Entry tab is empty / inserts go nowhere

This was a real bug. [admin_dashboard/views.py](FrontEnd/admin_dashboard/views.py) used to point at `Measurements.db`, which was deleted when the DB was consolidated into `database.db`. The code now honours `MEASUREMENTS_DB_PATH` env var or defaults to `REPO_ROOT/database.db`. If you still see no tables, check:

```bash
python manage.py shell
>>> from FrontEnd.admin_dashboard.views import MEASUREMENTS_DB
>>> import os
>>> print(MEASUREMENTS_DB, os.path.exists(MEASUREMENTS_DB))
```

### Graph is empty or says "No data available"

Run through this checklist in order:

1. **Does the location name match the DB exactly?**
   ```bash
   sqlite3 database.db 'SELECT DISTINCT "meta.name" FROM COCORAHS LIMIT 20;'
   ```
   Location names in COCORAHS look like `BISMARCK 1.3 WNW`, which the client may post differently.

2. **Does the metric column exist?**
   Confirm the entry in `TABLE_SCHEMA['<TABLE>']['data_cols']` maps to an actual column in the table. If not, `_display_metric_to_sql_column` falls back to a slugified guess that likely doesn't exist.

3. **Does the column have data in your date range?**
   ```sql
   SELECT COUNT(*) FROM COCORAHS
   WHERE "meta.name" = 'BISMARCK 1.3 WNW' AND "v5" IS NOT NULL
     AND "date" BETWEEN '2025-10-01' AND '2025-10-31';
   ```

4. **Datetime format mismatches.** COCORAHS stores `YYYY-MM-DD`, DANR stores ISO 8601, USACE stores `YYYY-MM-DD HH:MM`. The `_closest_window_epochs` helper compares against a `YYYY-MM-DD HH:MM:SS` formatted string, which works for all three but can silently fail for weird entries. Sample your datetime values directly.

5. **COCORAHS missing-value codes.** Raw values can be `"M"` (missing), `"T"` (trace), or `"S"` (snow). These get dropped by `pd.to_numeric(errors='coerce')` in `_load_direct_series` — correct behavior but the DataFrame may end up empty.

### Map markers don't appear for a location

- Confirm the location's row has non-null lat/lon in its `lat_col`/`lon_col`, OR add an entry to `TABLE_SCHEMA[table]['hardcoded_coords']`.
- Check `/api/map_locations/` in the browser — the JSON is the authoritative data feed for `openModals.js`.
- Remember COCORAHS has `lat_lon_swapped=True`: the column named `latitude` actually holds the longitude value, and vice versa.

### Mapbox map doesn't render

- Check the browser console for a 401/403 from `api.mapbox.com`. The access token in [map.js:7](FrontEnd/static/js/map.js) may have been revoked.
- Check network connectivity — Mapbox tiles are fetched on demand.

### Admin "Run Updates" stuck on "Script running…"

- The process runs in a daemon thread with module-level `_script_running` flag. If the subprocess hangs, restart the Django server to reset the flag.
- The subprocess is spawned with `cwd=REPO_ROOT` but imports with `sys.path.insert(0, REPO_ROOT)`, so imports inside the command function need to be relative to the repo root. Check stdout captured in the admin console.
- `commands.listAllSources` has the `sources += file.name...` bug that iterates characters. Either fix it (`append`) or don't run it.

### Admin login returns "Invalid credentials or insufficient permissions"

- Wrong password → `python manage.py changepassword <user>`.
- Password correct but rejected → user exists but has neither `is_staff=True` nor Data Moderator group membership. Fix via shell:
  ```python
  u = User.objects.get(username='...')
  u.is_staff = True   # or: u.groups.add(Group.objects.get(name='Data Moderator'))
  u.save()
  ```
- User disabled → `u.is_active = True; u.save()`.

### Static files (CSS/JS) 404 in production

- `python manage.py collectstatic --noinput`
- Make sure `WhiteNoiseMiddleware` is in `MIDDLEWARE` (it is by default in this project).
- `STATIC_ROOT` is `FrontEnd/staticfiles/` — your deployment must include this directory.

### Data inserted via admin doesn't appear in graphs

- `api_insert` writes to `database.db` via `sqlite3.connect`, then returns. If the Django server is running with a cached connection elsewhere, a hard refresh should still see the new row since the frontend opens its own connection per request.
- Confirm the row went in:
  ```bash
  sqlite3 database.db 'SELECT * FROM DANR ORDER BY rowid DESC LIMIT 3;'
  ```
- If the date format is off, the graph's date filter will exclude the row. Use `YYYY-MM-DD` (or `YYYY-MM-DD HH:MM:SS`).

### Logging

Every admin action appends a timestamped line to [BackEnd/log.txt](BackEnd/log.txt):

```
[2026-03-26 13:58:07] DATA INSERT by admin: table="DANR", data={'id': 6767, 'station_ID': 'skibidi'}
[2026-03-28 10:01:54] SCRIPT RUN by admin: Sync All Sources started
[2026-04-09 12:00:00] DATA INSERT ERROR by admin: table="DANR", error=...
```

- Tail live: `tail -f BackEnd/log.txt`
- Clear without deleting: `> BackEnd/log.txt`
- The admin "Clear" button **does not** clear the file — it only clears the client display for 5 seconds.

---

## 14. Deployment

### Azure Web Apps
Current production hosts (already in `ALLOWED_HOSTS` + `CSRF_TRUSTED_ORIGINS`):
- `standingrock-dashboard.azurewebsites.net`
- `standingrock-demo.azurewebsites.net`
- `standing-rock-dev-buduamfpfuafaqdw.eastus-01.azurewebsites.net`

WSGI entry point: `FrontEnd.config.wsgi.application`.

### Firebase Hosting
[firebase.json](firebase.json) is configured to serve `FrontEnd/` as static content. This is used for a static preview / landing mirror — the full Django app lives on Azure.

### Production Checklist

1. Set `DEBUG = False` in [settings.py](FrontEnd/config/settings.py).
2. Replace the hardcoded `SECRET_KEY` with `os.environ['SECRET_KEY']`.
3. Move the SMTP credentials in [info.py](FrontEnd/config/info.py) to environment variables.
4. Add your domain to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.
5. `python manage.py collectstatic --noinput`.
6. `python manage.py migrate`.
7. Ensure `database.db` is deployed alongside the code, or set `MEASUREMENTS_DB_PATH`.
8. Ensure `BackEnd/log.txt` is writable by the app user.
9. Create at least one admin account (`createsuperuser`).
10. Verify: `/health` returns `OK`, `/map/` renders markers, `/admin/login/` accepts credentials.

---

## 15. Known Bugs & Limitations

### Actionable Bugs

| Severity | Bug | File / Line | Fix |
|---|---|---|---|
| High | `commands.listAllSources()` iterates characters into a list instead of appending filenames | [BackEnd/commands.py:13-15](BackEnd/commands.py) | Replace `sources +=` with `sources.append(...)`. Also remove the `os.chdir` side effect. |
| Medium | Legacy routes `/customgaugegraph/`, `/customcocograph/`, `/custommesonetgraph/`, `/customnoaagraph/`, `/customshadehillgraph/` target tables that no longer exist (`gauge`, `cocorahs` lowercase, `mesonet`, `noaa_weather`, `shadehill`) | [FrontEnd/config/urls.py](FrontEnd/config/urls.py), [views.py](FrontEnd/services/views.py) | Either remove these routes, or re-point the views to the new `COCORAHS`/`DANR`/`USACE` tables through `TABLE_SCHEMA`. |
| Medium | USACE markers appear on the map but have no legend entry | [interactiveMap.html](FrontEnd/services/templates/HTML/interactiveMap.html) | Add a third `<li>` with `#140ceb` color and label "USACE Dams" |
| Medium | `/admin/api/commands/` URL is referenced by the frontend but not registered in `admin_dashboard/urls.py` | [admin_dashboard/urls.py](FrontEnd/admin_dashboard/urls.py) | Register `path('api/commands/', views.api_commands, name='api_commands')`. The view already exists. |
| Low | `commands.listStations()` and `updateAll()` are empty stubs | [BackEnd/commands.py](BackEnd/commands.py) | Implement real logic once the admin "Run Updates" flow is wired for production use. |
| Low | Gmail SMTP credentials are committed to the repo | [FrontEnd/config/info.py](FrontEnd/config/info.py) | Move to env vars. Rotate the password (the committed one should be treated as leaked). |
| Low | `SECRET_KEY` is committed | [FrontEnd/config/settings.py](FrontEnd/config/settings.py) | Read from env. |
| Low | Contact form has no backend handler | [FrontEnd/services/templates/HTML/contactus.html](FrontEnd/services/templates/HTML/contactus.html) | Add an `action=` and a view that emails submissions using `django.core.mail.send_mail` (SMTP is already configured). |

### Structural / Cleanup Items

- **Unused JS files**: `maptabs.js`, `mapgraphs.js`, `statistics.js`, `selectchecks.js`, `checkboxes.js`, `service-worker.js` are not referenced by any template. Safe to delete.
- **Unused pre-generated graphs**: 200+ HTML files in [FrontEnd/static/graphs/](FrontEnd/static/graphs/) are from the old rendering model and add ~MB to every `collectstatic`. Safe to delete.
- **Unused templates**: [FrontEnd/services/templates/graphing/test.html](FrontEnd/services/templates/graphing/test.html) is the only remaining graphing template, wired to `/homep/`. Remove if no longer needed.
- **Unused `forecast` and `favorites` routes**: Stubs in views. Remove or finish.
- **DEBUG flag** is currently `True` in production settings.

### External Dependencies that can fail

- **Mapbox API**: hardcoded token in [map.js:7](FrontEnd/static/js/map.js). If revoked, the map fails silently.
- **Builder.io CDN**: homepage and about-page images. If the CDN is down, images break.
- **External data sources**: USACE's nwd-mr server has a weak SSL cert — `_USACE.py` uses `curl` specifically to bypass Python's strict validation. The COCORAHS/DANR endpoints are more stable but can still time out.

---

*Last updated: 2026-04-20. Schema and bug findings verified against commit `df6bc35e`.*
