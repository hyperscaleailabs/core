#!/usr/bin/env bash
# Import the checked-in Superset dashboard bundles into a running Superset.
#
# Why this exists: the dashboards used to be built by hand in the Superset UI, on a pod
# whose metadata database is ephemeral. That made the analytics evidence unreproducible -
# a restart erased it, and a fresh clone could never recreate it. The bundles under
# dashboards/superset/ are now the source of truth and this script is how they land.
#
# Usage (from prod/):
#   bash deploy/scripts/import-superset-dashboards.sh [--url URL] [--bundle DIR]
#
# With no --url it port-forwards the in-cluster Superset service.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

CTX="${CTX:-k3d-agentsim}"
NS_DATA="${NS_DATA:-data}"
PORT="${PORT:-18088}"
URL=""
BUNDLE_DIR="$ROOT/dashboards/superset"
SUPERSET_USER="${SUPERSET_USER:-admin}"
SUPERSET_PASSWORD="${SUPERSET_PASSWORD:-admin}"
# The bundle masks the database password on export; supply the target's on import.
CH_PASSWORD="${CH_PASSWORD:-asc}"

while [ $# -gt 0 ]; do
  case "$1" in
    --url) URL="$2"; shift 2 ;;
    --bundle) BUNDLE_DIR="$2"; shift 2 ;;
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

PF=""
cleanup() { [ -n "$PF" ] && kill "$PF" 2>/dev/null || true; }
trap cleanup EXIT

if [ -z "$URL" ]; then
  kubectl --context "$CTX" -n "$NS_DATA" port-forward svc/superset "$PORT:8088" >/dev/null 2>&1 &
  PF=$!
  URL="http://127.0.0.1:$PORT"
  for _ in $(seq 1 30); do
    curl -sf -m 3 "$URL/health" >/dev/null 2>&1 && break
    sleep 2
  done
fi

echo ">> Superset at $URL"

TOKEN="$(curl -s -m 20 -X POST "$URL/api/v1/security/login" -H 'Content-Type: application/json' \
  -d "{\"username\":\"$SUPERSET_USER\",\"password\":\"$SUPERSET_PASSWORD\",\"provider\":\"db\",\"refresh\":true}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('access_token',''))")"
[ -n "$TOKEN" ] || { echo "login failed" >&2; exit 1; }

COOKIE_JAR="$(mktemp)"
CSRF="$(curl -s -m 20 -c "$COOKIE_JAR" -H "Authorization: Bearer $TOKEN" "$URL/api/v1/security/csrf_token/" \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('result',''))")"

status=0
for dir in "$BUNDLE_DIR"/*/; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"
  # The importer takes a zip whose top-level directory carries the bundle.
  work="$(mktemp -d)"
  cp -R "$dir" "$work/$name"
  # Restore the masked database password for the target environment.
  find "$work/$name/databases" -name '*.yaml' -exec \
    sed -i.bak "s|:XXXXXXXXXX@|:${CH_PASSWORD}@|g" {} \; 2>/dev/null || true
  find "$work/$name" -name '*.bak' -delete
  zip_path="$work/$name.zip"
  (cd "$work" && zip -qr "$zip_path" "$name")

  passwords="{\"$name/databases/ClickHouse.yaml\": \"$CH_PASSWORD\"}"
  echo ">> importing $name"
  resp="$(curl -s -m 120 -b "$COOKIE_JAR" \
    -H "Authorization: Bearer $TOKEN" -H "X-CSRFToken: $CSRF" -H "Referer: $URL/" \
    -F "formData=@$zip_path;type=application/zip" \
    -F "passwords=$passwords" \
    -F "overwrite=true" \
    "$URL/api/v1/dashboard/import/")"
  if printf '%s' "$resp" | grep -q '"message": *"OK"'; then
    echo "   ok"
  else
    echo "   FAILED: $(printf '%s' "$resp" | head -c 400)"
    status=1
  fi
  rm -rf "$work"
done

# Superset's dashboard importer does not carry `query_context` onto the chart record, so a
# chart imported this way renders in the UI but is not queryable through /api/v1/chart/<id>/data.
# That gap is what made the analytics hop unverifiable from CI; reconcile it explicitly.
for chart_yaml in "$BUNDLE_DIR"/*/charts/*.yaml; do
  [ -f "$chart_yaml" ] || continue
  CHART_YAML="$chart_yaml" URL="$URL" TOKEN="$TOKEN" CSRF="$CSRF" COOKIE_JAR="$COOKIE_JAR" \
  python3 - <<'PY' || status=1
import json, os, re, subprocess, sys

path = os.environ["CHART_YAML"]
text = open(path).read()
m = re.search(r"^query_context: '(.*?)'\n(?=\w|$)", text, re.M | re.S)
if not m:
    sys.exit(0)  # no query context declared; nothing to reconcile
qc = m.group(1).replace("''", "'")
try:
    json.loads(qc)
except json.JSONDecodeError as exc:
    print(f"   invalid query_context in {os.path.basename(path)}: {exc}", file=sys.stderr)
    sys.exit(1)

name = re.search(r"^slice_name: (.*)$", text, re.M).group(1).strip()
url, token, csrf, jar = (os.environ[k] for k in ("URL", "TOKEN", "CSRF", "COOKIE_JAR"))
auth = ["-H", f"Authorization: Bearer {token}"]


def curl(*args):
    return subprocess.run(["curl", "-s", "-m", "30", *args], capture_output=True, text=True).stdout


listing = curl(*auth, f"{url}/api/v1/chart/?q=(page_size:100)")
try:
    charts = json.loads(listing)["result"]
except (KeyError, json.JSONDecodeError):
    print(f"   could not list charts while looking for '{name}'", file=sys.stderr)
    sys.exit(1)
ids = [c["id"] for c in charts if c.get("slice_name") == name]
if not ids:
    print(f"   chart '{name}' not found after import", file=sys.stderr)
    sys.exit(1)

payload = json.dumps({"query_context": qc})
for cid in ids:
    out = curl("-b", jar, "-X", "PUT", *auth, "-H", f"X-CSRFToken: {csrf}",
               "-H", f"Referer: {url}/", "-H", "Content-Type: application/json",
               "--data-binary", payload, f"{url}/api/v1/chart/{cid}")
    if '"result"' not in out:
        print(f"   query_context PUT failed for '{name}': {out[:200]}", file=sys.stderr)
        sys.exit(1)
    print(f"   query_context reconciled: {name} (chart {cid})")
PY
done

rm -f "$COOKIE_JAR"
if [ "$status" -eq 0 ]; then
  echo ">> Superset dashboards imported."
else
  echo ">> one or more imports failed." >&2
fi
exit "$status"
