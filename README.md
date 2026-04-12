# Standing Rock Water Data Dashboard

A web dashboard for the Standing Rock Sioux Tribe displaying environmental and water quality data from monitoring stations across North and South Dakota.

**Live site:** https://standingrock-dashboard.web.app

## Architecture

The site is deployed as **static files on Firebase Hosting** — no server required.

```
FrontEnd/               ← Firebase serves this directory
  index.html            ← Homepage
  about.html            ← About page
  map.html              ← Interactive Mapbox map
  maptabs.html          ← Custom graph dashboard (client-side Plotly.js)
  contactus.html        ← Contact form
  navbar.html           ← Shared navigation bar
  static/
    css/                ← Stylesheets
    js/                 ← JavaScript (map, modals, admin)
    images/             ← Static images
    graphs/             ← Pre-generated interactive Plotly HTML graphs
    data/               ← JSON data files (exported from Measurements.db)
      manifest.json     ← Location/metric metadata
      usgs__Hazen.json  ← Per-location time series data
      ...

BackEnd/                ← Data ingestion pipeline (runs offline)
  SourceFiles/
    config.py           ← Master config: stations, URLs, field mappings
    _COCORAHS.py        ← CoCoRaHS precipitation data
    _DANR.py            ← SD Dept of Agriculture & Natural Resources
    _USACE.py           ← US Army Corps of Engineers dam data
  commands.py           ← Backend command catalog
  custom_graph.py       ← Graph generation engine

Measurements.db         ← SQLite database (primary data store)
export_static_data.py   ← Exports DB → JSON for the static frontend
refresh_and_deploy.sh   ← One-command data refresh + deploy
```

## Data Sources

| Source | Table | What it measures |
|--------|-------|-----------------|
| USGS | `usgs` | Gauge height, elevation, discharge, water temp |
| ND Mesonet | `mesonet` | Air temp, humidity, soil temp, wind, rainfall, pressure |
| CoCoRaHS | `cocorahs` | Precipitation, snowfall, snow depth |
| Shadehill Dam | `shadehill` | Reservoir storage, elevation, inflow, discharge |
| NOAA | `noaa_weather` | Precipitation, avg/max/min temperature |
| DANR | `DANR` | Water chemistry (pH, dissolved oxygen, etc.) |
| Water Quality | `water_quality` | Phosphorus, nitrogen, e.coli, ammonia |

## How to Update Data and Redeploy

### Quick way (one command)

```bash
./refresh_and_deploy.sh
```

### Manual steps

```bash
# 1. Pull latest data from APIs into Measurements.db
cd BackEnd/SourceFiles
python3 _COCORAHS.py
python3 _DANR.py
python3 _USACE.py

# 2. Regenerate interactive graph HTML files
cd ../..
python3 -m BackEnd.custom_graph

# 3. Re-export JSON data for the static frontend
python3 export_static_data.py

# 4. Deploy to Firebase
firebase deploy --only hosting
```

### Prerequisites

```bash
pip install -r requirements.txt
npm install -g firebase-tools
firebase login    # use standingrock.hdr@gmail.com
```

## How to Run Locally

### Static site (like Firebase)
```bash
cd FrontEnd
python3 -m http.server 9000
# Open http://127.0.0.1:9000
```

### Django dev server (full backend)
```bash
pip install -r requirements.txt
python3 manage.py runserver
# Open http://127.0.0.1:8000
```

## How to Add a New Data Source

1. Create `BackEnd/SourceFiles/_NEWSOURCE.py` following the pull/process/push pattern of existing scripts
2. Add the station config to `BackEnd/SourceFiles/config.py`
3. Add any new metric display names to `LOCATION_TO_TABLE` and `SQL_CONVERSION` in config.py
4. Add the same display names to `DISPLAY_NAMES` in `export_static_data.py`
5. Run the ingestion script, then `python3 export_static_data.py`, then deploy

## Team

Built by **EPICS HDR (Harnessing the Data Revolution)** at Purdue University.

- Project partner: Standing Rock Sioux Tribe
- Contact: Epics-hdr@ecn.purdue.edu
