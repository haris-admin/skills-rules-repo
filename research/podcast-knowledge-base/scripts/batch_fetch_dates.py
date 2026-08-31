#!/usr/bin/env python3
"""Batch fetch YouTube video upload dates for large channels (>100 episodes).
Uses subprocess (NOT Hermes tool calls) to avoid the 50-call limit in execute_code.
Saves progress to a JSON state file — resume-safe if interrupted.

Usage:
    # First run (creates /tmp/channel_video_ids.txt first):
    /tmp/podcast_venv/bin/yt-dlp --flat-playlist --playlist-end 500 \
        --print '%(id)s' 'https://www.youtube.com/@HANDLE' > /tmp/channel_video_ids.txt
    python3 -u batch_fetch_dates.py --input /tmp/channel_video_ids.txt --cutoff 20250606

    # Resume from saved state:
    python3 -u batch_fetch_dates.py --input /tmp/channel_video_ids.txt --cutoff 20250606

State file is auto-saved at /tmp/batch_dates_state.json.
"""

import subprocess, json, time, sys, os, argparse

YT_DLP = '/tmp/podcast_venv/bin/yt-dlp'
STATE_FILE = '/tmp/batch_dates_state.json'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='File with video IDs (one per line)')
    parser.add_argument('--cutoff', default='20250606', help='Date cutoff YYYYMMDD (default: 20250606)')
    parser.add_argument('--state', default=STATE_FILE, help='Progress state file')
    args = parser.parse_args()

    # Load or create state
    if os.path.exists(args.state):
        with open(args.state) as f:
            state = json.load(f)
        dates = state.get('dates', {})
        last_idx = state.get('last_idx', 0)
    else:
        dates, last_idx = {}, 0

    with open(args.input) as f:
        video_ids = [line.strip() for line in f if line.strip()]

    print(f"Starting from index {last_idx}, {len(dates)} dates cached, total {len(video_ids)} videos", flush=True)

    for i in range(last_idx, len(video_ids)):
        vid = video_ids[i]
        if vid in dates:
            continue

        try:
            r = subprocess.run(
                [YT_DLP, '--print', '%(upload_date)s', '--', vid],
                capture_output=True, text=True, timeout=10
            )
            date_str = r.stdout.strip()
            if date_str and date_str not in ('NA', 'None', ''):
                dates[vid] = date_str
        except Exception:
            pass

        if i % 25 == 0 or i == len(video_ids) - 1:
            with open(args.state, 'w') as f:
                json.dump({'dates': dates, 'last_idx': i + 1, 'total': len(video_ids)}, f)
            in_range = sum(1 for d in dates.values() if d >= args.cutoff)
            print(f"  {i+1}/{len(video_ids)} | {len(dates)} dates | {in_range} in window", flush=True)

        time.sleep(0.2)

    # Final save
    with open(args.state, 'w') as f:
        json.dump({'dates': dates, 'last_idx': len(video_ids), 'total': len(video_ids)}, f)

    in_range = sum(1 for d in dates.values() if d >= args.cutoff)
    out_range = sum(1 for d in dates.values() if d < args.cutoff)
    print(f"\nDONE: {len(dates)}/{len(video_ids)} dates | {in_range} in window | {out_range} older", flush=True)


if __name__ == '__main__':
    main()
