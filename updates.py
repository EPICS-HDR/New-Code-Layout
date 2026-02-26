#!/usr/bin/env python3
'''Daily datasource update script. Run this to update all datasources in Measurements.db'''
import sys
import os

# Must run from project root for imports to work
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.environ['PYTHONPATH'] = project_root

from datetime import datetime

# Set NOAA token if available
if 'NOAA_TOKEN' not in os.environ:
    os.environ['NOAA_TOKEN'] = 'WkaDdDnFDuEUpiUEFiNMFcLcNKVsQgtp'

print(f"Starting datasource updates at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

sources = [
    ("DANR", "services.backend.datasources.New_DANR"),
    ("CoCoRaHS", "services.backend.datasources.New_Cocorahs"),
    ("Shadehill", "services.backend.datasources.New_Shadehills"),
    ("NDGIS", "services.backend.datasources.New_NDGIS"),
    ("NDMES", "services.backend.datasources.New_NDMES"),
    ("NOAA", "services.backend.datasources.New_NOAA"),
    ("USGS", "services.backend.datasources.New_USGS"),
    ("USACE", "services.backend.datasources.New_USACE"),
]

for name, module_path in sources:
    try:
        print(f"\nUpdating {name}...", end=" ", flush=True)
        module = __import__(module_path, fromlist=['update'])
        module.update()
        print("✓")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}")

print("\n" + "=" * 60)
print(f"Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
