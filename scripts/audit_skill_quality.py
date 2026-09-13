#!/usr/bin/env python3
"""Skill-quality audit for skills-rules-repo.

`validate.py` checks structural minimums (frontmatter present, name matches
folder, description non-trivial) required for CI to pass. This script checks
the same corpus against Anthropic's official Skill-authoring rubric
(platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) —
things a skill can satisfy `validate.py` while still failing at: a
description that doesn't state when to use the skill, a body over the
500-line guideline, bundled files SKILL.md never points Claude to, reference
chains more than one level deep, or a name using a reserved word.

Read-only. Discovery mirrors sync.sh / generate_catalog.py's own glob so the
count always matches what actually ships to `~/.claude/skills`.

Usage:
    python3 scripts/audit_skill_quality.py            # full report
    python3 scripts/audit_skill_quality.py --summary  # aggregate counts only
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

ROOT_DIR = Path(__file__).resolve().parent.parent
RESERVED_WORDS = {"anthropic", "claude"}
VAGUE_NAMES = {"helper", "helpers", "utils", "util", "tools", "tool", "documents",
               "data", "files", "misc", "general", "stuff"}

# Kept in sync with generate_catalog.py's SKIP_TOP_LEVEL_DIRS / validate.py's copy.
SKIP_TOP_LEVEL_DIRS = {".git", ".github", ".archive", "node_modules", "templates"}

TRIGGER_MARKERS = [
    "use when", "used when", "use for", "use this", "use if", "invoke when",
    "invoke this", "trigger", "when the user", "when asked", "when a user",
    "when someone", "when working", "when running", "when creating",
    "when building", "when writing", "when managing", "when reviewing",
    "when adding", "when changing", "when the ", " use ",
]
VAGUE_DESC_PHRASES = ["helps with", "does stuff", "processes data",
                       "general purpose", "various tasks", "helps you"]


def discover_skill_dirs():
    """Every <top-level-dir>/<name>/SKILL.md, deduplicated by resolved path —
    the same set sync.sh actually syncs. See generate_catalog.py's identical
    logic (kept separate here rather than imported, matching this repo's
    existing pattern of each script owning its own copy)."""
    found = {}
    seen_paths = set()

    def consider(skill_dir):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            return
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            return
        resolved = skill_md.resolve()
        if resolved in seen_paths:
            return
        seen_paths.add(resolved)
        found[skill_dir.name] = skill_dir.relative_to(ROOT_DIR)

    for top in sorted(ROOT_DIR.iterdir()):
        if not top.is_dir() or top.name.startswith(".") or top.name in SKIP_TOP_LEVEL_DIRS:
            continue
        for sub in sorted(top.iterdir()):
            consider(sub)
    return found


def parse_frontmatter(content):
    if not content.startswith("---"):
        return None, "no frontmatter"
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "unterminated frontmatter"
    data, current_key, multiline = {}, None, []
    for line in parts[1].splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            if current_key and multiline:
                data[current_key] = " ".join(multiline).strip()
                multiline = []
            key, val = line.split(":", 1)
            current_key = key.strip()
            val = val.strip()
            if val in (">-", ">", "|", "|-"):
                multiline = []
            elif val:
                data[current_key] = val.strip('"').strip("'")
        elif current_key:
            multiline.append(line.strip())
    if current_key and multiline:
        data[current_key] = " ".join(multiline).strip()
    return data, None


def check_description(desc):
    issues = []
    if not desc:
        return ["missing description"]
    if len(desc) > 1024:
        issues.append(f"description {len(desc)} chars (>1024 limit)")
    if re.match(r"^\s*I\b", desc) or re.search(r"\bI can\b|\bI'll\b|\bI will\b", desc):
        issues.append("description written in first person ('I ...')")
    if re.search(r"\byou can\b|\byou'll\b|\byour\b", desc, re.I):
        issues.append("description addresses the user directly ('you ...') instead of third person")
    if not any(m in desc.lower() for m in TRIGGER_MARKERS):
        issues.append("no explicit trigger condition (states what it does, not when to use it)")
    if any(p in desc.lower() for p in VAGUE_DESC_PHRASES):
        issues.append("vague/generic description phrase")
    return issues


def check_name(name, dirname):
    issues = []
    if not name:
        return ["missing name in frontmatter"]
    if name != dirname:
        issues.append(f"frontmatter name '{name}' != directory name '{dirname}'")
    if not re.match(r"^[a-z0-9-]+$", name):
        issues.append("name has invalid characters (must be lowercase/digits/hyphens)")
    if len(name) > 64:
        issues.append(f"name {len(name)} chars (>64 limit)")
    if any(rw in name.split("-") for rw in RESERVED_WORDS):
        issues.append("name contains reserved word (anthropic/claude)")
    if name in VAGUE_NAMES:
        issues.append("vague/generic name")
    return issues


def check_nesting(skill_dir_abs, skill_md_body):
    """Reference files linked from SKILL.md that themselves link to further
    .md files — a 2+ level-deep chain, which the official guidance says
    Claude may only partially read (head -N) rather than in full.

    Only a REAL problem if that further file isn't ALSO independently linked
    directly from SKILL.md (many skills deliberately cross-link two sibling
    reference files AND link both directly from SKILL.md — that's one-hop
    reachable either way, not a real nesting issue). Checked against known
    cases in this repo (hermes-agent, comfyui, humanizer, wsl-cron-test-runner,
    productivity/box, pluto-weekly-review, research-paper-writing) — every one
    turned out to already satisfy this, so this refinement matters in practice,
    not just in theory."""
    direct_links = {l.split("#")[0] for l in
                    re.findall(r'\]\(([^)]+\.md)\)', skill_md_body)}
    nested = []
    for md in skill_dir_abs.rglob("*.md"):
        if md.name == "SKILL.md":
            continue
        rel = str(md.relative_to(skill_dir_abs))
        if rel not in direct_links:
            continue
        try:
            sub_links = set(re.findall(r'\]\(([^)]+\.md)\)', md.read_text(errors="ignore")))
        except Exception:
            continue
        # drop any sub-link that's also directly reachable from SKILL.md itself
        # (by full relative path or by bare filename, matching check_orphans's
        # own reachability definition)
        truly_nested = {
            s for s in sub_links
            if s not in direct_links
            and Path(s).name not in skill_md_body
            and s not in skill_md_body
        }
        if truly_nested:
            nested.append((rel, sorted(truly_nested)[:3]))
    return nested


def check_orphans(skill_dir_abs, skill_md_body):
    """references/*.md files SKILL.md never mentions at all — link, backtick,
    or bare prose. Per the official guidance: 'If Claude never accesses a
    bundled file, it might be unnecessary or poorly signaled.'

    Scoped to references/*.md only — NOT templates/, tests/, scripts/,
    LICENSE, README.md, pyproject.toml, etc. Those are legitimate unlinked
    infrastructure (packaging metadata, test suites, helper modules Claude
    executes rather than reads); flagging them as 'orphaned documentation'
    produced 100% false positives when checked against this repo's actual
    skills (docx, pdf, powerpoint, xlsx, google-workspace, local-places,
    skill-creator, github-issues, and others all bundle such files by design).

    Also excludes references/*.md files covered by a templated/glob pattern
    mentioned in SKILL.md (e.g. `references/styles/<style>.md` covering an
    entire catalog directory like creative/baoyu-infographic's 41 style/layout
    files) — that's an intentional pattern reference, not an orphan."""
    orphans = []
    for f in skill_dir_abs.rglob("*"):
        if f.is_dir() or f.name in ("SKILL.md", ".DS_Store"):
            continue
        if not (str(f.relative_to(skill_dir_abs)).startswith("references" + "/") and f.suffix == ".md"):
            continue
        rel = str(f.relative_to(skill_dir_abs))
        if rel in skill_md_body or f.name in skill_md_body:
            continue
        parent = str(f.parent.relative_to(skill_dir_abs))
        if (re.search(re.escape(parent) + r"/<[^>]+>\.md", skill_md_body)
                or re.search(re.escape(parent) + r"/\*", skill_md_body)):
            continue
        orphans.append(rel)
    return orphans


def main():
    summary_only = "--summary" in sys.argv
    skill_dirs = discover_skill_dirs()
    print(f"Total skills discovered: {len(skill_dirs)}")
    print()

    stats = defaultdict(int)
    long_files = []
    all_issues = defaultdict(list)

    for name, relpath in sorted(skill_dirs.items()):
        skill_dir_abs = ROOT_DIR / relpath
        md = skill_dir_abs / "SKILL.md"
        try:
            content = md.read_text(errors="ignore")
        except Exception as e:
            all_issues[str(relpath)].append(f"unreadable: {e}")
            continue

        data, fm_err = parse_frontmatter(content)
        if fm_err:
            all_issues[str(relpath)].append(f"frontmatter: {fm_err}")
            stats["frontmatter_error"] += 1
            continue

        for i in check_name(data.get("name", ""), name):
            all_issues[str(relpath)].append(f"name: {i}")
            stats["name_issue"] += 1
        for i in check_description(data.get("description", "")):
            all_issues[str(relpath)].append(f"description: {i}")
            stats["description_issue"] += 1

        body = content.split("---", 2)[2] if content.count("---") >= 2 else content
        line_count = len(body.splitlines())
        if line_count > 500:
            long_files.append((str(relpath), line_count))
            all_issues[str(relpath)].append(f"body {line_count} lines (>500 guideline)")
            stats["too_long"] += 1

        orphans = check_orphans(skill_dir_abs, body)
        if orphans:
            all_issues[str(relpath)].append(
                f"{len(orphans)} orphaned file(s) SKILL.md never mentions: {orphans[:5]}")
            stats["orphans"] += 1

        nested = check_nesting(skill_dir_abs, body)
        if nested:
            all_issues[str(relpath)].append(f"nested reference chain (2+ levels deep): {nested[:2]}")
            stats["nested_refs"] += 1

    print("=== Aggregate stats ===")
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print()

    print(f"=== Files over 500 lines ({len(long_files)}) ===")
    for relpath, n in sorted(long_files, key=lambda x: -x[1]):
        print(f"  {n:5d}  {relpath}")

    if summary_only:
        return

    print()
    print(f"=== All flagged skills ({len(all_issues)}) ===")
    for relpath, issues in sorted(all_issues.items()):
        print(f"\n[{relpath}]")
        for i in issues:
            print(f"  - {i}")


if __name__ == "__main__":
    main()
