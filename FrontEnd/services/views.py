'''
Author: Fenix Do
Date: 03/28/2026
Purpose: Coordinates backend Django processing, returning proper HTML templates or JSON endpoints.
'''
import json
import math
import os
import re
import sqlite3
import statistics
from datetime import datetime, timedelta

import plotly.graph_objs as go
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import render
from plotly.offline import plot

import sys
import types

try:
    from BackEnd.SourceFiles.config import DB_PATH as CONFIG_DB_PATH, LOCATION_TO_TABLE, SQL_CONVERSION
except SyntaxError:
    # config.py has a git merge conflict, so we catch the SyntaxError and define the mappings locally.
    mock_config = types.ModuleType('BackEnd.SourceFiles.config')
    mock_config.DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'database.db')
    mock_config.LOCATION_TO_TABLE = {
        "Big Bend": "dam", "Fort Randall": "dam", "Gavins Point": "dam", "Garrison": "dam", "Fort Peck": "dam",
        "Bison": "cocorahs", "Faulkton": "cocorahs", "Langdon": "cocorahs", "Shadehill": "shadehill",
        "Bismarck": "noaa_weather", "Williston/Basin": "noaa_weather", "Minot": "noaa_weather",
        "Fort Yates": "mesonet", "Linton": "mesonet", "Mott": "mesonet", "Carson": "mesonet",
    }
    mock_config.SQL_CONVERSION = {
        "Elevation": "elevation", "Air Temperature": "air_temp", "Water Temperature": "water_temp", "Flow Spill": "flow_spill", "Flow Powerhouse": "flow_power", "Flow Out": "flow_out", "Tailwater Elevation": "tail_ele", "Energy": "energy", "Discharge": "discharge", "Gauge Height": "gauge_height", "Average Air Temperature": "avg_air_temp", "Average Relative Humidity": "avg_rel_hum", "Average Bare Soil Temperature": "avg_bare_soil_temp", "Average Turf Soil Temperature": "avg_turf_soil_temp", "Maximum Wind Speed": "max_wind_speed", "Average Wind Direction": "avg_wind_dir", "Total Solar Radiation": "total_solar_rad", "Total Rainfall": "total_rainfall", "Average Baromatric Pressure": "avg_bar_pressure", "Average Dew Point": "avg_dew_point", "Average Wind Chill": "avg_wind_chill", "Precipitation": "precipitation", "Snowfall": "snowfall", "Snow Depth": "snow_depth", "Reservoir Storage Content": "res_stor_content", "Reservoir Forebay Elevation": "res_forebay_elev", "Daily Mean Computed Inflow": "daily_mean_comp_inflow", "Daily Mean Air Temperature": "daily_mean_air_temp", "Daily Minimum Air Temperature": "daily_min_air_temp", "Daily Maximum Air Temperature": "daily_max_air_temp", "Total Precipitation (inches per day)": "tot_precip_daily", "Total Water Year Precipitation": "tot_year_precip", "Daily Mean Total Discharge": "daily_mean_tot_dis", "Daily Mean River Discharge": "daily_mean_river_dis", "Daily Mean Spillway Discharge": "daily_mean_spill_dis", "Daily Mean Gate One Opening": "daily_mean_gate_opening", "temperature": "temperature", "dewpoint": "dew_point", "relativeHumidity": "rel_humidity", "windChill": "wind_chill", "Average Temperature": "avg_temp", "Max Temperature": "max_temp", "Min Temperature": "min_temp", "Phosphorus (Total) (P)": "total_phosphorus", "Phosphorus (Total Kjeldahl) (P)": "total_kjeldahl_phosphorus", "Nitrate + Nitrite (N)": "nitrate_nitrite", "Nitrate Forms Check": "nitrate_forms_check", "Nitrate + Nitrite (N) Dis": "nitrate_nitrite_dissolved", "Nitrogen (Total Kjeldahl)": "total_kjeldahl_nitrogen", "Nitrogen (TKN-Dissolved)": "tkn_dissolved", "Nitrogen (Total-Dis)": "total_nitrogen_dissolved", "E.coli": "e_coli", "Nitrogen (Total)": "total_nitrogen", "pH": "ph", "Ammonia (N)": "ammonia_nitrogen", "Ammonia (N)-Dissolved": "ammonia_nitrogen_dissolved", "Ammonia Forms Check": "ammonia_forms_check", "Diss Ammonia TKN Check": "diss_ammonia_tkn_check", "Dissolved Phosphorus as P": "dissolved_phosphorus",
    }
    sys.modules['BackEnd.SourceFiles.config'] = mock_config
    CONFIG_DB_PATH = mock_config.DB_PATH
    LOCATION_TO_TABLE = mock_config.LOCATION_TO_TABLE
    SQL_CONVERSION = mock_config.SQL_CONVERSION

from BackEnd import custom_graph

DB_PATH = os.fspath(getattr(settings, 'MEASUREMENTS_DB_PATH', CONFIG_DB_PATH))

# Schema config for tables in database.db that use non-standard column names.
# lat_lon_swapped=True means the DB column named 'latitude' actually holds longitude and vice versa.
TABLE_SCHEMA = {
    'COCORAHS': {
        'location_col': 'meta.name',
        'datetime_col': 'date',
        'lat_col': 'latitude',
        'lon_col': 'longitude',
        'lat_lon_swapped': True,
        'data_cols': {
            'Max Temperature': 'v1',
            'Min Temperature': 'v2',
            'Average Temperature': 'v3',
            'Observed Temperature': 'v4',
            'Precipitation': 'v5',
            'Snowfall': 'v6',
            'Snow Depth': 'v7',
        },
    },
    'DANR': {
        'location_col': 'station.stationId',
        'datetime_col': 'sampleDate',
        'lat_col': 'station.latitude',
        'lon_col': 'station.longitude',
        'lat_lon_swapped': False,
        'data_cols': {
            'Water Temperature': 'waterTemperature',
            'Dissolved Oxygen': 'dissolvedOxygen',
            'pH': 'pH',
            'Specific Conductance': 'specificConductance',
            'TSS': 'tss',
            'TKN': 'tkn',
            'Ammonia': 'ammonia',
            'Nitrate/Nitrite': 'nitrateNitrite',
            'Total Phosphorus': 'tp',
            'E.coli': 'eColi',
            'Chlorophyll Alpha': 'chlorophyllAlpha',
        },
    },
    'USACE': {
        'location_col': 'Station',
        'datetime_col': 'DateTime',
        'lat_col': None,
        'lon_col': None,
        'lat_lon_swapped': False,
        'hardcoded_coords': {'GARR': (47.4988, -101.4194)},
        'data_cols': {
            'Elevation': 'Elev',
            'Air Temperature': 'Temp_Air',
            'Water Temperature': 'Temp_Water',
            'Flow Out': 'Flow_Out',
            'Flow Spill': 'Flow_Spill',
            'Flow Powerhouse': 'Flow_Powerhouse',
            'Tailwater Elevation': 'Elev_Tailwater',
            'Energy': 'Energy',
        },
    },
}


def _get_location_col(table_name: str) -> str:
    return TABLE_SCHEMA.get(table_name, {}).get('location_col', 'location')


def _get_datetime_col(table_name: str) -> str:
    return TABLE_SCHEMA.get(table_name, {}).get('datetime_col', 'datetime')


def _quote_ident(name: str) -> str:
    return '"' + (name or '').replace('"', '""') + '"'


def _list_db_tables(conn):
    curr = conn.cursor()
    curr.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )
    return [r[0] for r in curr.fetchall() if r and r[0]]


def _table_columns(conn, table_name):
    curr = conn.cursor()
    curr.execute(f"PRAGMA table_info({_quote_ident(table_name)})")
    return [r[1] for r in curr.fetchall() if len(r) > 1]


def _scan_location_table_map(conn):
    """Discover location->table mapping. Handles both standard 'location' column
    and the alternate location columns defined in TABLE_SCHEMA."""
    location_table_map = {}
    tables = []
    ignored_tables = {'temp_staging'}
    for table_name in _list_db_tables(conn):
        if table_name in ignored_tables or table_name.lower().startswith(('temp_', 'staging_')):
            continue
        try:
            cols = _table_columns(conn, table_name)
        except Exception:
            continue

        loc_col = None
        if 'location' in cols:
            loc_col = 'location'
        elif table_name in TABLE_SCHEMA:
            alt = TABLE_SCHEMA[table_name].get('location_col')
            if alt and alt in cols:
                loc_col = alt

        if loc_col is None:
            continue

        tables.append(table_name)
        try:
            curr = conn.cursor()
            curr.execute(
                f"SELECT DISTINCT {_quote_ident(loc_col)} FROM {_quote_ident(table_name)} "
                f"WHERE {_quote_ident(loc_col)} IS NOT NULL"
            )
            for r in curr.fetchall():
                if not r:
                    continue
                loc = (r[0] or '').strip()
                if not loc:
                    continue
                if loc not in location_table_map:
                    location_table_map[loc] = table_name
        except Exception:
            continue
    return location_table_map, tables

def health(request):
    return HttpResponse("OK")


def favorites(request):
    favorites = []
    if request.user.is_authenticated:
        favorites = request.user.favorites.all()
    return render(request, 'HTML/favorites.html', {"favorites": favorites})

def contactus(request):
    return render(request,'HTML/contactus.html')

def about(request):
    return render(request, 'HTML/about.html')

def forecast(request):
    return render(request, 'HTML/forecast.html')

def homepage(request):
    return render(request, 'HTML/homepage.html')


def _display_metric_to_sql_column(metric_name: str) -> str:
    # Check SQL_CONVERSION first, then check TABLE_SCHEMA data_cols mappings.
    col = SQL_CONVERSION.get(metric_name)
    if col:
        return col
    for schema in TABLE_SCHEMA.values():
        data_cols = schema.get('data_cols', {})
        if metric_name in data_cols:
            return data_cols[metric_name]
    return metric_name.replace(' ', '_').lower()


def _normalize_metric_name(metric_name: str) -> str:
    # Some forms still send values like `Flow_Spill`.
    if '_' in metric_name:
        parts = metric_name.split('_')
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"
    return metric_name


def _canonical_location_name(loc: str) -> str:
    if not loc:
        return ''
    l = (loc or '').strip()
    # Normalize punctuation/casing and remove common trailing state tags.
    l = re.sub(r',', '', l)
    l = re.sub(r"\s+(ND|SD|NORTH\s+DAKOTA|SOUTH\s+DAKOTA)$", '', l, flags=re.IGNORECASE)
    return ' '.join(l.lower().split())


def _resolve_location_name(loc: str, location_table_map):
    """Resolve user-posted location text to the closest known DB location key."""
    if not loc:
        return loc
    if loc in location_table_map:
        return loc

    canon = _canonical_location_name(loc)
    if not canon:
        return loc

    for known in location_table_map.keys():
        if _canonical_location_name(known) == canon:
            return known

    return loc


def _to_epoch(date_str):
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str)
    except Exception:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp())


def _parse_db_datetime(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(int(value))
        except Exception:
            return None
    raw = str(value).strip()
    candidates = [raw]

    # Some rows contain duplicated time segments like
    # `2025-05-21T00:00:00 00:00:00`; keep the leading timestamp portion.
    match = re.match(r'^(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})', raw)
    if match:
        candidates.insert(0, match.group(1))

    if ' ' in raw and 'T' in raw:
        candidates.insert(0, raw.split()[0])

    # Mesonet can emit `24:00:00` to represent midnight of the next day.
    rolled = re.match(r'^(\d{4}-\d{2}-\d{2})([T\s])24:00:00$', raw)
    if rolled:
        try:
            next_day = datetime.strptime(rolled.group(1), "%Y-%m-%d") + timedelta(days=1)
            candidates.insert(0, next_day.strftime(f"%Y-%m-%d{rolled.group(2)}00:00:00"))
        except Exception:
            pass

    for candidate in candidates:
        try:
            return datetime.fromisoformat(candidate.replace('Z', '+00:00'))
        except Exception:
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(candidate, fmt)
                except Exception:
                    continue
    return None


def _closest_window_epochs(conn, table_name, col, loc, target_end_epoch):
    """Find a closest available datetime for location/metric and return a 30-day epoch window."""
    try:
        table_cols = _table_columns(conn, table_name)
        loc_col = _get_location_col(table_name)
        dt_col = _get_datetime_col(table_name)
        has_location_col = loc_col in table_cols
        if col not in table_cols:
            return None, None

        target_epoch = target_end_epoch or int(datetime.now().timestamp())

        where_parts = [f"{_quote_ident(col)} IS NOT NULL"]
        params = []
        if has_location_col:
            where_parts.append(f"{_quote_ident(loc_col)} = ?")
            params.append(loc)

        target_value = datetime.fromtimestamp(target_epoch).strftime("%Y-%m-%d %H:%M:%S")
        where_clause = ' AND '.join(where_parts)
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT MAX({_quote_ident(dt_col)}) FROM {_quote_ident(table_name)} "
            f"WHERE {where_clause} AND {_quote_ident(dt_col)} <= ?",
            params + [target_value],
        )
        left = cursor.fetchone()[0]

        cursor.execute(
            f"SELECT MIN({_quote_ident(dt_col)}) FROM {_quote_ident(table_name)} "
            f"WHERE {where_clause} AND {_quote_ident(dt_col)} >= ?",
            params + [target_value],
        )
        right = cursor.fetchone()[0]

        left_dt = _parse_db_datetime(left)
        right_dt = _parse_db_datetime(right)
        target_dt = datetime.fromtimestamp(target_epoch)

        if left_dt and right_dt:
            anchor_dt = left_dt if abs((target_dt - left_dt).total_seconds()) <= abs((right_dt - target_dt).total_seconds()) else right_dt
        else:
            anchor_dt = left_dt or right_dt

        if not anchor_dt:
            return None, None

        end_e = int(anchor_dt.timestamp())
        start_e = end_e - 30 * 24 * 3600
        return start_e, end_e
    except Exception:
        return None, None


def _load_direct_series(conn, table_name, col, loc, *, start_epoch=None, end_epoch=None):
    """Directly load datetime/value rows for a location+metric, handling both standard
    and TABLE_SCHEMA-defined column names."""
    try:
        table_cols = _table_columns(conn, table_name)
        if col not in table_cols:
            return None

        loc_col = _get_location_col(table_name)
        dt_col = _get_datetime_col(table_name)
        has_location_col = loc_col in table_cols

        selected_cols = [dt_col, col] + ([loc_col] if has_location_col else [])
        where_parts = [f"{_quote_ident(col)} IS NOT NULL"]
        params = []

        if has_location_col:
            where_parts.append(f"{_quote_ident(loc_col)} = ?")
            params.append(loc)

        if start_epoch is not None and end_epoch is not None:
            start_dt = datetime.fromtimestamp(start_epoch).strftime('%Y-%m-%d %H:%M:%S')
            end_dt = datetime.fromtimestamp(end_epoch).strftime('%Y-%m-%d %H:%M:%S')
            where_parts.append(f"{_quote_ident(dt_col)} BETWEEN ? AND ?")
            params.extend([start_dt, end_dt])

        query = (
            f"SELECT {', '.join(_quote_ident(c) for c in selected_cols)} "
            f"FROM {_quote_ident(table_name)} WHERE {' AND '.join(where_parts)} "
            f"ORDER BY {_quote_ident(dt_col)} ASC"
        )
        df = custom_graph.pd.read_sql_query(query, conn, params=params)
        if df is not None and not df.empty:
            rename = {}
            if dt_col != 'datetime' and dt_col in df.columns:
                rename[dt_col] = 'datetime'
            if loc_col != 'location' and loc_col in df.columns:
                rename[loc_col] = 'location'
            if rename:
                df = df.rename(columns=rename)
            # Coerce numeric columns (e.g. COCORAHS uses 'M' for missing)
            if col in df.columns:
                df[col] = custom_graph.pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception:
        return None


def _post_graph_window(request):
    return (
        _to_epoch(request.POST.get('start-date', '')),
        _to_epoch(request.POST.get('end-date', '')),
    )


def _render_posted_graph(
    request,
    *,
    location_field='location',
    fallback_table='gauge',
    fixed_locations=None,
    include_diagnostics=False,
    fallback_to_recent_window=False,
):
    locations = fixed_locations if fixed_locations is not None else request.POST.getlist(location_field)
    metric_name = _normalize_metric_name(request.POST.get('data2see', ''))
    start_epoch, end_epoch = _post_graph_window(request)

    return _render_graph_response(
        request,
        locations,
        metric_name,
        fallback_table,
        start_epoch=start_epoch,
        end_epoch=end_epoch,
        fallback_to_recent_window=fallback_to_recent_window,
        include_diagnostics=include_diagnostics,
    )


def _build_stats_table_html(sites, series_list):
    rows = []
    for idx, (_, values) in enumerate(series_list):
        vals = []
        for v in values:
            if v is None:
                continue
            try:
                fv = float(v)
            except (TypeError, ValueError):
                continue
            if math.isnan(fv):
                continue
            vals.append(fv)
        if not vals:
            rows.append({'site': sites[idx], 'mean': '', 'sd': '', 'median': '', 'min': '', 'max': '', 'range': ''})
            continue
        mean = round(statistics.mean(vals), 3)
        sd = round(statistics.pstdev(vals), 3) if len(vals) > 1 else 0.0
        med = round(statistics.median(vals), 3)
        mn = round(min(vals), 3)
        mx = round(max(vals), 3)
        rg = round(mx - mn, 3)
        rows.append({'site': sites[idx], 'mean': mean, 'sd': sd, 'median': med, 'min': mn, 'max': mx, 'range': rg})

    table_html = '<table class="stats"><tr><th>Site</th><th>Mean</th><th>SD</th><th>Median</th><th>Min</th><th>Max</th><th>Range</th></tr>'
    for r in rows:
        table_html += (
            f"<tr><td>{r['site']}</td><td>{r['mean']}</td><td>{r['sd']}</td>"
            f"<td>{r['median']}</td><td>{r['min']}</td><td>{r['max']}</td><td>{r['range']}</td></tr>"
        )
    table_html += '</table>'
    return table_html


def _build_no_data_diagnostics(conn, sites, fallback_table, location_table_map):
    diag = '<p>No data available for selected stations/date range.</p>'
    diag += '<h4>Diagnostics</h4>'
    diag += '<table class="stats"><tr><th>Site</th><th>Rows</th><th>Min Datetime</th><th>Max Datetime</th><th>Non-empty Columns</th></tr>'
    for loc in sites:
        try:
            curr = conn.cursor()
            table_name = location_table_map.get(loc, LOCATION_TO_TABLE.get(loc, fallback_table))
            curr.execute(f'SELECT count(*) FROM {_quote_ident(table_name)} WHERE location=?', (loc,))
            total = curr.fetchone()[0]

            try:
                curr.execute(f'SELECT MIN(datetime), MAX(datetime) FROM {_quote_ident(table_name)} WHERE location=?', (loc,))
                mn_mx = curr.fetchone()
                mn = mn_mx[0]
                mx = mn_mx[1]
            except Exception:
                mn = mx = None

            nonempty = []
            try:
                curr.execute(f'PRAGMA table_info({_quote_ident(table_name)})')
                cols = [r[1] for r in curr.fetchall()]
                for c in cols:
                    if c in ('datetime', 'location'):
                        continue
                    try:
                        curr.execute(
                            f'SELECT count(*) FROM {_quote_ident(table_name)} '
                            f'WHERE location=? AND {_quote_ident(c)} IS NOT NULL',
                            (loc,),
                        )
                        cnt = curr.fetchone()[0]
                        if cnt and cnt > 0:
                            nonempty.append(f'{c} ({cnt})')
                    except Exception:
                        continue
            except Exception:
                nonempty = []
            diag += f"<tr><td>{loc}</td><td>{total}</td><td>{mn or ''}</td><td>{mx or ''}</td><td>{', '.join(nonempty)}</td></tr>"
        except Exception as e:
            diag += f"<tr><td>{loc}</td><td colspan=4>Error: {e}</td></tr>"
    diag += '</table>'
    return diag


def _render_graph_response(
    request,
    locations,
    metric_name,
    fallback_table,
    *,
    start_epoch=None,
    end_epoch=None,
    fallback_to_recent_window=False,
    fallback_to_closest_window=True,
    include_diagnostics=False,
):
    sites = []
    series_list = []
    col = _display_metric_to_sql_column(metric_name)

    conn = sqlite3.connect(DB_PATH)
    try:
        location_table_map, _ = _scan_location_table_map(conn)
        source_tables = []
        for raw_loc in locations:
            posted_loc = _normalize_posted_location(raw_loc)
            loc = _resolve_location_name(posted_loc, location_table_map)
            sites.append(loc)
            table_name = location_table_map.get(loc, LOCATION_TO_TABLE.get(loc, fallback_table))
            source_tables.append(table_name)

            if fallback_to_recent_window and (start_epoch is None or end_epoch is None):
                latest_dt = custom_graph.get_latest_datetime(conn, table_name, col)
                if latest_dt:
                    end_e = int(latest_dt.timestamp())
                    start_e = end_e - 30 * 24 * 3600
                else:
                    now_ts = int(datetime.now().timestamp())
                    end_e = now_ts
                    start_e = now_ts - 30 * 24 * 3600
            else:
                start_e = start_epoch
                end_e = end_epoch

            if table_name in TABLE_SCHEMA:
                df = _load_direct_series(conn, table_name, col, loc,
                                         start_epoch=start_e, end_epoch=end_e)
            else:
                df = custom_graph.query_data(conn, table_name, start_e, end_e)

            if (df is None or df.empty) and fallback_to_closest_window:
                closest_start, closest_end = _closest_window_epochs(conn, table_name, col, loc, end_e)
                if closest_start is not None and closest_end is not None:
                    if table_name in TABLE_SCHEMA:
                        df = _load_direct_series(conn, table_name, col, loc,
                                                 start_epoch=closest_start, end_epoch=closest_end)
                    else:
                        df = custom_graph.query_data(conn, table_name, closest_start, closest_end)
            if df is None or df.empty:
                series_list.append(([], []))
                continue

            if 'location' in df.columns:
                loc_series = df['location'].astype(str)
                exact = df[loc_series == loc]
                if not exact.empty:
                    df = exact
                else:
                    loc_canon = _canonical_location_name(loc)
                    mask = loc_series.map(_canonical_location_name) == loc_canon
                    df = df[mask]
            if col not in df.columns:
                series_list.append(([], []))
                continue

            clean = custom_graph._prepare_df_for_plot(df, 'datetime', col)
            if clean.empty:
                direct_df = _load_direct_series(conn, table_name, col, loc, start_epoch=start_e, end_epoch=end_e)
                if (direct_df is None or direct_df.empty) and fallback_to_closest_window:
                    closest_start, closest_end = _closest_window_epochs(conn, table_name, col, loc, end_e)
                    if closest_start is not None and closest_end is not None:
                        direct_df = _load_direct_series(
                            conn,
                            table_name,
                            col,
                            loc,
                            start_epoch=closest_start,
                            end_epoch=closest_end,
                        )
                if direct_df is not None and not direct_df.empty:
                    clean = custom_graph._prepare_df_for_plot(direct_df, 'datetime', col)
            if clean.empty:
                series_list.append(([], []))
            else:
                series_list.append((clean['datetime'].tolist(), clean[col].tolist()))

        traces = []
        for idx, (times, values) in enumerate(series_list):
            if times:
                trace_name = f"{sites[idx]} ({source_tables[idx]})"
                traces.append(go.Scatter(x=times, y=values, mode='lines', name=trace_name))

        if traces:
            unique_sources = sorted(set(source_tables))
            layout = {
                'title': f"{metric_name} - {', '.join(sites)} | Source: {', '.join(unique_sources)}",
                'xaxis': {'title': 'Time'},
                'yaxis': {'title': metric_name},
            }
            plot_div = plot({'data': traces, 'layout': layout}, output_type='div')
        elif include_diagnostics:
            plot_div = _build_no_data_diagnostics(conn, sites, fallback_table, location_table_map)
        else:
            plot_div = '<p>No data available for selected stations/date range.</p>'

        labeled_sites = [f"{sites[i]} ({source_tables[i]})" for i in range(len(sites))]
        table_html = _build_stats_table_html(labeled_sites, series_list)
        return render(request, 'HTML/graphdisplay.html', context={'plot': plot_div, 'table': table_html})
    finally:
        conn.close()

def get_latest_date(request):
    """API endpoint to get the latest available date for a location/metric"""
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'POST required'}, status=400)
        
        location = request.POST.get('location', '').strip()
        metric = request.POST.get('metric', '').strip()
        
        if not location or not metric:
            return JsonResponse({'error': 'location and metric required'}, status=400)
        
        location = _normalize_posted_location(location)
        col = _display_metric_to_sql_column(metric)

        with sqlite3.connect(DB_PATH) as conn:
            location_table_map, _ = _scan_location_table_map(conn)
            location = _resolve_location_name(location, location_table_map)
            table_name = location_table_map.get(location, LOCATION_TO_TABLE.get(location, 'gauge'))
            cursor = conn.cursor()

            table_cols = _table_columns(conn, table_name)
            loc_col = _get_location_col(table_name)
            dt_col = _get_datetime_col(table_name)
            has_location_col = loc_col in table_cols
            has_metric_col = col in table_cols

            if not has_metric_col:
                return JsonResponse(
                    {'latest_date': None, 'message': f'Metric column not found: {col}'},
                    status=404,
                )

            if has_location_col:
                query = (
                    f"SELECT MAX({_quote_ident(dt_col)}) FROM {_quote_ident(table_name)} "
                    f"WHERE {_quote_ident(loc_col)} = ? AND {_quote_ident(col)} IS NOT NULL"
                )
                cursor.execute(query, (location,))
            else:
                query = (
                    f"SELECT MAX({_quote_ident(dt_col)}) FROM {_quote_ident(table_name)} "
                    f"WHERE {_quote_ident(col)} IS NOT NULL"
                )
                cursor.execute(query)
            result = cursor.fetchone()
        
        if result and result[0] is not None:
            dt = _parse_db_datetime(result[0])

            if dt is None:
                return JsonResponse({'latest_date': None, 'message': 'Could not parse latest datetime'}, status=404)

            end_date = dt.date()
            start_date = end_date - timedelta(days=30)
            return JsonResponse({
                'latest_date': end_date.isoformat(),
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
            })
        
        return JsonResponse({'latest_date': None, 'message': 'No data found'}, status=404)
        
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'trace': traceback.format_exc()}, status=500)

def maptabs(request):
    try:
        conn = sqlite3.connect(DB_PATH)
        curr = conn.cursor()
    except Exception:
        conn = None
        curr = None

    locations = []
    location_table_map = {}
    try:
        if curr:
            location_table_map, _ = _scan_location_table_map(conn)
            locations = list(location_table_map.keys())
        locations = sorted(set(locations))
    except Exception:
        locations = []

    rev = {v: k for k, v in SQL_CONVERSION.items()}

    default_options = {
        'gauge': ['Gauge Height', 'Elevation', 'Discharge', 'Water Temperature'],
        'dam': ['Elevation', 'Flow Spill', 'Flow Powerhouse', 'Flow Out', 'Tailwater Elevation'],
        'mesonet': ['Average Air Temperature', 'Average Relative Humidity', 'Total Rainfall'],
    }

    location_options = {}
    location_availability = {}
    # For TABLE_SCHEMA tables, use the pre-defined data_cols as the display options.
    schema_display_cols = {
        tbl: {v: k for k, v in schema['data_cols'].items()}
        for tbl, schema in TABLE_SCHEMA.items()
        if 'data_cols' in schema
    }

    ignored_metric_columns = {'datetime', 'location', 'unique_id', 'id', 'date',
                               'sampleDate', 'DateTime', 'meta.uid', 'meta.state',
                               'meta.elev', 'meta.name', 'meta.name', 'latitude',
                               'longitude', 'sid1', 'sid2', 'station_ID', 'aU_ID',
                               'sampleDepth', 'station.objectID', 'station.stationId',
                               'station.latitude', 'station.longitude', 'station.auId',
                               'station.waterbodyName', 'station.primaryType', 'station.type',
                               'Station', 'id', 'station_ID'}
    for loc in locations:
        base = loc
        table_name = location_table_map.get(base, LOCATION_TO_TABLE.get(base, 'gauge'))
        loc_col = _get_location_col(table_name)
        dt_col = _get_datetime_col(table_name)

        # For tables with known schema, use pre-defined data_cols mapping.
        if table_name in TABLE_SCHEMA and 'data_cols' in TABLE_SCHEMA[table_name]:
            data_cols = TABLE_SCHEMA[table_name]['data_cols']
            opts = list(data_cols.keys())
            availability_for_loc = {}
            for display_name, sql_col in data_cols.items():
                earliest = None
                latest = None
                if curr:
                    try:
                        curr.execute(
                            f"SELECT MIN({_quote_ident(dt_col)}), MAX({_quote_ident(dt_col)}) "
                            f"FROM {_quote_ident(table_name)} "
                            f"WHERE {_quote_ident(loc_col)} = ? AND {_quote_ident(sql_col)} IS NOT NULL",
                            (loc,),
                        )
                        min_max = curr.fetchone() or (None, None)
                        earliest_dt = _parse_db_datetime(min_max[0])
                        latest_dt = _parse_db_datetime(min_max[1])
                        if earliest_dt:
                            earliest = earliest_dt.date().isoformat()
                        if latest_dt:
                            latest = latest_dt.date().isoformat()
                    except Exception:
                        pass
                availability_for_loc[display_name] = {'start': earliest, 'end': latest}
        else:
            cols = []
            if curr:
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
                earliest = None
                latest = None
                if curr:
                    try:
                        curr.execute(
                            f"SELECT MIN({_quote_ident(dt_col)}), MAX({_quote_ident(dt_col)}) "
                            f"FROM {_quote_ident(table_name)} "
                            f"WHERE {_quote_ident(loc_col)} = ? AND {_quote_ident(c)} IS NOT NULL",
                            (loc,),
                        )
                        min_max = curr.fetchone() or (None, None)
                        earliest_dt = _parse_db_datetime(min_max[0])
                        latest_dt = _parse_db_datetime(min_max[1])
                        if earliest_dt:
                            earliest = earliest_dt.date().isoformat()
                        if latest_dt:
                            latest = latest_dt.date().isoformat()
                    except Exception:
                        earliest = None
                        latest = None
                if c in rev:
                    display_name = rev[c]
                else:
                    display_name = c.replace('_', ' ').title()
                opts.append(display_name)
                availability_for_loc[display_name] = {'start': earliest, 'end': latest}

            if not opts:
                opts = default_options.get(table_name, ['Value'])

        location_options[loc] = opts
        location_availability[loc] = availability_for_loc

    if conn:
        conn.close()

    table_to_endpoint = {
        'gauge': ('/customgaugegraph/', 'location'),
        'dam': ('/customdamgraph/', 'dam'),
        'mesonet': ('/custommesonetgraph/', 'mesonet'),
        'cocorahs': ('/customcocograph/', 'cocorahs'),
        'COCORAHS': ('/generate_maptab_graph/', 'location'),
        'DANR': ('/generate_maptab_graph/', 'location'),
        'USACE': ('/generate_maptab_graph/', 'location'),
        'shadehill': ('/customshadehillgraph/', None),
        'noaa_weather': ('/customnoaagraph/', 'noaa')
    }

    display_location_options = {}
    display_location_table_map = {}
    location_entries = []
    for loc, opts in location_options.items():
        # Skip purely numeric locations (USGS station codes, etc.)
        if loc and loc.isdigit():
            continue
        table = location_table_map.get(loc, LOCATION_TO_TABLE.get(loc, 'gauge'))
        endpoint, input_name = table_to_endpoint.get(table, ('/customgaugegraph/', 'location'))
        display_location_options[loc] = opts
        display_location_table_map[loc] = table
        location_entries.append({'location': loc, 'metrics': opts, 'endpoint': endpoint, 'input_name': input_name})

    today = datetime.utcnow().date()
    default_end = today.isoformat()
    default_start = (today - timedelta(days=30)).isoformat()

    return render(request, 'HTML/maptabs.html', {
        'location_entries': location_entries,
        'location_options_json': json.dumps(display_location_options),
        'location_table_map_json': json.dumps(display_location_table_map),
        'location_availability_json': json.dumps(location_availability),
        'graph_index_json': json.dumps({}),
        'default_start': default_start,
        'default_end': default_end,
    })


def _normalize_posted_location(loc: str) -> str:
    """Normalize posted location values from forms to match DB 'location' values.
    Examples: 'Hazen ND' -> 'Hazen', 'Little Eagle SD' -> 'Little Eagle'.
    """
    if not loc:
        return loc
    l = loc.strip()
    # remove trailing state abbreviations
    l = re.sub(r"\s+(ND|SD)$", '', l, flags=re.IGNORECASE)
    # special-case where template may post 'Little' alone
    parts = l.split()
    if parts and parts[0].lower() == 'little':
        return 'Little Eagle'
    return l
    
def tabs(request):
    return render(request, 'graphing/tabs.html')

def tabstest(request):
    return render(request, 'graphing/tabstest.html')

def test(request):
    return render(request, 'graphing/test.html')

def customgauge(request):
    return render(request, 'graphing/customgauge.html')

def customdam(request):
    return render(request, 'graphing/customdam.html')

def custommesonet(request):
    return render(request, 'graphing/custommesonet.html')

def interactiveMap(request):
    locations = []
    try:
        with sqlite3.connect(DB_PATH) as conn:
            location_table_map, _ = _scan_location_table_map(conn)
            cur = conn.cursor()
            for loc, table in location_table_map.items():
                schema = TABLE_SCHEMA.get(table, {})
                lat, lon = None, None

                if schema.get('hardcoded_coords') and loc in schema['hardcoded_coords']:
                    lat, lon = schema['hardcoded_coords'][loc]
                elif schema.get('lat_col') and schema.get('lon_col'):
                    lat_col = schema['lat_col']
                    lon_col = schema['lon_col']
                    loc_col = schema['location_col']
                    try:
                        cur.execute(
                            f"SELECT {_quote_ident(lat_col)}, {_quote_ident(lon_col)} "
                            f"FROM {_quote_ident(table)} WHERE {_quote_ident(loc_col)} = ? LIMIT 1",
                            (loc,)
                        )
                        row = cur.fetchone()
                        if row and row[0] is not None and row[1] is not None:
                            if schema.get('lat_lon_swapped'):
                                # Column names are swapped: 'latitude' col = real lon, 'longitude' col = real lat
                                lon, lat = float(row[0]), float(row[1])
                            else:
                                lat, lon = float(row[0]), float(row[1])
                    except Exception:
                        pass

                if lat is None or lon is None:
                    continue

                datasets = list(schema.get('data_cols', {}).keys()) if 'data_cols' in schema else []
                locations.append({
                    'name': loc,
                    'lat': lat,
                    'lon': lon,
                    'table': table,
                    'datasets': datasets,
                })
    except Exception:
        pass

    return render(request, 'HTML/interactiveMap.html', {
        'locations_json': json.dumps(locations),
    })

def customgaugegraph(request):
    return _render_posted_graph(request, fallback_table='gauge', include_diagnostics=True)

def customdamgraph(request):
    return _render_posted_graph(request, location_field='dam', fallback_table='dam')

def custommesonetgraph(request):
    return _render_posted_graph(request, location_field='mesonet', fallback_table='mesonet')

def customcocograph(request):
    return _render_posted_graph(request, location_field='cocorahs', fallback_table='cocorahs')

def customshadehillgraph(request):
    return _render_posted_graph(request, fallback_table='shadehill', fixed_locations=['Shadehill'])

def customnoaagraph(request):
    return _render_posted_graph(request, location_field='noaa', fallback_table='noaa_weather')


def generate_maptab_graph(request):
    """Unified endpoint for maptabs forms: accepts location(s), data2see, start-date, end-date
    and returns the same HTML fragment as other graph endpoints (plot + stats table).
    """
    return _render_posted_graph(request, fallback_table='gauge', fallback_to_recent_window=True)


def api_map_locations(request):
    """Return JSON list of all locations with lat/lon from the database."""
    locations = []
    try:
        with sqlite3.connect(DB_PATH) as conn:
            location_table_map, _ = _scan_location_table_map(conn)
            cur = conn.cursor()
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
                            (loc,)
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
                locations.append({
                    'name': loc,
                    'lat': lat,
                    'lon': lon,
                    'table': table,
                    'datasets': datasets,
                })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'locations': locations})


def api_timeseries(request):
    """Return time-series JSON for a location+dataset.
    Query params: location, dataset
    Response: {times, values, location, dataset}
    """
    location = request.GET.get('location', '').strip()
    dataset = request.GET.get('dataset', '').strip()
    if not location or not dataset:
        return JsonResponse({'error': 'location and dataset required'}, status=400)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            location_table_map, _ = _scan_location_table_map(conn)
            loc = _resolve_location_name(location, location_table_map)
            table = location_table_map.get(loc)
            if not table:
                return JsonResponse({'error': f'Location not found: {location}'}, status=404)

            schema = TABLE_SCHEMA.get(table)
            if not schema:
                return JsonResponse({'error': f'No schema config for table: {table}'}, status=404)

            data_cols = schema.get('data_cols', {})
            sql_col = data_cols.get(dataset)
            if not sql_col:
                sql_col = _display_metric_to_sql_column(dataset)

            loc_col = schema['location_col']
            dt_col = schema['datetime_col']

            cur = conn.cursor()
            cur.execute(
                f"SELECT {_quote_ident(dt_col)}, {_quote_ident(sql_col)} "
                f"FROM {_quote_ident(table)} "
                f"WHERE {_quote_ident(loc_col)} = ? AND {_quote_ident(sql_col)} IS NOT NULL "
                f"ORDER BY {_quote_ident(dt_col)} ASC",
                (loc,)
            )
            rows = cur.fetchall()

        times, values = [], []
        for row in rows:
            raw_val = row[1]
            try:
                val = float(raw_val)
            except (TypeError, ValueError):
                continue
            import math
            if math.isnan(val):
                continue
            dt = _parse_db_datetime(row[0])
            if dt is None:
                continue
            times.append(dt.isoformat())
            values.append(val)

        return JsonResponse({'times': times, 'values': values, 'location': loc, 'dataset': dataset})
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'trace': traceback.format_exc()}, status=500)
