from __future__ import annotations

import pandas as pd


def query_data(conn, table_name, start_epoch=None, end_epoch=None):
    query = f'SELECT * FROM "{table_name}"'
    params = []
    where = []

    if start_epoch is not None:
        where.append('datetime >= ?')
        params.append(start_epoch)
    if end_epoch is not None:
        where.append('datetime <= ?')
        params.append(end_epoch)

    if where:
        query += ' WHERE ' + ' AND '.join(where)

    try:
        return pd.read_sql_query(query, conn, params=params)
    except Exception:
        return pd.DataFrame()


def _prepare_df_for_plot(df, datetime_col, value_col):
    if df is None or df.empty:
        return pd.DataFrame(columns=[datetime_col, value_col])

    out = df.copy()
    out = out[[c for c in [datetime_col, value_col] if c in out.columns]]
    if datetime_col not in out.columns or value_col not in out.columns:
        return pd.DataFrame(columns=[datetime_col, value_col])

    out[value_col] = pd.to_numeric(out[value_col], errors='coerce')
    out = out.dropna(subset=[value_col])

    dt_from_epoch = pd.to_datetime(out[datetime_col], unit='s', errors='coerce')
    dt_from_string = pd.to_datetime(out[datetime_col], errors='coerce')
    out[datetime_col] = dt_from_epoch.fillna(dt_from_string)

    out = out.dropna(subset=[datetime_col]).sort_values(datetime_col)
    return out


def get_latest_datetime(conn, table_name, value_col):
    try:
        cur = conn.cursor()
        cur.execute(
            f'SELECT MAX(datetime) FROM "{table_name}" WHERE "{value_col}" IS NOT NULL'
        )
        row = cur.fetchone()
        if not row or row[0] is None:
            return None

        raw_value = row[0]
        parsed = pd.to_datetime(raw_value, unit='s', errors='coerce')
        if pd.isna(parsed):
            parsed = pd.to_datetime(raw_value, errors='coerce')
        if pd.isna(parsed):
            return None
        return parsed.to_pydatetime()
    except Exception:
        return None
