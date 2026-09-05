#!/usr/bin/env python3
"""
generate_catalog.py — regenerate the "Skills Catalog" and "Rules Catalog" tables
in README.md from the actual repository content.

The repo currently has ~290+ skills spread across topic-category directories
(agent-governance-and-git/, compliance/, backend-and-database/, etc.) plus the
flat skills/ directory, and 60+ files under rules/. The README's two catalog
tables were hand-maintained and had drifted badly out of date (missing most
skills, and showing raw YAML folding markers like ">-" as skill descriptions
where the original hand-rolled table generator failed to parse folded/
multi-line frontmatter scalars).

This script is the durable fix: it discovers every skill and rule directly
from the filesystem, parses frontmatter with the *same* parser
scripts/validate.py uses (so a fix to one text format only needs to happen in
one place), and regenerates both tables in place.

Usage:
    python3 scripts/generate_catalog.py            # regenerate README.md
    python3 scripts/generate_catalog.py --check    # exit 1 if README.md is
                                                     # out of date; write nothing

Run --check in CI (see .github/workflows/validate.yml) so the catalog can
never silently drift again — any PR that adds/removes/renames a skill or rule
without regenerating the README fails the build.
"""

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts"))

README_PATH = ROOT_DIR / "README.md"


def parse_frontmatter(content: str):
    """Parse SKILL.md YAML frontmatter using the same indentation-based
    approach as scripts/validate.py's parse_frontmatter(), with one fix:
    a plain (non-folded, no '>'/'|' indicator) multi-line scalar is
    concatenated with its continuation lines instead of being overwritten by
    them.

    scripts/validate.py's original parser does e.g.:
        description: Design, implement, and audit inclusive digital products
          using WCAG 2.2 Level AA standards.
    -> assigns data["description"] = the first line's text, then at the next
    flush point OVERWRITES it with only the continuation line ("using WCAG
    2.2 Level AA standards."), silently dropping the first line. This is a
    latent bug in the validator itself (see TECHNICAL_DEBT.md) that isn't
    caught there because validate.py only checks description length/presence,
    not content — but it does corrupt this catalog's Description column, so
    it's fixed here rather than inherited.
    """
    if not content.startswith("---"):
        return None, "Missing opening frontmatter delimiter (---)"
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "Missing closing frontmatter delimiter (---)"

    yaml_text = parts[1].strip()
    data = {}
    lines = yaml_text.splitlines()
    current_key = None
    first_line_val = ""
    multiline_val = []

    def flush():
        if current_key is None:
            return
        pieces = ([first_line_val] if first_line_val else []) + multiline_val
        if pieces:
            data[current_key] = " ".join(pieces).strip()

    for line in lines:
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            flush()
            key, val = line.split(":", 1)
            current_key = key.strip()
            val = val.strip()
            multiline_val = []
            first_line_val = "" if val in (">-", ">", "|", "|-") else val
        elif current_key:
            multiline_val.append(line.strip())

    flush()
    return data, None

# Top-level directories to never treat as skill-category directories.
# Mirrors sync.sh's "$REPO_DIR"/*/* discovery glob (which implicitly skips
# hidden dirs since bash globs don't match dotfiles by default), minus the
# templates/ directory, which holds the *template* SKILL.md, not a real skill.
SKIP_TOP_LEVEL_DIRS = {".git", ".github", ".archive", "node_modules", "templates"}

TRUNCATE_LEN = 150

SKILLS_TABLE_HEADER = ["| Skill Name | Description | References |", "| :--- | :--- | :--- |"]
RULES_TABLE_HEADER = ["| Rule File | Scope & Summary |", "| :--- | :--- |"]

H1_RE = re.compile(r"^#\s+(.+?)\s*$")


def escape_cell(text: str) -> str:
    """Escape characters that would break Markdown table syntax."""
    return text.replace("|", "\\|")


def truncate(text: str, limit: int = TRUNCATE_LEN) -> str:
    """Collapse whitespace/newlines and truncate on a word boundary with an ellipsis."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(",.;:- ") + "…"


# ---------------------------------------------------------------------------
# Skill discovery
# ---------------------------------------------------------------------------

def discover_skill_dirs(warnings):
    """Find every <top-level-dir>/<name>/SKILL.md, plus skills/*/SKILL.md.

    This matches the set sync.sh would actually sync (its
    "$REPO_DIR"/*/* "$REPO_DIR"/skills/* glob), except we explicitly skip
    SKIP_TOP_LEVEL_DIRS (.git, .github, .archive, node_modules, templates)
    and hidden directories, since those aren't real distributable skills.

    Returns a dict of folder_name -> skill_dir Path, deduplicated by resolved
    SKILL.md path (so a name matched by both the generic top-level scan and
    the explicit skills/* scan is only counted once).
    """
    found = {}
    seen_paths = set()

    def consider(skill_dir: Path):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            return
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            return
        resolved = skill_md.resolve()
        if resolved in seen_paths:
            return
        seen_paths.add(resolved)
        folder_name = skill_dir.name
        if folder_name in found:
            warnings.append(
                f"Duplicate skill folder name '{folder_name}' found at both "
                f"'{found[folder_name].relative_to(ROOT_DIR)}' and "
                f"'{skill_dir.relative_to(ROOT_DIR)}' — keeping the first one found."
            )
            return
        found[folder_name] = skill_dir

    for top in sorted(ROOT_DIR.iterdir()):
        if not top.is_dir() or top.name.startswith("."):
            continue
        if top.name in SKIP_TOP_LEVEL_DIRS:
            continue
        for sub in sorted(top.iterdir()):
            consider(sub)

    # Explicit skills/* pass for parity with sync.sh's literal glob (a no-op
    # in practice since "skills" is already a top-level dir covered above).
    skills_top = ROOT_DIR / "skills"
    if skills_top.is_dir():
        for sub in sorted(skills_top.iterdir()):
            consider(sub)

    return found


def pick_reference(skill_dir: Path):
    """Return (title, relative_link) for the first *.md file directly under
    references/, or None if there is no references/ dir or it has no .md files."""
    references_dir = skill_dir / "references"
    if not references_dir.is_dir():
        return None
    md_files = sorted(p for p in references_dir.iterdir() if p.is_file() and p.suffix == ".md")
    if not md_files:
        return None
    ref = md_files[0]
    title = ref.stem.replace("-", " ").replace("_", " ").title()
    rel = ref.relative_to(ROOT_DIR).as_posix()
    return title, f"./{rel}"


def build_skill_row(folder_name: str, skill_dir: Path, warnings):
    skill_md = skill_dir / "SKILL.md"
    try:
        content = skill_md.read_text(encoding="utf-8")
    except Exception as e:  # pragma: no cover - defensive
        warnings.append(f"[Skill: {folder_name}] Failed to read SKILL.md: {e}")
        content = None

    data = {}
    if content is not None:
        data, err = parse_frontmatter(content)
        if err:
            warnings.append(f"[Skill: {folder_name}/SKILL.md] {err}")
            data = {}
        data = data or {}

    fm_name = data.get("name")
    if not fm_name:
        warnings.append(f"[Skill: {folder_name}/SKILL.md] Missing 'name' in frontmatter; using folder name.")
    elif fm_name != folder_name:
        warnings.append(
            f"[Skill: {folder_name}/SKILL.md] Frontmatter name '{fm_name}' does not match "
            f"folder name '{folder_name}'; indexing under the folder name."
        )

    description = (data.get("description") or "").strip()
    if not description:
        warnings.append(f"[Skill: {folder_name}/SKILL.md] Missing or empty 'description' in frontmatter.")
        description_cell = "-"
    else:
        description_cell = escape_cell(truncate(description))

    rel_path = skill_md.relative_to(ROOT_DIR).as_posix()
    link = f"./{rel_path}"

    references_cell = "-"
    ref = pick_reference(skill_dir)
    if ref:
        title, ref_link = ref
        references_cell = f"[{escape_cell(title)}]({ref_link})"

    row = f"| **[{escape_cell(folder_name)}]({link})** | {description_cell} | {references_cell} |"
    return folder_name, row


def build_skills_table(warnings):
    skill_dirs = discover_skill_dirs(warnings)
    rows = []
    for folder_name, skill_dir in skill_dirs.items():
        rows.append(build_skill_row(folder_name, skill_dir, warnings))
    rows.sort(key=lambda item: item[0].lower())
    table_lines = list(SKILLS_TABLE_HEADER) + [row for _name, row in rows]
    return table_lines, len(rows)


# ---------------------------------------------------------------------------
# Rule discovery
# ---------------------------------------------------------------------------

def discover_rule_files():
    rules_dir = ROOT_DIR / "rules"
    if not rules_dir.is_dir():
        return []
    # Flat, no recursion — matches scripts/validate.py's own scope.
    return sorted(
        p for p in rules_dir.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.suffix == ".md"
    )


def extract_rule_title_and_summary(rule_path: Path, warnings):
    try:
        content = rule_path.read_text(encoding="utf-8")
    except Exception as e:  # pragma: no cover - defensive
        warnings.append(f"[Rule: {rule_path.name}] Failed to read file: {e}")
        return rule_path.stem.replace("-", " ").title(), "-"

    lines = content.splitlines()

    title = None
    idx = 0
    for i, line in enumerate(lines):
        m = H1_RE.match(line)
        if m:
            title = m.group(1).strip()
            idx = i + 1
            break

    if title is None:
        warnings.append(f"[Rule: {rule_path.name}] No H1 title found; using filename as display name.")
        title = rule_path.stem.replace("-", " ").title()

    # Skip blank lines between the H1 and the summary content.
    while idx < len(lines) and not lines[idx].strip():
        idx += 1

    summary_lines = []
    if idx < len(lines) and lines[idx].lstrip().startswith(">"):
        # A blockquote immediately after the title is the summary.
        while idx < len(lines) and lines[idx].lstrip().startswith(">"):
            summary_lines.append(re.sub(r"^\s*>\s?", "", lines[idx]))
            idx += 1
    else:
        # Otherwise take the first non-empty paragraph after the title.
        while idx < len(lines) and lines[idx].strip() and not lines[idx].lstrip().startswith("#"):
            summary_lines.append(lines[idx].strip())
            idx += 1

    summary = " ".join(s.strip() for s in summary_lines if s.strip())
    if not summary:
        warnings.append(f"[Rule: {rule_path.name}] No summary paragraph/blockquote found after the H1 title.")
        summary = "-"
    else:
        summary = truncate(summary)

    return title, summary


def build_rule_row(rule_path: Path, warnings):
    title, summary = extract_rule_title_and_summary(rule_path, warnings)
    rel_path = rule_path.relative_to(ROOT_DIR).as_posix()
    link = f"./{rel_path}"
    row = f"| **[{escape_cell(title)}]({link})** | {escape_cell(summary)} |"
    return title, row


def build_rules_table(warnings):
    rule_files = discover_rule_files()
    rows = [build_rule_row(p, warnings) for p in rule_files]
    rows.sort(key=lambda item: item[0].lower())
    table_lines = list(RULES_TABLE_HEADER) + [row for _title, row in rows]
    return table_lines, len(rows)


# ---------------------------------------------------------------------------
# README section replacement
# ---------------------------------------------------------------------------

def replace_section(lines, heading_keyword: str, new_table_lines):
    """Replace the content between the heading containing heading_keyword and
    the next '## '-prefixed heading, with a blank line + table + blank line +
    '---' + blank line (the wrapper style both catalog sections already use).
    Leaves everything before/after that span untouched.
    """
    start_idx = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and heading_keyword in line:
            start_idx = i
            break
    if start_idx is None:
        raise RuntimeError(f"Could not find a '## ' heading containing {heading_keyword!r} in README.md")

    end_idx = None
    for j in range(start_idx + 1, len(lines)):
        if lines[j].startswith("## "):
            end_idx = j
            break
    if end_idx is None:
        raise RuntimeError(f"Could not find the next '## ' heading after {heading_keyword!r} in README.md")

    heading_line = lines[start_idx]
    new_section = [heading_line, ""] + new_table_lines + ["", "---", ""]
    return lines[:start_idx] + new_section + lines[end_idx:]


def generate_readme(warnings):
    original = README_PATH.read_text(encoding="utf-8")
    lines = original.splitlines()

    skills_table, skill_count = build_skills_table(warnings)
    lines = replace_section(lines, "Skills Catalog", skills_table)

    rules_table, rule_count = build_rules_table(warnings)
    lines = replace_section(lines, "Rules Catalog", rules_table)

    new_content = "\n".join(lines) + "\n"
    return new_content, skill_count, rule_count


def main():
    check_only = "--check" in sys.argv[1:]
    warnings = []

    new_content, skill_count, rule_count = generate_readme(warnings)
    current_content = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""

    up_to_date = new_content == current_content

    if check_only:
        if up_to_date:
            print(f"✅ README catalog is up to date ({skill_count} skills, {rule_count} rules).")
        else:
            print(
                "❌ README catalog is out of date — run `python3 scripts/generate_catalog.py` "
                "and commit the result."
            )
    else:
        if up_to_date:
            print(f"README.md already up to date ({skill_count} skills, {rule_count} rules). No write needed.")
        else:
            README_PATH.write_text(new_content, encoding="utf-8")
            print(f"README.md regenerated ({skill_count} skills, {rule_count} rules).")

    print(f"\nSkills discovered: {skill_count}")
    print(f"Rules discovered:  {rule_count}")
    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("\nNo parsing warnings.")

    if check_only and not up_to_date:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
