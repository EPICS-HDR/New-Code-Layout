'''
Author: Kartik Jariam
Date: 3/05/2026
Purpose: This is the backend's API. Any and all commands accessible to front end and the user will be available here.
'''
from pathlib import Path
import os
import sys

BACKEND_DIR = Path(__file__).resolve().parent
SOURCE_FILES_DIR = BACKEND_DIR / 'SourceFiles'


def get_command_catalog():
    """Return metadata for all available backend commands."""
    return [
        {
            'id': 'listAllSources',
            'label': 'List All Sources',
            'description': 'List all source files in the BackEnd/SourceFiles folder.',
        },
        {
            'id': 'listStations',
            'label': 'List Stations',
            'description': 'List all stations for each configured source.',
        },
    ]


def listAllSources():
    """List all source files (files starting with _) in BackEnd/SourceFiles."""
    sources = []
    for file in SOURCE_FILES_DIR.glob('_*.py'):
        sources.append(file.stem)  # e.g. '_COCORAHS'
    print('Available sources:', sources)
    return sources


def listStations():
    """List all stations for each configured source."""
    sys.path.insert(0, str(SOURCE_FILES_DIR))
    try:
        from config import COCORAHSConfig, DANRConfig, USACEConfig
        stations = {
            'COCORAHS': list(COCORAHSConfig['stationList'].keys()),
            'DANR': DANRConfig['stationList'],
            'USACE': USACEConfig['stationList'],
        }
        for source, station_list in stations.items():
            print(f'{source}: {station_list}')
        return stations
    finally:
        sys.path.pop(0)


if __name__ == "__main__":
    listAllSources()
