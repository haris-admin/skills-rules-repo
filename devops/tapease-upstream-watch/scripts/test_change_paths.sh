#!/usr/bin/env bash
# Change-detection proof: tamper a TEMP copy of the state so each detector fires, run the real
# script with --no-email against it, and check the rendered message. Production state untouched.
# Usage: bash scripts/test_change_paths.sh
set -u
SCRATCH=/home/habib/.hermes/cache/scratch/uwtest2
rm -rf "$SCRATCH"; mkdir -p "$SCRATCH"
cp /home/habib/.hermes/state/upstream-watch-state.json "$SCRATCH/state.json"
export UW_STATE="$SCRATCH/state.json"

python3 - "$SCRATCH/state.json" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
# 1) HTML page: force a fingerprint mismatch with a stale text/heading set
s = d['html']['clover-announcements']
s['fingerprint'] = 'stale'
s['text'] = 'OLD TEXT THAT IS GONE'
s['headings'] = []
# 2) Oxygen: drop the known post and age one page -> new post + edited page
d['oxygen']['posts'] = []
d['oxygen']['pages'][0][1] = '2020-01-01T00:00:00'
d['oxygen']['fingerprint'] = 'stale'
# 3) Availability: pretend it was down
d['availability']['oxygen-home']['state'] = 'down'
json.dump(d, open(p, 'w'), indent=1)
print('tampered:', p)
PY

echo "########## change detection (expect HTML + oxygen content + availability sections)"
python3 /home/habib/.hermes/scripts/upstream_watch.py --no-email 2>&1 | head -30

echo
echo "########## immediately re-run (expect silence — change consumed)"
out=$(python3 /home/habib/.hermes/scripts/upstream_watch.py --no-email); echo "bytes=$(printf %s "$out" | wc -c)"
