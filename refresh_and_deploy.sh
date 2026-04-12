#!/usr/bin/env bash
# ============================================================
# refresh_and_deploy.sh
#
# One-command script to refresh data and redeploy the site.
# Run from the repo root:
#   ./refresh_and_deploy.sh
#
# What it does:
#   1. Runs data ingestion scripts (pulls latest from APIs)
#   2. Regenerates interactive graph HTML files
#   3. Re-exports JSON data for the static frontend
#   4. Deploys to Firebase Hosting
#
# Prerequisites:
#   - Python 3 with dependencies: pip install -r requirements.txt
#   - Firebase CLI: npm install -g firebase-tools
#   - Firebase login: firebase login
# ============================================================

set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

echo "========================================"
echo "  Standing Rock Dashboard — Refresh"
echo "========================================"
echo ""

# Step 1: Run ingestion scripts
echo "[1/4] Pulling latest data from sources..."
echo "  → CoCoRaHS..."
python3 -c "
import sys; sys.path.insert(0, 'BackEnd/SourceFiles')
try:
    from _COCORAHS import update; update()
    print('    CoCoRaHS: OK')
except Exception as e:
    print(f'    CoCoRaHS: SKIPPED ({e})')
"

echo "  → DANR..."
python3 -c "
import sys; sys.path.insert(0, 'BackEnd/SourceFiles')
try:
    from _DANR import update; update()
    print('    DANR: OK')
except Exception as e:
    print(f'    DANR: SKIPPED ({e})')
"

echo "  → USACE..."
python3 -c "
import sys; sys.path.insert(0, 'BackEnd/SourceFiles')
try:
    from _USACE import update; update()
    print('    USACE: OK')
except Exception as e:
    print(f'    USACE: SKIPPED ({e})')
"
echo ""

# Step 2: Regenerate graph HTMLs
echo "[2/4] Regenerating interactive graph files..."
python3 -m BackEnd.custom_graph 2>&1 | tail -3
echo ""

# Step 3: Re-export JSON data
echo "[3/4] Exporting JSON data for static frontend..."
python3 export_static_data.py 2>&1 | tail -3
echo ""

# Step 4: Deploy
echo "[4/4] Deploying to Firebase..."
firebase deploy --only hosting 2>&1 | tail -5
echo ""

echo "========================================"
echo "  Done! Site updated at:"
echo "  https://standingrock-dashboard.web.app"
echo "========================================"
