#!/usr/bin/env python3
"""One-command answer to "is this lane DRAINED or STARVED?"

The router's summary line (`free-routed=0 failed=0 skipped=0 cooling=[]`) is IDENTICAL for a
fully-routed corpus and for a lane whose window is too narrow to see the work — so a run of zeros
must be resolved by counting, not by reading the summary. This does that count and nothing else:

    all-time candidates (transcript >= MIN_TRANSCRIPT_CHARS)   vs   the router's `done` set

`remaining == 0`  -> CAUGHT UP (0 is correct, stay quiet).
`remaining > 0`   -> STARVED: the ids are printed and the first few are fetched to show whether they
                     are reachable at all (an id that is not fetchable is a judged/no-transcript
                     artifact, not queued work).

Run:  python3 ~/.hermes/skills/research/podcast-knowledge-base/scripts/router_coverage_probe.py

Uses the SAME two helpers the router uses (podcast_three_filters.pick_ids,
podcast_capture_verify.fetch_episodes), so its notion of "candidate" cannot drift from the lane's.
Carries the cron env guard: the gateway exports a foreign interpreter's site-packages via
PYTHONPATH, which shadows the venv's pydantic_core — strip the env, drop the foreign sys.path
entries, and re-exec the venv python (the re-exec alone is not enough, and the strip alone is not
either).
"""
import os
import pathlib
import sys

HOME = pathlib.Path.home()
VENV = HOME / ".hermes" / "venv" / "bin" / "python3"

# --- cron env guard (see the skill's "Cron env guard" recipe) -------------
os.environ.pop("PYTHONPATH", None)
os.environ.pop("PYTHONHOME", None)
if VENV.exists() and os.path.realpath(sys.executable) != os.path.realpath(VENV) \
        and not os.environ.get("_ROUTER_COVERAGE_GUARD"):
    os.environ["_ROUTER_COVERAGE_GUARD"] = "1"
    os.execv(str(VENV), [str(VENV), __file__])

import importlib.util  # noqa: E402
import json  # noqa: E402

sys.path.insert(0, str(HOME / ".hermes/scripts"))


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HOME / ".hermes/scripts" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tf = _load("tf", "podcast_three_filters.py")
pv = _load("pv", "podcast_capture_verify.py")

DONE = HOME / ".hermes/cache/scratch/free_router_done.json"

try:
    done = set(int(i) for i in json.loads(DONE.read_text())["done"])
except Exception as exc:  # a missing state file means NOTHING is routed, not everything
    print(f"done state unreadable ({type(exc).__name__}: {exc}) -> treating done as EMPTY")
    done = set()

# ALL-TIME is the whole point: a window narrower than the corpus turns a drained queue into a
# starved one with the same summary line (the 400-day window hid 15 episodes for months).
all_time = [int(i) for i in tf.pick_ids(100000, None, None)]
windowed = [int(i) for i in tf.pick_ids(3650, None, None)]
missing = [i for i in all_time if i not in done]

print(f"python        : {sys.executable}")
print(f"candidates    : {len(all_time)} all-time (>= {pv.MIN_TRANSCRIPT_CHARS} char transcript) "
      f"| {len(windowed)} inside the wrapper's 3650-day window | max_id={max(all_time) if all_time else 0}")
print(f"done set      : {len(done)}")
print(f"REMAINING     : {len(missing)}")

if not missing:
    print("VERDICT       : CAUGHT UP — the queue is genuinely drained; 0 routed is correct.")
else:
    print(f"VERDICT       : STARVED — {len(missing)} candidate(s) are not in `done`; queued ids: {missing[:40]}")
    for i in missing[:10]:
        eps = pv.fetch_episodes(episode_id=i, ignore_ledger=True)
        if eps:
            e = eps[0]
            print(f"   id={i} FETCHABLE show={e.get('show')!r} published={e.get('published')} "
                  f"chars={len(e['transcript'])}")
        else:
            print(f"   id={i} NOT FETCHABLE (no usable transcript row) — artifact, not queued work")
