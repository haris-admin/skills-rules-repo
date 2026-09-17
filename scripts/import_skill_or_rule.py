#!/usr/bin/env python3
"""
Import & Intake Helper for skills-rules-repo

Automates auditing, formatting, and copying skills or rules from external
repositories into skills-rules-repo, followed by validation and catalog regeneration.

Usage:
  # Ingest a skill folder from another repository
  python3 scripts/import_skill_or_rule.py --source /path/to/my-skill --type skill --category core-methodology

  # Ingest a rule markdown file (automatically strips frontmatter if present)
  python3 scripts/import_skill_or_rule.py --source /path/to/my-rule.md --type rule

  # Dry run
  python3 scripts/import_skill_or_rule.py --source /path/to/my-rule.md --type rule --dry-run
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def sanitize_rule_content(raw_content: str, filename: str) -> str:
    """Ensure rule starts with H1 title and summary, stripping any YAML frontmatter."""
    content = raw_content.strip()
    
    # Check if file has YAML frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            
            # Extract description or title from frontmatter if helpful
            fm_desc = ""
            for line in fm_text.splitlines():
                if line.startswith("description:"):
                    fm_desc = line.split(":", 1)[1].strip().strip('"').strip("'")
            
            # If body already starts with # H1, keep body and ensure summary
            if body.startswith("# "):
                first_lines = body.splitlines()
                title_line = first_lines[0]
                rest = "\n".join(first_lines[1:]).strip()
                
                # Check if there is an immediate summary paragraph
                if fm_desc and (not rest or rest.startswith("#")):
                    content = f"{title_line}\n\n{fm_desc}\n\n{rest}"
                else:
                    content = body
            else:
                default_title = filename.replace("-", " ").title()
                if fm_desc:
                    content = f"# {default_title}\n\n{fm_desc}\n\n{body}"
                else:
                    content = f"# {default_title}\n\n{body}"

    # Ensure starts with # 
    if not content.startswith("# "):
        default_title = filename.replace("-", " ").title()
        content = f"# {default_title}\n\n{content}"

    return content


def import_rule(source_path: Path, dry_run: bool = False):
    if not source_path.is_file():
        print(f"❌ Error: Source file '{source_path}' does not exist.")
        sys.exit(1)

    stem = source_path.stem.lower()
    if not re.match(r"^[a-z0-9-]+$", stem):
        print(f"❌ Error: Rule filename '{source_path.name}' must be lowercase and hyphenated.")
        sys.exit(1)

    dest_file = ROOT_DIR / "rules" / f"{stem}.md"
    print(f"📥 Processing rule: {source_path.name} -> rules/{dest_file.name}")

    content = source_path.read_text(encoding="utf-8")
    sanitized = sanitize_rule_content(content, stem)

    if dry_run:
        print("🔍 [DRY RUN] Would write sanitized rule to:", dest_file)
        print("--- Preview First 15 Lines ---")
        print("\n".join(sanitized.splitlines()[:15]))
        return

    dest_file.write_text(sanitized, encoding="utf-8")
    print(f"✅ Wrote rule to {dest_file.relative_to(ROOT_DIR)}")


def import_skill(source_path: Path, category: str = "skills", dry_run: bool = False):
    if not source_path.is_dir():
        print(f"❌ Error: Source directory '{source_path}' does not exist.")
        sys.exit(1)

    skill_md = source_path / "SKILL.md"
    if not skill_md.is_file():
        print(f"❌ Error: Missing SKILL.md in '{source_path}'.")
        sys.exit(1)

    skill_name = source_path.name.lower()
    if not re.match(r"^[a-z0-9-]+$", skill_name):
        print(f"❌ Error: Skill directory '{skill_name}' must be lowercase and hyphenated.")
        sys.exit(1)

    target_dir = ROOT_DIR / category / skill_name
    print(f"📥 Processing skill: {skill_name} -> {target_dir.relative_to(ROOT_DIR)}")

    if dry_run:
        print(f"🔍 [DRY RUN] Would copy {source_path} to {target_dir}")
        return

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    if target_dir.exists():
        shutil.rmtree(target_dir)

    shutil.copytree(source_path, target_dir)
    print(f"✅ Copied skill to {target_dir.relative_to(ROOT_DIR)}")


def run_validations():
    print("\n🔍 Running test validation...")
    res = subprocess.run([sys.executable, str(ROOT_DIR / "scripts" / "validate.py")])
    if res.returncode != 0:
        print("❌ Validation failed!")
        sys.exit(1)

    print("\n📚 Regenerating README catalog...")
    res = subprocess.run([sys.executable, str(ROOT_DIR / "scripts" / "generate_catalog.py")])
    if res.returncode != 0:
        print("❌ Catalog regeneration failed!")
        sys.exit(1)

    print("\n🔒 Verifying catalog check...")
    res = subprocess.run([sys.executable, str(ROOT_DIR / "scripts" / "generate_catalog.py"), "--check"])
    if res.returncode != 0:
        print("❌ Catalog check failed!")
        sys.exit(1)

    print("\n✨ Intake complete and verified!")


def main():
    parser = argparse.ArgumentParser(description="Import skills or rules from external repositories.")
    parser.add_argument("--source", required=True, type=Path, help="Path to source skill directory or rule file.")
    parser.add_argument("--type", required=True, choices=["skill", "rule"], help="Asset type (skill or rule).")
    parser.add_argument("--category", default="skills", help="Target category folder for skills (default: 'skills').")
    parser.add_argument("--dry-run", action="store_true", help="Inspect actions without copying.")

    args = parser.parse_args()

    if args.type == "rule":
        import_rule(args.source, dry_run=args.dry_run)
    elif args.type == "skill":
        import_skill(args.source, category=args.category, dry_run=args.dry_run)

    if not args.dry_run:
        run_validations()


if __name__ == "__main__":
    main()
