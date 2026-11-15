#!/usr/bin/env python3
"""Audit the skills-rules-repo for overlaps, duplicate names, broken links, and stale README refs.

Usage: python3 audit_skills_repo.py [repo_path]
Default repo path: /mnt/c/Code/github/haris-admin/skills-rules-repo
Exit code 0 = clean, 1 = issues found.
"""
import os, re, sys
from collections import defaultdict

REPO = sys.argv[1] if len(sys.argv) > 1 else '/mnt/c/Code/github/haris-admin/skills-rules-repo'

skills = []
for cat in os.listdir(REPO):
    cd = os.path.join(REPO, cat)
    if not os.path.isdir(cd) or cat.startswith('.'):
        continue
    for skill in os.listdir(cd):
        sd = os.path.join(cd, skill)
        smd = os.path.join(sd, 'SKILL.md')
        if not os.path.isdir(sd) or not os.path.exists(smd):
            continue
        text = open(smd, encoding='utf-8', errors='replace').read()
        m = re.search(r'^name:\s*["\']?([^"\'\n]+)', text, re.M)
        fname = m.group(1).strip().strip('"\'') if m else ''
        skills.append({'name': skill, 'cat': cat, 'path': os.path.join(cat, skill), 'fname': fname, 'text': text})

issues = []

# 1. Duplicate names
byname = defaultdict(list)
for s in skills:
    byname[s['name'].lower()].append(s)
for n, v in byname.items():
    if len(v) > 1:
        issues.append(f"DUPLICATE NAME '{n}': {[s['path'] for s in v]}")

# 2. Flat <-> category overlap
flat = {s['name'] for s in skills if s['cat'] == 'skills'}
cat_skills = {s['name'] for s in skills if s['cat'] != 'skills'}
overlap = flat & cat_skills
if overlap:
    issues.append(f"FLAT<->CATEGORY OVERLAP (sync.sh double-copies): {sorted(overlap)}")

# 3. Frontmatter name mismatch
for s in skills:
    if s['fname'] and s['fname'] != s['name']:
        issues.append(f"NAME MISMATCH: dir {s['path']} vs frontmatter '{s['fname']}'")

# 4. Broken .md links (resolve vs skill dir, category dir, repo root)
def check_broken(cat, skill):
    sd = os.path.join(REPO, cat, skill)
    text = open(os.path.join(sd, 'SKILL.md'), encoding='utf-8', errors='replace').read()
    broken = []
    for m in re.finditer(r'\[[^\]]*\]\(([^)#]+\.md)\)', text):
        rel = m.group(1).strip()
        cands = [os.path.join(sd, rel), os.path.join(REPO, cat, rel), os.path.join(REPO, rel)]
        if not any(os.path.exists(c) for c in cands):
            broken.append(rel)
    return broken

for s in skills:
    b = check_broken(s['cat'], s['name'])
    if b:
        issues.append(f"BROKEN LINKS {s['path']}: {b[:4]}")

# 5. Placeholder scan (contextual — raw hits often false positive)
for s in skills:
    hits = [m.group(0) for m in re.finditer(r'\[SKILL_PRUNED\]|PLACEHOLDER|lorem ipsum', s['text'], re.I)]
    if hits:
        issues.append(f"PLACEHOLDER CANDIDATES {s['path']}: {hits} (verify context — often false positives)")

# 6. Stale README refs (moved skills still referenced at old flat path)
readme_path = os.path.join(REPO, 'README.md')
if os.path.exists(readme_path):
    readme = open(readme_path, encoding='utf-8', errors='replace').read()
    for s in skills:
        if s['cat'] != 'skills' and f'./skills/{s["name"]}/' in readme:
            issues.append(f"README STALE LINK: ./skills/{s['name']}/ should be ./{s['cat']}/{s['name']}/")

print(f"Total skills: {len(skills)}")
if issues:
    print(f"\n{len(issues)} issue(s):")
    for i in issues:
        print(f"  - {i}")
    sys.exit(1)
else:
    print("\nCLEAN: no duplicates, no overlap, no name mismatches, no broken links.")
    sys.exit(0)
