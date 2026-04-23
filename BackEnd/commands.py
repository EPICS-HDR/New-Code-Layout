'''
Author: Kartik Jariam
Date: 3/05/2026
Purpose: This is the backend's API. Any and all commands accessable to front end and the user will be available here.
'''
from pathlib import Path
import os
import sys

def listAllSources():
    os.chdir('./BackEnd/SourceFiles')
    sources = []
    for file in Path('./').glob('_*.py'):
        sources += file.name.replace('.py','')
        #bro syntax error smh source += file
    return sources

def listStations(source):
    pass

def updateAll():
    pass


def refreshMapCache():
    """Rebuild the JSON cache used by the Map and Custom Graph (maptabs) pages."""
    from BackEnd.cache_builder import refresh_map_cache
    summary = refresh_map_cache(built_by='admin')
    print(summary)
    return summary


def _run_source_update(module_name: str) -> str:
    """Import a source file in BackEnd/SourceFiles/ and call its update()."""
    import importlib
    import time

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_dir = os.path.join(repo_root, 'BackEnd', 'SourceFiles')
    if source_dir not in sys.path:
        sys.path.insert(0, source_dir)

    old_cwd = os.getcwd()
    os.chdir(repo_root)  # so sqlite3.connect('database.db') hits the real db
    try:
        print(f'--- updating {module_name} ---')
        t0 = time.time()
        mod = importlib.import_module(module_name)
        importlib.reload(mod)
        mod.update()
        elapsed = time.time() - t0
        msg = f'{module_name} update finished in {elapsed:.1f}s'
        print(msg)
        return msg
    finally:
        os.chdir(old_cwd)


def updateUSACE():
    return _run_source_update('_USACE')


def updateDANR():
    return _run_source_update('_DANR')


def updateCOCORAHS():
    return _run_source_update('_COCORAHS')


def updateAllSources():
    """Run every source update in sequence, then rebuild the map cache."""
    results = []
    for mod_name in ('_USACE', '_DANR', '_COCORAHS'):
        try:
            results.append(_run_source_update(mod_name))
        except Exception as exc:
            results.append(f'{mod_name} FAILED: {exc}')
            print(f'[ERROR] {mod_name} failed: {exc}')
    try:
        refreshMapCache()
    except Exception as exc:
        results.append(f'refreshMapCache FAILED: {exc}')
        print(f'[ERROR] refreshMapCache failed: {exc}')
    return '\n'.join(results)


def get_command_catalog():
    """Commands exposed in the admin-dashboard 'Run Updates' dropdown."""
    return [
        {
            'id': 'refreshMapCache',
            'label': 'Refresh Map Cache',
            'description': 'Rebuild the server-side cache used by the Map and Custom Graph pages.',
        },
        {
            'id': 'updateAllSources',
            'label': 'Update All Sources',
            'description': 'Pull + push every source (USACE, DANR, COCORAHS) and rebuild the map cache.',
        },
        {
            'id': 'updateUSACE',
            'label': 'Update USACE',
            'description': 'Pull latest reservoir data from USACE and write to database.db.',
        },
        {
            'id': 'updateDANR',
            'label': 'Update DANR',
            'description': 'Pull latest water-quality data from DANR and write to database.db.',
        },
        {
            'id': 'updateCOCORAHS',
            'label': 'Update COCORAHS',
            'description': 'Pull latest weather observations from COCORAHS and write to database.db.',
        },
        {
            'id': 'listAllSources',
            'label': 'List All Sources',
            'description': 'List all source files in the BackEnd/SourceFiles folder.',
        },
    ]


if (__name__ == "__main__"):
    listAllSources()
