#!/usr/bin/env bash
# Proof harness for upstream_watch.py — exercises the real script against a temp state and a
# deliberately broken status URL. Never touches the production state, never sends email.
# Usage: bash scripts/test_upstream_watch.sh   (expects ~/.hermes/scripts/upstream_watch.py)
set -u
SCRATCH=/home/habib/.hermes/cache/scratch/uwtest
rm -rf "$SCRATCH"; mkdir -p "$SCRATCH"
cp /home/habib/.hermes/state/upstream-watch-state.json "$SCRATCH/state.json"
export UW_STATE="$SCRATCH/state.json"

sed 's#https://status.clover.com/api/v2/summary.json#https://status.clover.invalid/api/v2/summary.json#' \
    /home/habib/.hermes/scripts/upstream_watch.py > "$SCRATCH/bad.py"

echo "########## T1 healthy run (real sources) — expect TOTAL SILENCE"
out=$(python3 /home/habib/.hermes/scripts/upstream_watch.py --no-email); rc=$?
echo "rc=$rc bytes=$(printf %s "$out" | wc -c)"

echo
echo "########## T2 failure run 1 of 2 — expect silence (below threshold)"
out=$(python3 "$SCRATCH/bad.py" --no-email); rc=$?
echo "rc=$rc bytes=$(printf %s "$out" | wc -c)"

echo
echo "########## T3 failure run 2 of 2 — expect the problem line"
python3 "$SCRATCH/bad.py" --no-email

echo
echo "########## T4 failure run 3 — expect silence again (already notified, alert-once)"
out=$(python3 "$SCRATCH/bad.py" --no-email); rc=$?
echo "rc=$rc bytes=$(printf %s "$out" | wc -c)"

echo
echo "########## T5 source healthy again — expect one recovery line"
python3 /home/habib/.hermes/scripts/upstream_watch.py --no-email

echo
echo "########## T6 recovery already reported — expect silence"
out=$(python3 /home/habib/.hermes/scripts/upstream_watch.py --no-email); rc=$?
echo "rc=$rc bytes=$(printf %s "$out" | wc -c)"

echo
echo "########## state failures/notified after tests"
python3 -c "import json;d=json.load(open('$SCRATCH/state.json'));print('failures',d.get('failures'));print('notified',d.get('notified'))"
