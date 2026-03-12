#!/usr/bin/env python3
'''Daily datasource update script. Run this to update all datasources in Measurements.db'''
import sys
import os
import importlib

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

sources = [
    ("DANR", "BackEnd.SourceFiles._DANR"),
    ("NDGIS", "BackEnd.SourceFiles._NDGIS"),
    ("USACE", "BackEnd.SourceFiles._USACE"),
]

def main():
    print(f"Starting datasource updates at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    for name, module_path in sources:
        try:
            print(f"\nUpdating {name}...", end=" ", flush=True)
            module = importlib.import_module(module_path)
            if hasattr(module, 'update'):
                module.update()
            else:
                raise AttributeError(f"{module_path} has no update()")
            print("✓")
        except Exception as e:
            print(f"✗ Error: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print(f"Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    main()
