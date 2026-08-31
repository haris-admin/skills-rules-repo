#!/usr/bin/env python3
"""Verify an AMLHive content draft against public-copy guardrails and the word-count target.

Usage:
    python verify_amlhive_draft.py <path-to-draft.md> [--min 1100 --max 1400]

Exit 0 if all checks pass, 1 otherwise. Prints a PASS/FAIL table.
Read any FAIL against the actual sentence before acting — regexes span
sentences and can false-positive on compliant copy (e.g. a multi-line
"file.*SMR.*for you" pattern matched "eKYC does not file reports for you").

Checks covered:
  - body word count in [--min, --max] (markdown symbols stripped; inline
    //VERIFY annotations count toward the total)
  - trial offer wording ("14-day free trial" only)
  - tagline present; no statutory-officer / legal-adviser / certifier claims
  - C146 "contact for pricing"; no delivery-date promises
  - general-information disclaimer present
  - no AUSTRAC-approval / auto-lodgement claims
  - banned marketing words absent; SMR not SAR; TTR not CTR
  - no Haris personal reference; no other-venture brand names (reverse firewall)
"""
import re
import sys

BANNED_WORDS = r'\b(seamless|robust|leverage|synergies|AI-powered|enterprise-grade)\b'
VENTURES = r'\b(finai|paylicence|exitlens|tokenpilot|cloudproof|tapease|agentgate|cloudwise|verifylink)\b'


def wc(s: str) -> int:
    s = re.sub(r'[#*_>`\-]', ' ', s)
    return len(s.split())


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print('usage: verify_amlhive_draft.py <draft.md> [--min N --max N]')
        return 2
    path = args[0]
    lo = 1100
    hi = 1400
    if '--min' in sys.argv:
        lo = int(sys.argv[sys.argv.index('--min') + 1])
    if '--max' in sys.argv:
        hi = int(sys.argv[sys.argv.index('--max') + 1])

    text = open(path, encoding='utf-8').read()
    body = text.split('<!--')[0]  # visible article body only
    bw = wc(body)
    pw = wc(re.sub(r'//VERIFY:[^\n]*', '', body))  # publishable prose

    checks = {
        'word count in range': lo <= bw <= hi,
        '14-day free trial only': bool(re.search(r'14-day free trial', body)),
        'no two-week/30-day': not re.search(r'two-week|two week|30-day|30 day', body, re.I),
        'tagline present': 'Your Virtual Compliance Officer' in body,
        'no statutory-officer/legal-adviser/certifier': not re.search(
            r'statutory officer|legal adviser|certifier', body, re.I),
        'C146 contact-for-pricing': 'contact for pricing' in body.lower(),
        'no delivery-date promise': not re.search(
            r'deliver\w*.*\bby\b|delivery date|\bwithin \d+ (days|weeks)', body, re.I),
        'general-info disclaimer': 'general information only' in body,
        'not AUSTRAC-approved': not re.search(r'AUSTRAC-approved|approved by AUSTRAC', body, re.I),
        'no auto-lodgement claim': not re.search(r'file.*(SMR|TTR).*for you|automatically (file|lodge)', body, re.I),
        'no banned words': not re.search(BANNED_WORDS, body, re.I),
        'SMR not SAR': 'SAR' not in body,
        'TTR not CTR': 'CTR' not in body,
        'no other-venture brands (reverse firewall)': not re.search(VENTURES, body, re.I),
        'no Haris personal reference': 'haris' not in body.lower(),
    }
    ok = True
    print(f'body words (incl //VERIFY): {bw} | publishable prose: {pw} | target {lo}-{hi}')
    for k, v in checks.items():
        print(f"{'PASS' if v else 'FAIL'}  {k}")
        ok = ok and v
    print(f'VERIFY markers in body: {body.count("//VERIFY")}')
    if ok:
        print('ALL PASS')
        return 0
    print('ISSUES — read FAILs against the actual sentence before editing')
    return 1


if __name__ == '__main__':
    sys.exit(main())
