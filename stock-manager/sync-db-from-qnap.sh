#!/usr/bin/env bash
# Copy live SQLite DB from QNAP FilamentsManagement to local backend/data.
set -euo pipefail
QNAP_HOST="${QNAP_HOST:-192.168.10.11}"
QNAP_USER="${QNAP_USER:-admin}"
REMOTE="/share/Container/FilmentsManagement/backend/data/filaments.db"
LOCAL_DIR="$(cd "$(dirname "$0")/backend/data" && pwd)"
LOCAL="$LOCAL_DIR/filaments.db"

if [[ -z "${SSHPASS:-}" ]]; then
  echo "Set SSHPASS for admin password, e.g.: export SSHPASS='...'"
  exit 1
fi

mkdir -p "$LOCAL_DIR"
cp -f "$LOCAL" "$LOCAL.bak-$(date +%Y%m%d-%H%M%S)" 2>/dev/null || true

echo "Copying $QNAP_USER@$QNAP_HOST:$REMOTE -> $LOCAL"
sshpass -e scp -o StrictHostKeyChecking=no \
  "${QNAP_USER}@${QNAP_HOST}:${REMOTE}" "$LOCAL"

python3 - <<PY
import sqlite3
c = sqlite3.connect("$LOCAL")
cur = c.cursor()
cur.execute("SELECT COUNT(*) FROM filaments")
f = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM color_stocks")
cs = cur.fetchone()[0]
cur.execute("SELECT SUM(quantity) FROM color_stocks")
q = cur.fetchone()[0]
print(f"OK: {f} filaments, {cs} colors, {q} spools total")
PY
