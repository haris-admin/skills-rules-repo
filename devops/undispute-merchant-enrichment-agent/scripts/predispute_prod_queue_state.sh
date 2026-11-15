#!/usr/bin/env bash
# Deterministic gate for the PRODUCTION worker cron: idle | working:<job_id> | stuck:<job_id>
exec python3 "$HOME/.hermes/scripts/predispute_queue_state.py" --prod
