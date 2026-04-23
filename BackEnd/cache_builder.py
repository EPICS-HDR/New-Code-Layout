"""Server-side cache builder for the Map and Custom Graph (maptabs) pages.

Produces a single JSON file with the metadata both pages need, so page loads
can skip the expensive `_scan_location_table_map()` and per-metric MIN/MAX
scans on database.db. Triggered manually from the admin dashboard.
"""
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import threading
import time
from datetime import datetime, timedelta

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(REPO_ROOT, 'BackEnd', 'cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'map_cache.json')

_write_lock = threading.Lock()


def _ensure_django():
    """Ensure Django is configured so we can import helpers from services.views."""
    import django
    from django.conf import settings as dj_settings
    if dj_settings.configured:
        return
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FrontEnd.config.settings')
    import sys
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    django.setup()


def _build_payload(built_by: str | None = None) -> dict:
    _ensure_django()
    from FrontEnd.services.views import (
        DB_PATH,
        TABLE_SCHEMA,
        LOCATION_TO_TABLE,
        SQL_CONVERSION,
        _scan_location_table_map,
        _get_location_col,
        _get_datetime_col,
        _quote_ident,
        _parse_db_datetime,
    )

    conn = sqlite3.connect(DB_PATH)
    try:
        location_table_map, _tables = _scan_location_table_map(conn)

        map_locations = _build_map_locations(conn, location_table_map, TABLE_SCHEMA, _quote_ident)
        maptabs_payload = _build_maptabs(
            conn,
            location_table_map,
            TABLE_SCHEMA,
            LOCATION_TO_TABLE,
            SQL_CONVERSION,
            _get_location_col,
            _get_datetime_col,
            _quote_ident,
            _parse_db_datetime,
        )
    finally:
        conn.close()

    return {
        'built_at': datetime.now().isoformat(timespec='seconds'),
        'built_by': built_by or '',
        'location_table_map': location_table_map,
        'map_locations': map_locations,
        'maptabs': maptabs_payload,
    }


def _build_map_locations(conn, location_table_map, TABLE_SCHEMA, _quote_ident):
    cur = conn.cursor()
    out = []
    for loc, table in location_table_map.items():
        schema = TABLE_SCHEMA.get(table, {})
        lat, lon = None, None

        if schema.get('hardcoded_coords') and loc in schema.get('hardcoded_coords', {}):
            lat, lon = schema['hardcoded_coords'][loc]
        elif schema.get('lat_col') and schema.get('lon_col'):
            lat_col = schema['lat_col']
            lon_col = schema['lon_col']
            loc_col = schema['location_col']
            try:
                cur.execute(
                    f"SELECT {_quote_ident(lat_col)}, {_quote_ident(lon_col)} "
                    f"FROM {_quote_ident(table)} WHERE {_quote_ident(loc_col)} = ? LIMIT 1",
                    (loc,),
                )
                row = cur.fetchone()
                if row and row[0] is not None and row[1] is not None:
                    if schema.get('lat_lon_swapped'):
                        lon, lat = float(row[0]), float(row[1])
                    else:
                        lat, lon = float(row[0]), float(row[1])
            except Exception:
                pass

        if lat is None or lon is None:
            continue

        datasets = list(schema.get('data_cols', {}).keys()) if 'data_cols' in schema else []
        out.append({
            'name': loc,
            'lat': lat,
            'lon': lon,
            'table': table,
            'datasets': datasets,
        })
    return out


def _build_maptabs(
    conn,
    location_table_map,
    TABLE_SCHEMA,
    LOCATION_TO_TABLE,
    SQL_CONVERSION,
    _get_location_col,
    _get_datetime_col,
    _quote_ident,
    _parse_db_datetime,
):
    curr = conn.cursor()
    locations = sorted(set(location_table_map.keys()))

    rev = {v: k for k, v in SQL_CONVERSION.items()}
    default_options = {
        'gauge': ['Gauge Height', 'Elevation', 'Discharge', 'Water Temperature'],
        'mesonet': ['Average Air Temperature', 'Average Relative Humidity', 'Total Rainfall'],
    }

    ignored_metric_columns = {
        'datetime', 'location', 'unique_id', 'id', 'date', 'sampleDate', 'DateTime',
        'meta.uid', 'meta.state', 'meta.elev', 'meta.name', 'latitude', 'longitude',
        'sid1', 'sid2', 'station_ID', 'aU_ID', 'sampleDepth', 'station.objectID',
        'station.stationId', 'station.latitude', 'station.longitude', 'station.auId',
        'station.waterbodyName', 'station.primaryType', 'station.type', 'Station',
    }

    location_options: dict[str, list[str]] = {}
    location_availability: dict[str, dict[str, dict[str, str | None]]] = {}

    for loc in locations:
        table_name = location_table_map.get(loc, LOCATION_TO_TABLE.get(loc, 'gauge'))
        loc_col = _get_location_col(table_name)
        dt_col = _get_datetime_col(table_name)

        if table_name in TABLE_SCHEMA and 'data_cols' in TABLE_SCHEMA[table_name]:
            data_cols = TABLE_SCHEMA[table_name]['data_cols']
            opts = list(data_cols.keys())
            availability_for_loc: dict[str, dict[str, str | None]] = {}
            for display_name, sql_col in data_cols.items():
                earliest, latest = _min_max_dates(
                    curr, table_name, loc_col, dt_col, sql_col, loc, _quote_ident, _parse_db_datetime
                )
                availability_for_loc[display_name] = {'start': earliest, 'end': latest}
        else:
            try:
                curr.execute(f"PRAGMA table_info({_quote_ident(table_name)})")
                cols = [r[1] for r in curr.fetchall()]
            except Exception:
                cols = []

            opts = []
            availability_for_loc = {}
            for c in cols:
                if c in ignored_metric_columns:
                    continue
                earliest, latest = _min_max_dates(
                    curr, table_name, loc_col, dt_col, c, loc, _quote_ident, _parse_db_datetime
                )
                display_name = rev[c] if c in rev else c.replace('_', ' ').title()
                opts.append(display_name)
                availability_for_loc[display_name] = {'start': earliest, 'end': latest}

            if not opts:
                opts = default_options.get(table_name, ['Value'])

        location_options[loc] = opts
        location_availability[loc] = availability_for_loc

    table_to_endpoint = {
        'gauge': ('/customgaugegraph/', 'location'),
        'mesonet': ('/custommesonetgraph/', 'mesonet'),
        'cocorahs': ('/customcocograph/', 'cocorahs'),
        'COCORAHS': ('/generate_maptab_graph/', 'location'),
        'DANR': ('/generate_maptab_graph/', 'location'),
        'USACE': ('/generate_maptab_graph/', 'location'),
        'shadehill': ('/customshadehillgraph/', None),
        'noaa_weather': ('/customnoaagraph/', 'noaa'),
    }

    display_location_options: dict[str, list[str]] = {}
    display_location_table_map: dict[str, str] = {}
    location_entries: list[dict] = []
    for loc, opts in location_options.items():
        if loc and loc.isdigit():
            continue
        table = location_table_map.get(loc, LOCATION_TO_TABLE.get(loc, 'gauge'))
        endpoint, input_name = table_to_endpoint.get(table, ('/customgaugegraph/', 'location'))
        display_location_options[loc] = opts
        display_location_table_map[loc] = table
        location_entries.append({
            'location': loc,
            'metrics': opts,
            'endpoint': endpoint,
            'input_name': input_name,
        })

    today = datetime.utcnow().date()
    return {
        'location_entries': location_entries,
        'display_location_options': display_location_options,
        'display_location_table_map': display_location_table_map,
        'location_availability': location_availability,
        'default_start': (today - timedelta(days=30)).isoformat(),
        'default_end': today.isoformat(),
    }


def _min_max_dates(curr, table_name, loc_col, dt_col, sql_col, loc, _quote_ident, _parse_db_datetime):
    try:
        curr.execute(
            f"SELECT MIN({_quote_ident(dt_col)}), MAX({_quote_ident(dt_col)}) "
            f"FROM {_quote_ident(table_name)} "
            f"WHERE {_quote_ident(loc_col)} = ? AND {_quote_ident(sql_col)} IS NOT NULL",
            (loc,),
        )
        min_max = curr.fetchone() or (None, None)
    except Exception:
        return None, None
    earliest_dt = _parse_db_datetime(min_max[0])
    latest_dt = _parse_db_datetime(min_max[1])
    earliest = earliest_dt.date().isoformat() if earliest_dt else None
    latest = latest_dt.date().isoformat() if latest_dt else None
    return earliest, latest


def write_cache(payload: dict) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    with _write_lock:
        fd, tmp_path = tempfile.mkstemp(prefix='map_cache.', suffix='.tmp', dir=CACHE_DIR)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(payload, f)
            os.replace(tmp_path, CACHE_FILE)
        except Exception:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise


def refresh_map_cache(built_by: str | None = None) -> str:
    """Rebuild the cache file and return a one-line summary."""
    start = time.time()
    payload = _build_payload(built_by=built_by)
    write_cache(payload)
    elapsed = time.time() - start
    n_locs = len(payload.get('map_locations', []))
    n_entries = len(payload.get('maptabs', {}).get('location_entries', []))
    return (
        f"Wrote {n_locs} map locations, {n_entries} maptab entries to "
        f"{os.path.relpath(CACHE_FILE, REPO_ROOT)} in {elapsed:.2f}s"
    )


if __name__ == '__main__':
    print(refresh_map_cache(built_by='cli'))
