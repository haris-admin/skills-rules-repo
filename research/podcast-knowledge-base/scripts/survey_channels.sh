#!/usr/bin/env bash
# Survey candidate YouTube channels BEFORE adding them to podcast_kb.
#
# Usage:  bash scripts/survey_channels.sh handle1 handle2 ...      (@ optional)
#
# For each handle prints  <channel_id>|<newest 3 titles>  or  NOT FOUND.
# The channel_id is the first field — paste it straight into the INSERT.
#
# Why this and not a web search: a handle can exist, be spelled right, and still
# be a CLIPS/archive channel or an unrelated namesake. Three real recent titles
# are the evidence that the handle is the show you think it is. Rate: listing is
# cheap, but do NOT fan this out into parallel shards — the same IP serves the
# transcript endpoint the nightly ingest depends on.
set -u
YTDLP=${YTDLP:-/tmp/podcast_venv/bin/yt-dlp}
[ -x "$YTDLP" ] || YTDLP=$(command -v yt-dlp)
[ -n "${YTDLP:-}" ] || { echo "yt-dlp not found (rebuild /tmp/podcast_venv)" >&2; exit 2; }

for h in "$@"; do
  h=${h#@}
  out=$("$YTDLP" --flat-playlist --playlist-end 3 --no-warnings \
        --print '%(channel_id)s|%(title).62s' \
        "https://www.youtube.com/@${h}/videos" 2>/dev/null | head -3)
  if [ -n "$out" ]; then
    printf '@%s ::\n' "$h"
    printf '%s\n' "$out" | sed 's/^/     /'
  else
    printf '@%s :: NOT FOUND / unavailable\n' "$h"
  fi
  sleep 2
done
