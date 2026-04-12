"""
Export Measurements.db into JSON files for the static Firebase frontend.

Produces:
  FrontEnd/static/data/manifest.json   — location/metric metadata
  FrontEnd/static/data/<table>__<location>.json — time-series per location

Usage:
  python export_static_data.py
"""

import json
import os
import re
import sqlite3
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(REPO_ROOT, 'Measurements.db')
OUT_DIR = os.path.join(REPO_ROOT, 'FrontEnd', 'static', 'data')

# Tables to export (skip temp_staging and DANR which has no location/datetime)
TABLES = ['cocorahs', 'shadehill', 'water_quality', 'noaa_weather', 'usgs', 'mesonet']

IGNORED_COLS = {'unique_id', 'id', 'datetime', 'location'}

# Human-readable names for SQL columns (reverse of SQL_CONVERSION)
DISPLAY_NAMES = {
    "elevation": "Elevation",
    "air_temp": "Air Temperature",
    "water_temp": "Water Temperature",
    "flow_spill": "Flow Spill",
    "flow_power": "Flow Powerhouse",
    "flow_out": "Flow Out",
    "tail_ele": "Tailwater Elevation",
    "energy": "Energy",
    "discharge": "Discharge",
    "gauge_height": "Gauge Height",
    "avg_air_temp": "Average Air Temperature",
    "avg_rel_hum": "Average Relative Humidity",
    "avg_bare_soil_temp": "Average Bare Soil Temperature",
    "avg_turf_soil_temp": "Average Turf Soil Temperature",
    "max_wind_speed": "Maximum Wind Speed",
    "avg_wind_dir": "Average Wind Direction",
    "total_solar_rad": "Total Solar Radiation",
    "total_rainfall": "Total Rainfall",
    "avg_bar_pressure": "Average Barometric Pressure",
    "avg_dew_point": "Average Dew Point",
    "avg_wind_chill": "Average Wind Chill",
    "precipitation": "Precipitation",
    "snowfall": "Snowfall",
    "snow_depth": "Snow Depth",
    "res_stor_content": "Reservoir Storage Content",
    "res_forebay_elev": "Reservoir Forebay Elevation",
    "daily_mean_comp_inflow": "Daily Mean Computed Inflow",
    "daily_mean_air_temp": "Daily Mean Air Temperature",
    "daily_min_air_temp": "Daily Minimum Air Temperature",
    "daily_max_air_temp": "Daily Maximum Air Temperature",
    "tot_precip_daily": "Total Precipitation (inches per day)",
    "tot_year_precip": "Total Water Year Precipitation",
    "daily_mean_tot_dis": "Daily Mean Total Discharge",
    "daily_mean_river_dis": "Daily Mean River Discharge",
    "daily_mean_spill_dis": "Daily Mean Spillway Discharge",
    "daily_mean_gate_opening": "Daily Mean Gate One Opening",
    "avg_temp": "Average Temperature",
    "max_temp": "Max Temperature",
    "min_temp": "Min Temperature",
    "total_phosphorus": "Phosphorus (Total) (P)",
    "total_kjeldahl_nitrogen": "Nitrogen (Total Kjeldahl)",
    "nitrate_nitrite": "Nitrate + Nitrite (N)",
    "total_nitrogen": "Total Nitrogen",
    "ammonia_nitrogen": "Ammonia (N)",
    "ammonia_nitrogen_dissolved": "Ammonia (N)-Dissolved",
    "dissolved_phosphorus": "Dissolved Phosphorus as P",
    "nitrate_nitrite_dissolved": "Nitrate + Nitrite (N) Dis",
    "tkn_dissolved": "Nitrogen (TKN-Dissolved)",
    "total_nitrogen_dissolved": "Nitrogen (Total-Dis)",
    "e_coli": "E.coli",
    "ph": "pH",
}


def safe_filename(s):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', s).strip('_')


def parse_datetime(value):
    """Parse a datetime value (epoch or string) into an ISO date string."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(int(value)).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return None
    raw = str(value).strip()
    # Handle duplicated time segments
    m = re.match(r'^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', raw)
    if m:
        raw = m.group(1)
    # Handle mesonet 24:00:00
    rolled = re.match(r'^(\d{4}-\d{2}-\d{2})[T ]24:00:00$', raw)
    if rolled:
        try:
            from datetime import timedelta
            next_day = datetime.strptime(rolled.group(1), '%Y-%m-%d') + timedelta(days=1)
            return next_day.strftime('%Y-%m-%d 00:00:00')
        except Exception:
            pass
    return raw


def try_float(v):
    """Try to convert a value to float, return None on failure."""
    if v is None:
        return None
    try:
        f = float(v)
        if f != f:  # NaN check
            return None
        return f
    except (TypeError, ValueError):
        return None


def export():
    os.makedirs(OUT_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    manifest_locations = []

    for table in TABLES:
        # Get columns
        cur.execute(f'PRAGMA table_info("{table}")')
        all_cols = [r[1] for r in cur.fetchall()]
        data_cols = [c for c in all_cols if c not in IGNORED_COLS]

        if 'location' not in all_cols:
            print(f'  Skipping {table} (no location column)')
            continue

        # Get distinct locations
        cur.execute(f'SELECT DISTINCT location FROM "{table}" WHERE location IS NOT NULL ORDER BY location')
        locations = [r[0] for r in cur.fetchall() if r[0] and r[0].strip()]

        for loc in locations:
            # Skip numeric-only locations (USGS station codes) and test data
            if loc.isdigit() or loc.lower().startswith('test'):
                continue

            # Query all data for this location, ordered by datetime
            col_list = ', '.join(f'"{c}"' for c in data_cols)
            cur.execute(
                f'SELECT datetime, {col_list} FROM "{table}" WHERE location = ? ORDER BY datetime ASC',
                (loc,)
            )
            rows = cur.fetchall()

            if not rows:
                continue

            # Build column arrays
            columns = {}
            metric_info = []
            for i, col in enumerate(data_cols):
                dates = []
                values = []
                for row in rows:
                    dt = parse_datetime(row[0])
                    val = try_float(row[i + 1])
                    if dt is not None and val is not None:
                        dates.append(dt)
                        values.append(round(val, 4))

                if not dates:
                    continue

                display_name = DISPLAY_NAMES.get(col, col.replace('_', ' ').title())
                columns[col] = {
                    'dates': dates,
                    'values': values,
                }
                metric_info.append({
                    'column': col,
                    'display_name': display_name,
                    'start': dates[0][:10],
                    'end': dates[-1][:10],
                    'count': len(dates),
                })

            if not columns:
                continue

            # Write location data file
            fname = f'{safe_filename(table)}__{safe_filename(loc)}.json'
            fpath = os.path.join(OUT_DIR, fname)
            with open(fpath, 'w') as f:
                json.dump({
                    'location': loc,
                    'table': table,
                    'columns': columns,
                }, f, separators=(',', ':'))

            print(f'  Wrote {fname} ({len(rows)} rows, {len(columns)} metrics)')

            manifest_locations.append({
                'location': loc,
                'table': table,
                'file': fname,
                'metrics': metric_info,
            })

    # Write manifest
    manifest = {
        'generated': datetime.now().isoformat(),
        'locations': manifest_locations,
    }
    manifest_path = os.path.join(OUT_DIR, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    conn.close()

    print(f'\nDone. Exported {len(manifest_locations)} location files + manifest.json to {OUT_DIR}')


if __name__ == '__main__':
    export()
