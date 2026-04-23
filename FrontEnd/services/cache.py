"""Reader for the server-side map/maptabs cache produced by BackEnd/cache_builder.py.

Returns None on miss so callers can fall back to a live DB scan.
"""
from __future__ import annotations

import json
import os
import threading
from typing import Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_FILE = os.path.join(REPO_ROOT, 'BackEnd', 'cache', 'map_cache.json')

_mem_lock = threading.Lock()
_mem_mtime: float | None = None
_mem_payload: dict | None = None


def read_cache() -> Optional[dict]:
    """Return parsed cache dict, or None if missing/malformed. Memoized on file mtime."""
    global _mem_mtime, _mem_payload
    try:
        mtime = os.path.getmtime(CACHE_FILE)
    except OSError:
        return None

    with _mem_lock:
        if _mem_payload is not None and _mem_mtime == mtime:
            return _mem_payload

    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    except Exception:
        return None

    with _mem_lock:
        _mem_mtime = mtime
        _mem_payload = payload
    return payload


def get_map_locations() -> Optional[list]:
    payload = read_cache()
    if not payload:
        return None
    return payload.get('map_locations')


def get_maptabs_payload() -> Optional[dict]:
    payload = read_cache()
    if not payload:
        return None
    return payload.get('maptabs')


def get_location_table_map() -> Optional[dict]:
    payload = read_cache()
    if not payload:
        return None
    return payload.get('location_table_map')
