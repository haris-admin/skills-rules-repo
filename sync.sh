#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Skills & Rules Repo — Universal Cross-Tool Sync Utility

Supports:
  - Claude Code (~/.claude/skills, .claude/skills)
  - Codex (~/.Codex/skills, .agents/skills)
  - Cursor (.cursor/rules/*.mdc)
  - Antigravity IDE & Gemini (~/.gemini/config/skills, ~/.gemini/config/rules, .agents/rules)

Usage:
  ./sync.sh --global               Sync skills and rules to global user directories (~/.claude, ~/.Codex, ~/.gemini)
  ./sync.sh --project <dir>        Sync skills, rules, and Cursor .mdc files into a target project repository
  ./sync.sh --help                 Show this help message

Examples:
  ./sync.sh --global
  ./sync.sh --project /Users/harishabib/code/github/my-saas-app
EOF
  exit 0
}

if [ $# -eq 0 ]; then
  usage
fi

sync_global() {
  echo "🚀 Syncing skills and rules globally..."

  # 1. Claude Code
  mkdir -p "$HOME/.claude/skills"
  for skill_dir in "$REPO_DIR"/*/* "$REPO_DIR"/skills/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
      skill_name="$(basename "$skill_dir")"
      mkdir -p "$HOME/.claude/skills/$skill_name"
      cp -rf "$skill_dir"/* "$HOME/.claude/skills/$skill_name/"
    fi
  done
  echo "✅ Synced to ~/.claude/skills"

  # 2. Codex
  mkdir -p "$HOME/.Codex/skills"
  for skill_dir in "$REPO_DIR"/*/* "$REPO_DIR"/skills/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
      skill_name="$(basename "$skill_dir")"
      mkdir -p "$HOME/.Codex/skills/$skill_name"
      cp -rf "$skill_dir"/* "$HOME/.Codex/skills/$skill_name/"
    fi
  done
  echo "✅ Synced to ~/.Codex/skills"

  # 3. Gemini / Antigravity Global Config
  mkdir -p "$HOME/.gemini/config/skills" "$HOME/.gemini/config/rules"
  for skill_dir in "$REPO_DIR"/*/* "$REPO_DIR"/skills/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
      skill_name="$(basename "$skill_dir")"
      mkdir -p "$HOME/.gemini/config/skills/$skill_name"
      cp -rf "$skill_dir"/* "$HOME/.gemini/config/skills/$skill_name/"
    fi
  done
  if [ -d "$REPO_DIR/rules" ]; then
    cp -rf "$REPO_DIR/rules/"*.md "$HOME/.gemini/config/rules/" 2>/dev/null || true
  fi
  echo "✅ Synced to ~/.gemini/config/skills and ~/.gemini/config/rules"
  echo "✨ Global sync complete across Claude Code, Codex, Antigravity, and Gemini!"
}

sync_project() {
  TARGET_PROJECT="$1"
  if [ ! -d "$TARGET_PROJECT" ]; then
    echo "❌ Error: Project directory '$TARGET_PROJECT' does not exist."
    exit 1
  fi

  echo "🚀 Syncing skills & rules to project: $TARGET_PROJECT..."

  # .agents/skills (Antigravity & Codex)
  mkdir -p "$TARGET_PROJECT/.agents/skills" "$TARGET_PROJECT/.agents/rules"
  for skill_dir in "$REPO_DIR"/*/* "$REPO_DIR"/skills/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
      skill_name="$(basename "$skill_dir")"
      mkdir -p "$TARGET_PROJECT/.agents/skills/$skill_name"
      cp -rf "$skill_dir"/* "$TARGET_PROJECT/.agents/skills/$skill_name/"
    fi
  done

  # .agents/rules
  if [ -d "$REPO_DIR/rules" ]; then
    cp -rf "$REPO_DIR/rules/"*.md "$TARGET_PROJECT/.agents/rules/" 2>/dev/null || true
  fi

  # .claude/skills (Claude Code)
  mkdir -p "$TARGET_PROJECT/.claude/skills"
  for skill_dir in "$REPO_DIR"/*/* "$REPO_DIR"/skills/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
      skill_name="$(basename "$skill_dir")"
      mkdir -p "$TARGET_PROJECT/.claude/skills/$skill_name"
      cp -rf "$skill_dir"/* "$TARGET_PROJECT/.claude/skills/$skill_name/"
    fi
  done

  # .cursor/rules (Cursor)
  mkdir -p "$TARGET_PROJECT/.cursor/rules"
  if [ -d "$REPO_DIR/cursor-rules" ]; then
    cp -rf "$REPO_DIR/cursor-rules/"*.mdc "$TARGET_PROJECT/.cursor/rules/"
  fi

  echo "✅ Synced .agents/skills, .agents/rules, .claude/skills, and .cursor/rules into $TARGET_PROJECT"
  echo "✨ Project sync complete!"
}

case "$1" in
  --global)
    sync_global
    ;;
  --project)
    if [ -z "${2:-}" ]; then
      echo "❌ Error: Missing target directory argument for --project."
      usage
    fi
    sync_project "$2"
    ;;
  -h|--help)
    usage
    ;;
  *)
    usage
    ;;
esac
