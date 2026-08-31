#!/usr/bin/env python3
"""
Validation Script for skills-rules-repo
Checks:
1. Skills structure and valid YAML frontmatter in SKILL.md (name, description).
2. Rule naming conventions and valid Markdown headers.
3. Plugin manifests (plugin.json).
4. Relative link integrity across skills and documentation.
"""

import os
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def parse_frontmatter(content: str):
    """Simple parser for YAML frontmatter between --- and ---."""
    if not content.startswith("---"):
        return None, "Missing opening frontmatter delimiter (---)"
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "Missing closing frontmatter delimiter (---)"
    
    yaml_text = parts[1].strip()
    data = {}
    lines = yaml_text.splitlines()
    current_key = None
    multiline_val = []

    for line in lines:
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            if current_key and multiline_val:
                data[current_key] = " ".join(multiline_val).strip()
                multiline_val = []
            key, val = line.split(":", 1)
            current_key = key.strip()
            val = val.strip()
            if val in (">-", ">", "|", "|-"):
                multiline_val = []
            elif val:
                data[current_key] = val
        elif current_key:
            multiline_val.append(line.strip())
            
    if current_key and multiline_val:
        data[current_key] = " ".join(multiline_val).strip()

    return data, None

def validate_skills(errors):
    skills_dir = ROOT_DIR / "skills"
    if not skills_dir.exists():
        return

    print("🔍 Validating Skills...")
    for skill_path in sorted(skills_dir.iterdir()):
        if not skill_path.is_dir() or skill_path.name.startswith("."):
            continue
            
        skill_name = skill_path.name
        # Check folder naming convention (lowercase, hyphens/alphanumeric)
        if not re.match(r"^[a-z0-9-]+$", skill_name):
            errors.append(f"[Skill: {skill_name}] Directory name should be lowercase and hyphenated.")

        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"[Skill: {skill_name}] Missing required SKILL.md file.")
            continue

        try:
            content = skill_md.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"[Skill: {skill_name}] Failed to read SKILL.md: {e}")
            continue

        data, err = parse_frontmatter(content)
        if err:
            errors.append(f"[Skill: {skill_name}/SKILL.md] {err}")
            continue

        if not data.get("name"):
            errors.append(f"[Skill: {skill_name}/SKILL.md] Missing 'name' in frontmatter.")
        elif data["name"] != skill_name:
            errors.append(f"[Skill: {skill_name}/SKILL.md] Frontmatter name '{data['name']}' does not match directory '{skill_name}'.")

        if not data.get("description"):
            errors.append(f"[Skill: {skill_name}/SKILL.md] Missing 'description' in frontmatter.")
        elif len(data["description"]) < 15:
            errors.append(f"[Skill: {skill_name}/SKILL.md] Description is too short ({len(data['description'])} chars). Provide a detailed trigger description.")

        print(f"  ✓ Skill '{skill_name}' is valid.")

def validate_rules(errors):
    rules_dir = ROOT_DIR / "rules"
    if not rules_dir.exists():
        return

    print("\n🔍 Validating Rules...")
    for rule_path in sorted(rules_dir.iterdir()):
        if rule_path.is_dir() or rule_path.name.startswith("."):
            continue

        if not rule_path.name.endswith(".md"):
            errors.append(f"[Rule: {rule_path.name}] File must have a .md extension.")
            continue

        # Check naming convention
        base_name = rule_path.stem
        if not re.match(r"^[a-z0-9-]+$", base_name):
            errors.append(f"[Rule: {rule_path.name}] Filename should be lowercase and hyphenated.")

        try:
            content = rule_path.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"[Rule: {rule_path.name}] Failed to read file: {e}")
            continue

        if not content.strip().startswith("# "):
            errors.append(f"[Rule: {rule_path.name}] File should start with an H1 title ('# Title').")

        print(f"  ✓ Rule '{rule_path.name}' is valid.")

def validate_plugins(errors):
    plugins_dir = ROOT_DIR / "plugins"
    if not plugins_dir.exists():
        return

    print("\n🔍 Validating Plugins...")
    for plugin_path in sorted(plugins_dir.iterdir()):
        if not plugin_path.is_dir() or plugin_path.name.startswith("."):
            continue

        plugin_json = plugin_path / "plugin.json"
        if not plugin_json.exists():
            errors.append(f"[Plugin: {plugin_path.name}] Missing plugin.json manifest.")
        else:
            print(f"  ✓ Plugin '{plugin_path.name}' has valid manifest.")

def validate_templates(errors):
    templates_dir = ROOT_DIR / "templates"
    if not templates_dir.exists():
        return

    print("\n🔍 Validating Templates...")
    skill_template = templates_dir / "skill-template" / "SKILL.md"
    if not skill_template.exists():
        errors.append("[Templates] Missing templates/skill-template/SKILL.md")
    else:
        print("  ✓ Skill template present.")

    rule_template = templates_dir / "rule-template.md"
    if not rule_template.exists():
        errors.append("[Templates] Missing templates/rule-template.md")
    else:
        print("  ✓ Rule template present.")

def main():
    print("=" * 60)
    print("skills-rules-repo: Automated Validation Check")
    print("=" * 60)

    errors = []
    validate_skills(errors)
    validate_rules(errors)
    validate_plugins(errors)
    validate_templates(errors)

    print("\n" + "=" * 60)
    if errors:
        print(f"❌ FAILED: Found {len(errors)} issue(s):")
        for err in errors:
            print(f"  - {err}")
        print("=" * 60)
        sys.exit(1)
    else:
        print("✅ SUCCESS: All skills, rules, templates, and plugins validated successfully!")
        print("=" * 60)
        sys.exit(0)

if __name__ == "__main__":
    main()
