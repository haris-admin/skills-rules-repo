---
name: austrac-tranche2-digest
description: "Use when running the AUSTRAC Tranche 2 digest cron."
---

# AUSTRAC Tranche 2 digest

## Trigger
Scheduled digest: enforcement register changes, enrolment milestones, ASIC actions, digital-asset AFSL countdown, FATF milestones.

## Sources (check in this order, all public)
1. https://www.austrac.gov.au/about-us/record-our-actions/enforcement-actions-taken — named infringement notices (folder date in the PDF URL gives the month), EUs, court proceedings. Page footer carries "Last updated".
2. https://www.austrac.gov.au/news-and-media — media releases + featured articles. `/business/updates` can render stale cached listings; trust news-and-media.
2a. https://www.austrac.gov.au/industry-and-business/consultations — open consultations with "Open date" and "Submission deadline" lines. The page's own "Last updated" stamp lags badly (e.g. Mar 2026 while a Nov consultation is open) — ignore it. A new consultation also shows up as a new child item in the site-wide mega-menu, so a nav-only diff on any AUSTRAC page is a signal to check this index.
3. https://www.austrac.gov.au/new-austrac/enrol-us/enrol-us-overview — Reporting Entities Roll count, refreshed monthly (quote the "As of <date>" stamp).
4. https://www.asic.gov.au/newsroom — digital-asset licensing, CP 392, criminal/911A actions.
5. https://www.fatf-gafi.org/en/calendars/assessments.html — Australia row: possible onsite period + plenary date.

## Alert rules
- 🔴 only for a NEW enforcement outcome (court judgment, penalty, new named notice round) or a NEW near-term lodgement/submission deadline.
- 🟡 for milestones, counts, guidance, speeches.
- No new item since the state file → `[SILENT]`.

## Hard rules
- Enrolment numbers are COUNTS, never percentages — there is no denominator (firms ≠ reporting entities). Say "counts, not coverage rates".
- Enrolment clock is 28 days from first designated service, not a fixed calendar date (AUSTRAC release 30 Sep 2026).
- Annual compliance report now follows financial years: period 1 Jul 2026 – 30 Jun 2027, lodgement window 1 Jul – 30 Sep 2027 (AUSTRAC page cites Act s47, Rules 9-9).
- DAF Act commencement: ASIC says 8 Apr 2027; some law-firm sources say 9 Apr 2027 — cite as "8 Apr 2027 (ASIC)".
- Keep a dedup state file at ~/.hermes/data/tranche2_digest_state.json (seen items + deadline calendar) and update it each run.

## Change detection (fast, reliable)
Do NOT trust web_extract for change detection on AUSTRAC — it serves stale cached renders (e.g. shows a 12 Oct release as newest while an 11 Nov release is live). Instead:
1. `curl -sL -A '<Chrome UA>'` the page to a file, keep yesterday's file, and `diff <(sed 's/></>\n</g' old.html) <(sed 's/></>\n</g' new.html)`. AUSTRAC/Drupal pages change only in `form_build_id`/`honeypot_time` tokens when content is unchanged — a 2-line token-only diff means NO change.
2. Grep the rendered text for `Last updated` and the newest `N Month 2026` dates to confirm.
3. ASIC media releases are JS-rendered with no RSS: load `/about-asic/news-centre/find-a-media-release/` in the browser and read titles+dates via JS (`main li` innerText). Newest release number (e.g. 26-281MR) is the reliable recency marker.
4. fatf-gafi.org is Cloudflare-challenged for curl and headless browser alike — use web_extract, which renders the full assessments table; read only the Australia row.
5. Federal Court outcomes: **AustLII feeds were retired in Nov 2026** — `/cgi-bin/feed/au/cases/cth/FCA` returns 410 Gone (slash, no-slash and `?path=` variants), `/au/cases/cth/FCA/recent.xml` and judgments.fedcourt.gov.au return 403. No working FCA feed; fall back to `web_search` for a named-case outcome (e.g. "Star Entertainment AUSTRAC un-redaction judgment") and treat silence as "no judgment yet" only when the search returns nothing newer than the last known item.
6. Infringement-notice round detection: read the "Infringement notices" section on the enforcement-register page itself — it is grouped by year and ordered newest-first. Do NOT fetch `/about-us/record-our-actions/infringement-notices/2026`: it is a **soft 404** (HTTP 200, body "Page not found", marker `page-node-1587`), and `/business/infringement-notices[-2026]` hard-404s. New named notices also carry `/sites/default/files/<YYYY-MM>/...` PDF folders, but that folder scan only works from a page that actually lists them. Notices are published *after* the 28-day pay-by window, so the PDF folder month is publication, not issue, date — back out the issue date from "payable on or before <date>" minus 28 days.
7. Notice PDFs are partly scanned (page 1 image, no text layer). Render with pymupdf and read page 1 with vision:
   `uv venv .venv_ocr && uv pip install --python .venv_ocr/bin/python pymupdf`, then `pix = page.get_pixmap(dpi=180); pix.save(...)`, then `vision_analyze` the PNG. There are no poppler/pdftotext/OCR binaries on this host, and `read_file` fails with NeedsOcrError on these PDFs.

## Output
Telegram-ready, ~2 min read: alert-level block first, then watch items, then "on the horizon". Bold labels, no tables.
