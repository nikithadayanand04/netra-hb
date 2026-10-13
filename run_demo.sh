#!/usr/bin/env bash
# Start the Netra-Hb lab demo: offline, opens the browser on Home.
# Usage: ./run_demo.sh            (port 8501)
#        PORT=8600 ./run_demo.sh
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -f .venv/bin/activate ]]; then
  echo "No .venv found. Set it up first:" >&2
  echo "  python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi
# shellcheck disable=SC1091
source .venv/bin/activate

missing=0
for site in eye palm nail; do
  [[ -f "outputs/models/screen_${site}.joblib" ]] || missing=1
done
if [[ $missing -eq 1 ]]; then
  echo "Screen models missing: building them (needs data/ and the earlier pipeline outputs, ~4 min) ..."
  python -m scripts.build_screen_models
fi

PORT="${PORT:-8501}"
echo "Netra-Hb demo on http://localhost:${PORT}  (Ctrl+C to stop)"
exec streamlit run app/Home.py --server.port "$PORT" --server.headless false --browser.serverAddress localhost
