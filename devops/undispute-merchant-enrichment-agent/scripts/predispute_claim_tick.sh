#!/usr/bin/env bash
# Pre-Dispute claim tick — the no_agent cron wrapper (delivers its stdout verbatim).
# Claims at most one merchant-enrichment job and prints a short block ONLY when a
# job is claimed or the claim path is broken; empty stdout = nothing delivered.
# The enrich/complete half is the agent worker gated by predispute_queue_state.py.
#
# Exit code 10 from the poll script means "a job was claimed" — that is success for
# the cron, NOT an error (the scheduler alerts on non-zero exits), so it is mapped
# to 0 here. Real failures already print a claim_failed block.
python3 /home/habib/.hermes/scripts/predispute_enrich_poll.py --quiet
code=$?
if [ "$code" -eq 10 ]; then exit 0; fi
exit "$code"
