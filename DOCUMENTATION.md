# Standing Rock Water Data Dashboard — Documentation

A Django web application that displays water and weather data for the Standing Rock Nation and surrounding areas (ND/SD). Pulls data from government agencies (USGS, USACE, NOAA, Mesonet, CoCoRaHS, DANR) and presents it via interactive maps and custom graphs.

---

## Table of Contents

1. [Setup & Running](#1-setup--running)
2. [Project Structure](#2-project-structure)
3. [URL Routes](#3-url-routes)
4. [Admin API Endpoints](#4-admin-api-endpoints)
5. [Configuration Deep Dive](#5-configuration-deep-dive)
6. [Frontend Pages](#6-frontend-pages)
7. [Admin Dashboard](#7-admin-dashboard)
8. [Data Sources & Database Schema](#8-data-sources--database-schema)
9. [Custom Graph System](#9-custom-graph-system)
10. [Debugging & Troubleshooting](#10-debugging--troubleshooting)
11. [Deployment](#11-deployment)
12. [Known Bugs & Limitations](#12-known-bugs--limitations)

---

## 1. Setup & Running

### Prerequisites

- Python 3.10+
- pip

### Local Development

```bash
# 1. Navigate to project root
cd /path/to/New-Code-Layout

# 2. Create and activate virtual environment
python -m venv env
source env/bin/activate        # Mac/Linux
env\Scripts\activate           # Windows

# 3. Install dependencies
pip install django numpy plotly xlsxwriter whitenoise pandas matplotlib

# 4. Run migrations (for auth/user tables)
python manage.py migrate

# 5. Create a superuser (admin account)
python manage.py createsuperuser

# 6. Start the dev server
python manage.py runserver
```

- **Site:** http://127.0.0.1:8000
- **Admin panel:** http://127.0.0.1:8000/admin/login

### Common Startup Errors

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'django'` | Activate your venv, then `pip install django` |
| `ModuleNotFoundError: No module named 'plotly'` | `pip install plotly` |
| `ModuleNotFoundError: No module named 'whitenoise'` | `pip install whitenoise` |
| `SyntaxError` from `BackEnd/SourceFiles/config.py` | The file has a git merge conflict. The app has a fallback that catches this — it will still run, but fix the conflict for clean imports |
| `OperationalError: no such table` | Run `python manage.py migrate` |
| Port 8000 in use | `python manage.py runserver 8080` or kill the process on 8000 |

---

## 2. Project Structure

```
New-Code-Layout/
├── manage.py                          # Django entry point
├── Measurements.db                    # Main data (water/weather measurements)
├── db.sqlite3                         # Django auth DB (users, sessions)
├── mydatabase.db                      # Secondary data store
├── firebase.json / .firebaserc        # Firebase hosting config
│
├── BackEnd/
│   ├── commands.py                    # Script runner (called from admin "Run Script")
│   ├── custom_graph.py                # Graph generation (matplotlib, pandas, plotly)
│   ├── log.txt                        # System activity log
│   └── SourceFiles/
│       ├── config.py                  # DB_PATH, LOCATION_TO_TABLE, SQL_CONVERSION maps
│       ├── _COCORAHS.py               # CoCoRaHS data fetcher
│       ├── _DANR.py                   # DANR data fetcher
│       └── _USACE.py                  # Army Corps data fetcher
│
├── FrontEnd/
│   ├── config/
│   │   ├── settings.py                # Django settings (DEBUG, ALLOWED_HOSTS, apps, DB)
│   │   ├── urls.py                    # Root URL routing
│   │   ├── wsgi.py / asgi.py          # Server entry points
│   │   ├── api_config.py              # API settings
│   │   └── info.py                    # Email config (imported by settings.py)
│   │
│   ├── services/                      # Main public-facing app
│   │   ├── views.py                   # All public page views + graph generation logic
│   │   └── templates/HTML/            # Public templates
│   │       ├── homepage.html
│   │       ├── interactiveMap.html
│   │       ├── maptabs.html           # Custom graph dashboard
│   │       ├── graphdisplay.html      # Rendered graph output
│   │       ├── about.html
│   │       ├── contactus.html
│   │       └── navbar.html
│   │
│   ├── admin_dashboard/               # Admin app
│   │   ├── views.py                   # Auth, log API, data insert API, user CRUD API
│   │   ├── urls.py                    # /admin/* routes
│   │   └── templates/admin_dashboard/
│   │       ├── login.html
│   │       └── dashboard.html
│   │
│   └── static/
│       ├── css/                       # 13 stylesheets
│       ├── js/                        # 10 JS files (map.js, openModals.js, admin_dashboard.js, etc.)
│       ├── graphs/                    # Pre-generated HTML graphs (Plotly)
│       └── images/
```

### Key Files to Know

| File | What It Does |
|------|-------------|
| `FrontEnd/config/settings.py` | Django config — DEBUG flag, ALLOWED_HOSTS, DB path, static files, middleware |
| `FrontEnd/config/urls.py` | All URL routes for the entire app |
| `FrontEnd/services/views.py` | Core logic — page rendering, graph generation, DB queries, location resolution |
| `FrontEnd/admin_dashboard/views.py` | Admin auth, console log API, data insert API, user management API |
| `BackEnd/SourceFiles/config.py` | `LOCATION_TO_TABLE` mapping, `SQL_CONVERSION` (display name -> column name), `DB_PATH` |
| `BackEnd/custom_graph.py` | Graph rendering engine (matplotlib/plotly), `query_data()`, `get_time_format()`, `get_latest_datetime()` |
| `BackEnd/log.txt` | Activity log read by the admin console |

---

## 3. URL Routes

### Public Routes (`FrontEnd/config/urls.py`)

| URL | View Function | Description |
|-----|--------------|-------------|
| `/` or `/home/` | `homepage` | Landing page |
| `/map/` | `interactiveMap` | Interactive Mapbox map with 28 station markers |
| `/maptabs/` | `maptabs` | Custom graph dashboard |
| `/about/` | `about` | About page |
| `/contactus/` | `contactus` | Contact form |
| `/forecast/` | `forecast` | Placeholder (not implemented) |
| `/health` | `health` | Returns "OK" (health check) |
| `/generate_maptab_graph/` | `generate_maptab_graph` | POST — generates graph from maptabs form |
| `/get_latest_date/` | `get_latest_date` | POST — returns latest available data date for location/metric |
| `/customgaugegraph/` | `customgaugegraph` | POST — gauge graph |
| `/customdamgraph/` | `customdamgraph` | POST — dam graph |
| `/custommesonetgraph/` | `custommesonetgraph` | POST — mesonet graph |
| `/customcocograph/` | `customcocograph` | POST — CoCoRaHS graph |
| `/customnoaagraph/` | `customnoaagraph` | POST — NOAA graph |
| `/customshadehillgraph/` | `customshadehillgraph` | POST — Shadehill graph |

### Admin Routes (`FrontEnd/admin_dashboard/urls.py`, prefixed with `/admin/`)

| URL | Method | View | Access |
|-----|--------|------|--------|
| `/admin/login/` | GET/POST | `admin_login` | Public |
| `/admin/logout/` | GET | `admin_logout` | Any logged-in |
| `/admin/` | GET | `admin_dashboard` | Admin or Data Moderator |
| `/admin/api/logs/` | GET | `api_logs` | Admin or Data Moderator |
| `/admin/api/run-script/` | POST | `api_run_script` | Admin only |
| `/admin/api/tables/` | GET | `api_tables` | Admin or Data Moderator |
| `/admin/api/tables/<name>/columns/` | GET | `api_table_columns` | Admin or Data Moderator |
| `/admin/api/insert/` | POST | `api_insert` | Admin or Data Moderator |
| `/admin/api/users/` | GET/POST | `api_users_list` | Admin only |
| `/admin/api/users/<id>/` | PUT/DELETE | `api_user_detail` | Admin only |

---

## 4. Admin API Endpoints

### `GET /admin/api/logs/?lines=200`
Returns last N lines from `BackEnd/log.txt` plus any in-memory script output.
```json
{"lines": ["[2026-03-15 14:30:00] Data fetched...", ...], "running": false, "exit_code": 0}
```

### `POST /admin/api/run-script/`
Runs a backend command in a background thread. Body: `{"command": "listAllSources"}`. Returns `{"status": "started"}` or `{"status": "already_running"}`.

### `GET /admin/api/tables/`
Lists all tables in `Measurements.db`: `{"tables": ["cocorahs", "dam", "mesonet", ...]}`

### `GET /admin/api/tables/<name>/columns/`
Returns column metadata: `{"table": "dam", "columns": [{"name": "elevation", "type": "FLOAT", ...}]}`

### `POST /admin/api/insert/`
Inserts a row. Body: `{"table": "dam", "data": {"location": "Oahe", "elevation": 1615.5, "datetime": "2026-03-15"}}`. Logs the insert to `BackEnd/log.txt`.

### `GET /admin/api/users/`
Lists all users with role, active status, join date.

### `POST /admin/api/users/`
Creates a user. Body: `{"username": "jsmith", "password": "...", "email": "...", "role": "admin"|"data_moderator"}`.

### `PUT /admin/api/users/<id>/`
Updates email, role, password, active status. Cannot change your own role or deactivate yourself.

### `DELETE /admin/api/users/<id>/`
Deletes a user. Cannot delete yourself.

---

## 5. Configuration Deep Dive

### `settings.py` — Key Settings to Modify

**`DEBUG`** — Set to `True` for local dev (shows tracebacks). Set to `False` for production.

**`ALLOWED_HOSTS`** — Must include any domain/IP the server runs on:
```python
ALLOWED_HOSTS = [
    'standing-rock-dev-buduamfpfuafaqdw.eastus-01.azurewebsites.net',
    '127.0.0.1', 'localhost',
    'standingrock-demo.azurewebsites.net',
    'standingrock-dashboard.azurewebsites.net',
]
```
If you deploy to a new domain, add it here AND to `CSRF_TRUSTED_ORIGINS`.

**`DATABASES`** — Django auth uses `db.sqlite3` at repo root. Measurement data is in `Measurements.db` (separate, accessed directly via `sqlite3` module in views).

**`STATIC_ROOT` / `STATICFILES_STORAGE`** — Uses WhiteNoise for serving static files in production. Run `python manage.py collectstatic` before deploying.

**`SECRET_KEY`** — Currently hardcoded and insecure. For production, use an environment variable.

### `BackEnd/SourceFiles/config.py` — Data Mappings

Three critical dictionaries:

- **`LOCATION_TO_TABLE`** — Maps location names to DB table names (e.g., `"Oahe" -> "dam"`, `"Fort Yates" -> "mesonet"`)
- **`SQL_CONVERSION`** — Maps display metric names to DB column names (e.g., `"Gauge Height" -> "gauge_height"`, `"Average Air Temperature" -> "avg_air_temp"`)
- **`DB_PATH`** — Path to `Measurements.db`

**To add a new location:** Add it to `LOCATION_TO_TABLE` and ensure its data exists in the corresponding DB table. The app also dynamically scans tables via `_scan_location_table_map()`, so if the table has a `location` column, new locations may appear automatically.

**To add a new metric:** Add the display name -> column name mapping to `SQL_CONVERSION`, and ensure the column exists in the DB table.

### User Roles

Implemented via Django's built-in auth:
- **Admin** — `is_staff=True` on the User model. Full access.
- **Data Moderator** — Member of the `"Data Moderator"` Django Group. Can view logs and insert data, but no user management or script execution.

---

## 6. Frontend Pages

### Home (`/`)
Landing page with hero section, two service cards (Interactive Map, Custom Graphs), and footer contact email.

### Interactive Map (`/map/`)
Full-screen Mapbox map with 28 color-coded markers:
- **Red** = Water Gauge (USGS) — river levels, flow, temperature
- **Blue** = Dam (USACE) — reservoir levels, dam flow
- **Green** = Weather Station (Mesonet) — air temp, humidity, rainfall

Clicking a marker opens a modal with tabbed data views (Chart/Table). Graphs are pre-generated HTML files served from `FrontEnd/static/graphs/`. The view function `interactiveMap()` scans that directory and matches filenames to place names.

### Custom Graph Dashboard (`/maptabs/`)
User selects location -> metric -> date range -> Generate. The form POSTs to `/generate_maptab_graph/` which queries `Measurements.db`, builds a Plotly graph, and returns it in an iframe. Also shows a statistics table (mean, SD, median, min, max, range).

**"Recent Data" button** — POSTs to `/get_latest_date/` to find the most recent data point for the selected location/metric, then auto-fills a 30-day window.

**Date quick-ranges:** Last 7 Days, Last 30 Days, YTD, Last 1 Year, Clear.

### About (`/about/`)
Two sections: Standing Rock Sioux Tribe info and EPICS HDR Purdue team info, with external links.

### Contact Us (`/contactus/`)
Form with Name, Email, Category (Comment/Concern), Message. Submit button enables only when all fields are filled. **Note: no backend handler exists — form submission does nothing.**

---

## 7. Admin Dashboard

### Login (`/admin/login/`)
Username + password authentication. Redirects to `/admin/` on success. Shows error on invalid credentials.

### Console Log Tab
Displays contents of `BackEnd/log.txt` plus any in-memory script output. Updates on manual "Update Log" click (no auto-polling).

- **"Run Updates" button** (Admin only) — Executes backend data-fetch commands via `BackEnd/commands.py` in a background thread. Shows "Script running..." status with animated indicator.
- **"Clear" button** — Clears the console display (not the log file).
- Error lines containing "error" or "exception" are highlighted.

### Data Entry Tab
Select a database table from dropdown -> dynamic form fields appear matching that table's columns (with type hints: FLOAT, INTEGER, TEXT). Click "Insert Row" to write to `Measurements.db`. All inserts are logged.

**Date format:** `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`

### User Control Tab (Admin Only)
Full CRUD for user accounts. Shows username, email, role badge (purple=Admin, blue=Data Moderator), active status, join date. Supports Add/Edit/Delete with modal dialogs. Safety constraints: cannot delete/deactivate yourself, cannot change your own role.

---

## 8. Data Sources & Database Schema

### `Measurements.db` Tables

| Table | Source | Key Columns |
|-------|--------|-------------|
| `gauge` | USGS | location, datetime, gauge_height, elevation, discharge, water_temp |
| `dam` | USACE | location, datetime, elevation, flow_spill, flow_power, flow_out, tail_ele, energy |
| `mesonet` | ND Mesonet | location, datetime, avg_air_temp, avg_rel_hum, total_rainfall, avg_bare_soil_temp, max_wind_speed, avg_dew_point |
| `noaa_weather` | NOAA | location, datetime, temperature, dew_point, rel_humidity, wind_chill |
| `cocorahs` | CoCoRaHS | location, datetime, precipitation, snowfall, snow_depth |
| `shadehill` | USACE | datetime, res_forebay_elev, daily_mean_tot_dis, daily_mean_air_temp, tot_precip_daily |
| `water_quality` | Various | location, datetime, ph, e_coli, total_nitrogen, total_phosphorus, etc. |
| `DANR` | SD DANR | location, datetime, various water quality metrics |

All tables use `location` (TEXT) + `datetime` (TEXT or epoch INTEGER) as the primary query dimensions.

### Datetime Storage

Tables store datetime in mixed formats — some as ISO strings (`2026-03-15T14:00:00`), some as Unix epoch integers. The code handles both via `get_time_format()` (checks if values are numeric) and `_parse_db_datetime()` (tries multiple parse strategies).

---

## 9. Custom Graph System

### Flow

1. User selects location + metric + dates on `/maptabs/`
2. Form POSTs to `/generate_maptab_graph/`
3. `_render_posted_graph()` is called, which calls `_render_graph_response()`
4. Location is resolved: first checks `_scan_location_table_map()` (dynamic DB scan), then falls back to `LOCATION_TO_TABLE` from config
5. Metric display name is converted to SQL column via `SQL_CONVERSION`
6. Data is queried via `custom_graph.query_data(conn, table, start_epoch, end_epoch)`
7. If no data found, it tries `_closest_window_epochs()` to find the nearest available data
8. Results are filtered by location, cleaned via `custom_graph._prepare_df_for_plot()`
9. Plotly `go.Scatter` trace is built and rendered as an HTML div
10. Stats table (mean, SD, median, min, max, range) is computed and appended

### Adding a New Graph Type

1. Add the metric column to the relevant DB table
2. Add the display name -> column name mapping to `SQL_CONVERSION` in `BackEnd/SourceFiles/config.py`
3. The metric will automatically appear in the Custom Graph Dashboard dropdown for locations in that table

### Adding a New Location

1. Insert data rows into the appropriate table in `Measurements.db` with the new location name in the `location` column
2. Optionally add it to `LOCATION_TO_TABLE` in config (the dynamic scanner will also pick it up)
3. For the interactive map: add the marker coordinates in `FrontEnd/static/js/map.js` and generate graph HTML files in `FrontEnd/static/graphs/`

---

## 10. Debugging & Troubleshooting

### Turning on Debug Mode

In `FrontEnd/config/settings.py`, set `DEBUG = True`. This shows full Django tracebacks in the browser instead of generic 500 pages. **Never leave this on in production.**

### Django Shell

```bash
python manage.py shell
```
Useful for inspecting the DB, testing queries, or resetting passwords:
```python
from django.contrib.auth.models import User
u = User.objects.get(username='admin')
u.set_password('newpassword')
u.save()
```

### Database Inspection

```bash
# Open Measurements.db directly
sqlite3 Measurements.db

# List tables
.tables

# Check a table's schema
.schema dam

# Sample data
SELECT * FROM dam WHERE location='Oahe' ORDER BY datetime DESC LIMIT 5;

# Check what locations exist
SELECT DISTINCT location FROM gauge;

# Check date range for a location/metric
SELECT MIN(datetime), MAX(datetime) FROM mesonet WHERE location='Fort Yates' AND avg_air_temp IS NOT NULL;
```

### Common Issues

#### "No data found" on graph generation
1. Check the location name matches exactly what's in the DB: `SELECT DISTINCT location FROM <table>;`
2. Check the metric column exists and has data: `SELECT COUNT(*) FROM <table> WHERE location='X' AND <column> IS NOT NULL;`
3. Check the date range overlaps with available data
4. Look for location name normalization issues — the app strips trailing state abbreviations (ND, SD) and does case-insensitive matching

#### Graph shows but is empty or has gaps
- Some tables store datetime as epoch, others as strings. Check `custom_graph.get_time_format()` is detecting correctly
- The `_parse_db_datetime()` function handles many formats but may fail on malformed entries. Check for entries like `2025-05-21T00:00:00 00:00:00` (duplicated time segments — the parser handles this but log it)
- Mesonet data can emit `24:00:00` timestamps — the parser rolls these to midnight of the next day

#### Admin "Run Script" stuck on "Running"
- The script runs in a background thread. If it hangs, the `_script_running` global stays `True`
- Restart the Django server to reset the flag
- Check `BackEnd/log.txt` for the last logged message to see where it got stuck

#### Admin login fails
- Verify the user exists: `python manage.py shell` -> `from django.contrib.auth.models import User; User.objects.all()`
- Check `is_staff=True` (for Admin) or membership in "Data Moderator" group
- Reset password via shell (see above)

#### Static files not loading (CSS/JS broken)
- In development: `DEBUG = True` handles static files automatically
- In production: run `python manage.py collectstatic` and ensure WhiteNoise middleware is in `MIDDLEWARE`
- Hard refresh browser: `Cmd+Shift+R` (Mac) / `Ctrl+Shift+R` (Windows)

#### Map not loading
- Mapbox requires an API access token hardcoded in `FrontEnd/static/js/map.js`. If the token expires, the map won't render — get a new one from Mapbox and update the JS file
- Requires internet access for map tiles

#### Config.py SyntaxError on import
- `BackEnd/SourceFiles/config.py` has (or had) a git merge conflict
- The app catches this with a `try/except SyntaxError` in `FrontEnd/services/views.py` and falls back to a hardcoded mock config
- Fix: resolve the merge conflict markers in config.py

#### Data insert logged but not visible on frontend
- The frontend queries `Measurements.db` directly. Data should appear after a page refresh
- If you inserted with wrong date format, the graph's date filter may exclude it. Use `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`
- Check the data availability indicator on the Custom Graph Dashboard — it shows the actual date range

#### "Cannot delete yourself" / "Cannot change your own role"
- These are intentional safety constraints in `api_user_detail()`. Use another admin account to modify your own.

### Logging

All admin actions are logged to `BackEnd/log.txt` with timestamps:
- `DATA INSERT by <username>: table="...", data={...}`
- `DATA INSERT ERROR by <username>: ...`
- `SCRIPT RUN by <username>: <command> started`

View logs in the admin Console Log tab or directly: `cat BackEnd/log.txt`

### Adding a New Admin User via Command Line

```bash
python manage.py createsuperuser
# Follow prompts for username, email, password
# This creates a user with is_staff=True (Admin role)
```

To create a Data Moderator via command line:
```python
# In python manage.py shell
from django.contrib.auth.models import User, Group
u = User.objects.create_user('moderator1', password='securepass')
g, _ = Group.objects.get_or_create(name='Data Moderator')
u.groups.add(g)
u.save()
```

---

## 11. Deployment

### Azure Web Apps

The app is deployed to Azure. Key settings:
- `ALLOWED_HOSTS` must include the Azure domain
- `CSRF_TRUSTED_ORIGINS` must include `https://` prefixed Azure domain
- `DEBUG = False`
- Run `python manage.py collectstatic` for WhiteNoise to serve static files
- WSGI entry point: `FrontEnd.config.wsgi.application`

Current Azure hosts:
- `standing-rock-dev-buduamfpfuafaqdw.eastus-01.azurewebsites.net`
- `standingrock-demo.azurewebsites.net`
- `standingrock-dashboard.azurewebsites.net`

### Firebase

Firebase config exists (`firebase.json`, `.firebaserc`) with project ID `standingrock-dashboard`, serving from `FrontEnd/` as public directory.

### Production Checklist

1. Set `DEBUG = False` in `settings.py`
2. Set a secure `SECRET_KEY` (use env variable)
3. Run `python manage.py collectstatic`
4. Verify `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` include your domain
5. Ensure `Measurements.db` is deployed alongside the code
6. Ensure `BackEnd/log.txt` directory is writable

---

## 12. Known Bugs & Limitations

- **Search typo in map.js** — Line 49 uses `searhTerm` instead of `searchTerm`. Searching for certain station names will throw a JS error.
- **Contact form has no backend** — The form renders but submission doesn't send data anywhere (no form action or email handler).
- **Forecast & Favorites pages** — Placeholder templates with no functionality.
- **Homepage/About images rely on external CDN** (`cdn.builder.io`). If CDN is down, images break.
- **Hardcoded Mapbox token** in `map.js` — will break if the token expires.
- **No "undo" for data entry** — Inserted data cannot be edited or deleted from the admin UI. Requires direct DB access.
- **SECRET_KEY is hardcoded** in `settings.py` — insecure for production.
- **`config.py` merge conflict fallback** — The app uses a mock config when the real one has syntax errors. This works but means some location/metric mappings may be incomplete.

---

*Last updated: April 9, 2026*
