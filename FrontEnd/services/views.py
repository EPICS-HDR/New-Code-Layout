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

from BackEnd import custom_graph
from BackEnd.SourceFiles.config import DB_PATH, LOCATION_TO_TABLE, SQL_CONVERSION


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
    """Discover location->table mapping by scanning all DB tables with a location column."""
    location_table_map = {}
    tables = []
    for table_name in _list_db_tables(conn):
        try:
            cols = _table_columns(conn, table_name)
        except Exception:
            continue
        if 'location' not in cols:
            continue
        tables.append(table_name)
        try:
            curr = conn.cursor()
            curr.execute(
                f"SELECT DISTINCT location FROM {_quote_ident(table_name)} WHERE location IS NOT NULL"
            )
            for r in curr.fetchall():
                if not r:
                    continue
                loc = (r[0] or '').strip()
                if not loc:
                    continue
                # Keep first table encountered for a location to maintain deterministic routing.
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
    col = SQL_CONVERSION.get(metric_name)
    return col or metric_name.replace(' ', '_').lower()


def _normalize_metric_name(metric_name: str) -> str:
    # Some forms still send values like `Flow_Spill`.
    if '_' in metric_name:
        parts = metric_name.split('_')
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"
    return metric_name


def _to_epoch(date_str):
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str)
    except Exception:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp())


def _build_stats_table_html(sites, series_list):
    rows = []
    for idx, (_, values) in enumerate(series_list):
        vals = [
            v for v in values
            if v is not None and not (isinstance(v, float) and math.isnan(v))
        ]
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
            loc = _normalize_posted_location(raw_loc)
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

            df = custom_graph.query_data(conn, table_name, start_e, end_e)
            if df is None or df.empty:
                series_list.append(([], []))
                continue

            if 'location' in df.columns:
                df = df[df['location'] == loc]
            if col not in df.columns:
                series_list.append(([], []))
                continue

            clean = custom_graph._prepare_df_for_plot(df, 'datetime', col)
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
        conn = sqlite3.connect(DB_PATH)
        location_table_map, _ = _scan_location_table_map(conn)
        table_name = location_table_map.get(location, LOCATION_TO_TABLE.get(location, 'gauge'))
        col = _display_metric_to_sql_column(metric)
        cursor = conn.cursor()
        
        # Query for max datetime where this column is not null
        query = f"""
            SELECT MAX(datetime) 
            FROM {_quote_ident(table_name)} 
            WHERE location = ? AND {_quote_ident(col)} IS NOT NULL
        """
        cursor.execute(query, (location,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            max_datetime = result[0]
            
            if isinstance(max_datetime, str):
                latest_date = max_datetime
            else:
                dt = datetime.fromtimestamp(max_datetime)
                latest_date = dt.strftime('%Y-%m-%d')
            
            return JsonResponse({'latest_date': latest_date})
        
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

    location_options = {}
    for loc in locations:
        base = loc
        table_name = location_table_map.get(base, LOCATION_TO_TABLE.get(base, 'gauge'))
        cols = []
        if curr:
            try:
                curr.execute(f"PRAGMA table_info({_quote_ident(table_name)})")
                cols = [r[1] for r in curr.fetchall()]
            except Exception:
                cols = []

        opts = []
        for c in cols:
            if c == 'datetime' or c == 'location':
                continue
            if c in rev:
                opts.append(rev[c])
            else:
                opts.append(c.replace('_', ' ').title())

        if not opts:
            if table_name == 'gauge':
                opts = ['Gauge Height', 'Elevation', 'Discharge', 'Water Temperature']
            elif table_name == 'dam':
                opts = ['Elevation', 'Flow Spill', 'Flow Powerhouse', 'Flow Out', 'Tailwater Elevation']
            elif table_name == 'mesonet':
                opts = ['Average Air Temperature', 'Average Relative Humidity', 'Total Rainfall']
            else:
                opts = ['Value']

        location_options[loc] = opts

    if conn:
        conn.close()

    graphs_dir = os.path.join(settings.BASE_DIR, 'static', 'graphs')
    graph_index = {}
    try:
        files = os.listdir(graphs_dir)
    except Exception:
        files = []

    def norm(s):
        return ''.join((s or '').lower().split())

    for fn in files:
        if not fn.lower().endswith('.html'):
            continue
        stem = fn[:-5]
        if '__' in stem:
            parts = stem.split('__')
            if len(parts) >= 3:
                location = parts[1].replace('_', ' ').strip()
                metric = parts[2].replace('_', ' ').strip()
            else:
                continue
        else:
            atm = re.split(r"\s+at\s+", stem, flags=re.IGNORECASE)
            if len(atm) >= 2:
                location = atm[-1].replace('_', ' ').strip()
                metric = ' at '.join(atm[:-1]).replace('_', ' ').strip()
            else:
                continue

        for loc in location_options.keys():
            if norm(loc) == norm(location) or norm(loc) in norm(location):
                latest = None
                m = re.search(r"(\d{6,8})_(\d{6,8})_interactive", fn)
                if m:
                    end = m.group(2)
                    if len(end) == 8:
                        latest = f"{end[0:4]}-{end[4:6]}-{end[6:8]}"
                else:
                    m2 = re.search(r"(\d{8})_interactive", fn)
                    if m2:
                        d = m2.group(1)
                        latest = f"{d[0:4]}-{d[4:6]}-{d[6:8]}"

                entry = graph_index.setdefault(loc, {})
                metrics = entry.setdefault('metrics', {})
                lst = metrics.setdefault(metric.title(), [])
                lst.append(fn)
                if latest:
                    cur = entry.setdefault('latest', {})
                    prev = cur.get(metric.title())
                    if not prev or latest > prev:
                        cur[metric.title()] = latest
                break

    table_to_endpoint = {
        'gauge': ('/customgaugegraph/', 'location'),
        'dam': ('/customdamgraph/', 'dam'),
        'mesonet': ('/custommesonetgraph/', 'mesonet'),
        'cocorahs': ('/customcocograph/', 'cocorahs'),
        'shadehill': ('/customshadehillgraph/', None),
        'noaa_weather': ('/customnoaagraph/', 'noaa')
    }

    location_entries = []
    for loc, opts in location_options.items():
        table = location_table_map.get(loc, LOCATION_TO_TABLE.get(loc, 'gauge'))
        endpoint, input_name = table_to_endpoint.get(table, ('/customgaugegraph/', 'location'))
        location_entries.append({'location': loc, 'metrics': opts, 'endpoint': endpoint, 'input_name': input_name})

    today = datetime.utcnow().date()
    default_end = today.isoformat()
    default_start = (today - timedelta(days=30)).isoformat()

    return render(request, 'HTML/maptabs.html', {
        'location_entries': location_entries,
        'location_options_json': json.dumps(location_options),
        'location_table_map_json': json.dumps(location_table_map),
        'graph_index_json': json.dumps(graph_index),
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
    from django.templatetags.static import static

    graphs_dir = os.path.join(settings.BASE_DIR, 'static', 'graphs')
    places = ['Hazen', 'Stanton', 'Washburn', 'Price', 'Mandan', 'Bismarck', 'Judson',
              'Breien', 'Cash', 'Wakpala', 'Whitehorse', 'Schmidt', 'Little Eagle',
              'Oahe', 'Big Bend', 'Fort Randall', 'Gavins Point', 'Garrison', 'Fort Peck',
              'Fort Yates', 'Mott', 'Carson', 'Linton', 'Lemmon', 'McIntosh', 'Mclaughlin',
              'Mound City', 'Timber Lake']

    graph_map = {}
    try:
        files = os.listdir(graphs_dir)
    except Exception:
        files = []

    def norm(s):
        return ''.join((s or '').lower().split())

    for fn in files:
        if not fn.lower().endswith('.html'):
            continue
        fn_norm = norm(fn)
        for place in places:
            if norm(place) in fn_norm:
                graph_map.setdefault(place, []).append(static(f'graphs/{fn}'))

    for k in graph_map:
        graph_map[k] = sorted(graph_map[k])

    return render(request, 'HTML/interactiveMap.html', {'graph_map_json': json.dumps(graph_map)})

def customgaugegraph(request):
    return _render_graph_response(
        request,
        request.POST.getlist('location'),
        _normalize_metric_name(request.POST['data2see']),
        'gauge',
        start_epoch=_to_epoch(request.POST['start-date']),
        end_epoch=_to_epoch(request.POST['end-date']),
        include_diagnostics=True,
    )

def customdamgraph(request):
    return _render_graph_response(
        request,
        request.POST.getlist('dam'),
        _normalize_metric_name(request.POST['data2see']),
        'dam',
        start_epoch=_to_epoch(request.POST['start-date']),
        end_epoch=_to_epoch(request.POST['end-date']),
    )

def custommesonetgraph(request):
    return _render_graph_response(
        request,
        request.POST.getlist('mesonet'),
        _normalize_metric_name(request.POST['data2see']),
        'mesonet',
        start_epoch=_to_epoch(request.POST['start-date']),
        end_epoch=_to_epoch(request.POST['end-date']),
    )

def customcocograph(request):
    return _render_graph_response(
        request,
        request.POST.getlist('cocorahs'),
        _normalize_metric_name(request.POST['data2see']),
        'cocorahs',
        start_epoch=_to_epoch(request.POST['start-date']),
        end_epoch=_to_epoch(request.POST['end-date']),
    )

def customshadehillgraph(request):
    return _render_graph_response(
        request,
        ['Shadehill'],
        _normalize_metric_name(request.POST['data2see']),
        'shadehill',
        start_epoch=_to_epoch(request.POST['start-date']),
        end_epoch=_to_epoch(request.POST['end-date']),
    )

def customnoaagraph(request):
    return _render_graph_response(
        request,
        request.POST.getlist('noaa'),
        _normalize_metric_name(request.POST['data2see']),
        'noaa_weather',
        start_epoch=_to_epoch(request.POST['start-date']),
        end_epoch=_to_epoch(request.POST['end-date']),
    )


def generate_maptab_graph(request):
    """Unified endpoint for maptabs forms: accepts location(s), data2see, start-date, end-date
    and returns the same HTML fragment as other graph endpoints (plot + stats table).
    """
    locationlist = request.POST.getlist('location')
    data2see = request.POST.get('data2see', '')
    return _render_graph_response(
        request,
        locationlist,
        _normalize_metric_name(data2see),
        'gauge',
        start_epoch=_to_epoch(request.POST.get('start-date', '')),
        end_epoch=_to_epoch(request.POST.get('end-date', '')),
        fallback_to_recent_window=True,
    )
