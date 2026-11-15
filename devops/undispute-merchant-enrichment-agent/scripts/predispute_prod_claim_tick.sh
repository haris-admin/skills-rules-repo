#!/usr/bin/env bash
# Production claim tick (no_agent cron). Silent when the queue is empty.
# Exit 10 = a job was claimed; exit 3 = config refused — both are states,
# not scheduler faults, so they must not raise a cron error alert.
python3 "$HOME/.hermes/scripts/predispute_enrich_poll.py" --prod --quiet
code=$?
case "$code" in
  10|3) exit 0 ;;
  *) exit "$code" ;;
esac
