#!/usr/bin/env bash
# ==============================================================================
# Installation / Sync Script for skills-rules-repo
# ==============================================================================
# Usage:
#   ./scripts/install.sh --workspace /path/to/project   (installs into .agents/)
#   ./scripts/install.sh --global                      (installs into ~/.gemini/config/)
#   ./scripts/install.sh --list                        (lists available skills/rules)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

print_help() {
  cat <<EOF
skills-rules-repo Manager & Installer

Usage:
  ./scripts/install.sh [OPTIONS]

Options:
  -l, --list                  List all available skills, rules, and plugins in the repo
  -w, --workspace <PATH>      Install / link into project workspace (<PATH>/.agents)
  -g, --global                Install / link into user global config (~/.gemini/config)
  -s, --skill <NAME>          Install specific skill only (default: all)
  -r, --rule <NAME>           Install specific rule only (default: all)
  --copy                      Copy files instead of creating symbolic links
  -h, --help                  Show this help message

Examples:
  # Link all skills and rules to your active project
  ./scripts/install.sh --workspace .

  # Link only 'code-review' skill globally
  ./scripts/install.sh --global --skill code-review
EOF
}

MODE_LINK=1
TARGET_DIR=""
SELECTED_SKILL=""
SELECTED_RULE=""

list_items() {
  echo "=================================================="
  echo "📦 Available Skills in skills-rules-repo"
  echo "=================================================="
  if [ -d "${REPO_ROOT}/skills" ]; then
    for skill_dir in "${REPO_ROOT}/skills"/*; do
      if [ -d "$skill_dir" ]; then
        skill_name="$(basename "$skill_dir")"
        desc=""
        if [ -f "$skill_dir/SKILL.md" ]; then
          desc=$(grep -E "^description:" "$skill_dir/SKILL.md" | head -n 1 | sed -E 's/^description:[[:space:]]*>-?//' | sed 's/^[[:space:]]*//')
        fi
        echo "  • ${skill_name} : ${desc}"
      fi
    done
  fi

  echo ""
  echo "=================================================="
  echo "📋 Available Rules in skills-rules-repo"
  echo "=================================================="
  if [ -d "${REPO_ROOT}/rules" ]; then
    for rule_file in "${REPO_ROOT}/rules"/*.md; do
      if [ -f "$rule_file" ]; then
        rule_name="$(basename "$rule_file")"
        title=$(head -n 5 "$rule_file" | grep -E '^# ' | head -n 1 | sed 's/^# //')
        echo "  • ${rule_name} : ${title}"
      fi
    done
  fi

  echo ""
  echo "=================================================="
  echo "🧩 Available Plugins in skills-rules-repo"
  echo "=================================================="
  if [ -d "${REPO_ROOT}/plugins" ]; then
    for plugin_dir in "${REPO_ROOT}/plugins"/*; do
      if [ -d "$plugin_dir" ]; then
        plugin_name="$(basename "$plugin_dir")"
        echo "  • ${plugin_name}"
      fi
    done
  fi
  echo "=================================================="
}

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      print_help
      exit 0
      ;;
    -l|--list)
      list_items
      exit 0
      ;;
    -w|--workspace)
      TARGET_PATH="$2"
      TARGET_DIR="${TARGET_PATH}/.agents"
      shift 2
      ;;
    -g|--global)
      TARGET_DIR="${HOME}/.gemini/config"
      shift
      ;;
    -s|--skill)
      SELECTED_SKILL="$2"
      shift 2
      ;;
    -r|--rule)
      SELECTED_RULE="$2"
      shift 2
      ;;
    --copy)
      MODE_LINK=0
      shift
      ;;
    *)
      echo "Unknown option: $1"
      print_help
      exit 1
      ;;
  esac
done

if [ -z "$TARGET_DIR" ]; then
  echo "Error: Must specify either --workspace <PATH> or --global."
  print_help
  exit 1
fi

echo "🚀 Installing customizations into: ${TARGET_DIR}"
mkdir -p "${TARGET_DIR}/skills"
mkdir -p "${TARGET_DIR}/rules"

# Install Skills
if [ -n "$SELECTED_SKILL" ]; then
  SRC="${REPO_ROOT}/skills/${SELECTED_SKILL}"
  DEST="${TARGET_DIR}/skills/${SELECTED_SKILL}"
  if [ ! -d "$SRC" ]; then
    echo "Error: Skill '${SELECTED_SKILL}' not found at ${SRC}."
    exit 1
  fi
  if [ "$MODE_LINK" -eq 1 ]; then
    ln -sfn "$SRC" "$DEST"
    echo "  ✓ Linked skill: ${SELECTED_SKILL} -> ${DEST}"
  else
    rm -rf "$DEST"
    cp -R "$SRC" "$DEST"
    echo "  ✓ Copied skill: ${SELECTED_SKILL} -> ${DEST}"
  fi
else
  for skill_dir in "${REPO_ROOT}/skills"/*; do
    if [ -d "$skill_dir" ]; then
      skill_name="$(basename "$skill_dir")"
      DEST="${TARGET_DIR}/skills/${skill_name}"
      if [ "$MODE_LINK" -eq 1 ]; then
        ln -sfn "$skill_dir" "$DEST"
        echo "  ✓ Linked skill: ${skill_name}"
      else
        rm -rf "$DEST"
        cp -R "$skill_dir" "$DEST"
        echo "  ✓ Copied skill: ${skill_name}"
      fi
    fi
  done
fi

# Install Rules
if [ -n "$SELECTED_RULE" ]; then
  SRC="${REPO_ROOT}/rules/${SELECTED_RULE}"
  [[ "$SRC" != *.md ]] && SRC="${SRC}.md"
  rule_file="$(basename "$SRC")"
  DEST="${TARGET_DIR}/rules/${rule_file}"
  if [ ! -f "$SRC" ]; then
    echo "Error: Rule '${SELECTED_RULE}' not found at ${SRC}."
    exit 1
  fi
  if [ "$MODE_LINK" -eq 1 ]; then
    ln -sf "$SRC" "$DEST"
    echo "  ✓ Linked rule: ${rule_file} -> ${DEST}"
  else
    cp "$SRC" "$DEST"
    echo "  ✓ Copied rule: ${rule_file} -> ${DEST}"
  fi
else
  for rule_file in "${REPO_ROOT}/rules"/*.md; do
    if [ -f "$rule_file" ]; then
      rule_name="$(basename "$rule_file")"
      DEST="${TARGET_DIR}/rules/${rule_name}"
      if [ "$MODE_LINK" -eq 1 ]; then
        ln -sf "$rule_file" "$DEST"
        echo "  ✓ Linked rule: ${rule_name}"
      else
        cp "$rule_file" "$DEST"
        echo "  ✓ Copied rule: ${rule_name}"
      fi
    fi
  done
fi

echo ""
echo "✅ Customization installation complete!"
