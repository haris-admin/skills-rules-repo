#!/usr/bin/env python3
"""Decode SiliconFlow pricing from the .cn / .com pricing pages.

Why this exists: siliconflow.cn/pricing embeds model prices in Next.js RSC
"flight" data, triple-escaped inside self.__next_f.push([1,"..."]) chunks.
Naive greps for 'inputPrice' hit escaped junk; naive regexes for the chunk
terminator fail because it is `"])` + `</script>` with NO semicolon. This
script does the full unescape + RSC $ref resolution in one shot.

Usage:
    curl -sL -A "Mozilla/5.0 ... Chrome/126.0" -o /tmp/sf_cn.html https://siliconflow.cn/pricing
    python3 decode_sf_flight.py /tmp/sf_cn.html

Output: one line per model:  model | in=<inputPrice> out=<outputPrice> | status
The .cn page prices are RMB (¥); the .com page is a Framer site and needs a
different approach (see notes at bottom).

Verified 2026-08-09 on the .cn pricing page (DeepSeek-V4-Flash ¥1/¥2, GLM-5.2
¥6/¥28, Qwen3-Coder-30B ¥0.7/¥2.8 ...). Treat numbers as a snapshot.
"""
import json
import re
import sys


def decode_flight(html: str) -> str:
    """Extract + unescape the concatenated Next.js flight stream from raw HTML."""
    # Escape-aware content matcher: any run of non-quote/non-backslash chars,
    # or any backslash-escape pair. Terminator is `"])` (no semicolon, then
    # </script>), because the closing quote itself is escaped as `\"` in the file.
    pat = re.compile(r'__next_f\.push\((\[1,"(?:[^"\\]|\\.)*"\])', re.S)
    flight = ''
    for arr_s in pat.findall(html):
        try:
            flight += json.loads(arr_s)[1]  # layer 1: JS string literal
        except Exception as e:
            print(f'chunk decode err: {e}', file=sys.stderr)
    return flight


def parse_models(flight: str):
    """Parse RSC key:value lines and resolve $ref references into model dicts."""
    raw = {}
    for ln in flight.split('\n'):
        m = re.match(r'^([0-9a-fA-F]+):(.*)$', ln, re.S)
        if m and m.group(1) not in raw:
            raw[m.group(1)] = m.group(2)

    def resolve(val, depth=0):
        if depth > 15 or isinstance(val, (int, float, bool)) or val is None:
            return val
        if isinstance(val, str):
            m = re.fullmatch(r'\$([0-9a-fA-F]+)', val)
            if m and m.group(1) in raw:
                try:
                    return resolve(json.loads(raw[m.group(1)]), depth + 1)
                except Exception:
                    return val
            return val
        if isinstance(val, list):
            return [resolve(x, depth + 1) for x in val]
        if isinstance(val, dict):
            return {k: resolve(v, depth + 1) for k, v in val.items()}
        return val

    models = []
    for v in raw.values():
        try:
            obj = resolve(json.loads(v))
        except Exception:
            continue
        if isinstance(obj, dict) and ('modelName' in obj or 'targetModelName' in obj) \
                and 'inputPrice' in obj:
            pricing = obj.get('pricing') or []
            out = next((p.get('price') for p in pricing
                        if p.get('specification') == 'completion'), None)
            models.append((obj.get('modelName') or obj.get('targetModelName'),
                           obj.get('inputPrice'), out, obj.get('status')))
    return models


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    html = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    flight = decode_flight(html)
    if not flight:
        print('no flight chunks found — page structure changed, or you passed the wrong file', file=sys.stderr)
        sys.exit(2)
    seen = set()
    for name, inp, outp, status in sorted(parse_models(flight)):
        key = (name, inp, outp)
        if key in seen:
            continue
        seen.add(key)
        print(f'{name} | in={inp} out={outp} | {status}')

print('''
NOTES:
- .cn page = RMB (¥). International .com pricing is a Framer site: model
  prices live in framerusercontent.com/sites/.../searchIndex-*.json under
  blocks like "Input Price","$","0.13","/ M Tokens",[,"Cache Read","0.028",]
  "Output Price","0.28". Grep that JSON for '"Input Price"' and read the
  following array elements; blocks are ~50 model pages (one per /models/<slug>).
- DeepInfra (deepinfra.com/pricing) embeds model JSON in __NEXT_DATA__ with
  cents_per_input_token / cents_per_output_token — CENTS per token: $/M =
  value * 1e6 / 100. On per-model pages the first "$"-bearing NEXT_DATA match
  may belong to a DIFFERENT (related) model — render the page instead.
''')
