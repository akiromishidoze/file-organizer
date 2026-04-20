#!/usr/bin/env bash
# Launcher: starts the backend (which also serves the built frontend) and opens the browser.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [[ ! -d frontend/dist ]]; then
  echo "frontend not built — running 'npm run build' first..."
  (cd frontend && npm install --silent && npm run build)
fi

python3 backend/server.py &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null || true' EXIT INT TERM

for _ in {1..40}; do
  if curl -fs http://127.0.0.1:5174/api/health >/dev/null 2>&1; then
    break
  fi
  sleep 0.1
done

xdg-open "http://127.0.0.1:5174/" >/dev/null 2>&1 || true

wait $SERVER_PID
