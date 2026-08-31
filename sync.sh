#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Skills & Rules Repo — Cross-Tool Sync Utility

Usage:
  ./sync.sh --global               Sync skills to global agent directories (~/.claude, ~/.Codex, ~/.gemini)
  ./sync.sh --project <dir>        Sync skills and rules into a target project repository
  ./sync.sh --help                 Show this help message

Examples:
  ./sync.sh --global
  ./sync.sh --project /Users/harishabib/code/github/my-new-app
EOF
  exit 0
}

if [ $# -eq 0 ]; then
  usage
fi

sync_global() {
  echo "🚀 Syncing skills globally..."

  # Claude Code
  mkdir -p "$HOME/.claude/skills"
  for skill_dir in "$REPO_DIR"/*/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
      skill_name="$(basename "$skill_dir")"
      mkdir -p "$HOME/.claude/skills/$skill_name"
      cp -f "$skill_dir/SKILL.md" "$HOME/.claude/skills/$skill_name/SKILL.md"
    fi
  done
  echo "✅ Synced to ~/.claude/skills"

  # Codex
  mkdir -p "$HOME/.Codex/skills"
  for skill_dir in "$REPO_DIR"/*/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
      skill_name="$(basename "$skill_dir")"
      mkdir -p "$HOME/.Codex/skills/$skill_name"
      cp -f "$skill_dir/SKILL.md" "$HOME/.Codex/skills/$skill_name/SKILL.md"
    fi
  done
  echo "✅ Synced to ~/.Codex/skills"

  # Gemini / Antigravity Global Config
  mkdir -p "$HOME/.gemini/config/skills"
  for skill_dir in "$REPO_DIR"/*/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
      skill_name="$(basename "$skill_dir")"
      mkdir -p "$HOME/.gemini/config/skills/$skill_name"
      cp -f "$skill_dir/SKILL.md" "$HOME/.gemini/config/skills/$skill_name/SKILL.md"
    fi
  done
  echo "✅ Synced to ~/.gemini/config/skills"
  echo "✨ Global sync complete!"
}

sync_project() {
  TARGET_PROJECT="$1"
  if [ ! -d "$TARGET_PROJECT" ]; then
    echo "❌ Error: Project directory '$TARGET_PROJECT' does not exist."
    exit 0
  fi

  echo "🚀 Syncing skills & rules to project: $TARGET_PROJECT..."

  # .agents/skills (Antigravity & Codex)
  mkdir -p "$TARGET_PROJECT/.agents/skills"
  for skill_dir in "$REPO_DIR"/*/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
      skill_name="$(basename "$skill_dir")"
      mkdir -p "$TARGET_PROJECT/.agents/skills/$skill_name"
      cp -f "$skill_dir/SKILL.md" "$TARGET_PROJECT/.agents/skills/$skill_name/SKILL.md"
    fi
  done

  # .claude/skills (Claude Code)
  mkdir -p "$TARGET_PROJECT/.claude/skills"
  for skill_dir in "$REPO_DIR"/*/*; do
    if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
      skill_name="$(basename "$skill_dir")"
      mkdir -p "$TARGET_PROJECT/.claude/skills/$skill_name"
      cp -f "$skill_dir/SKILL.md" "$TARGET_PROJECT/.claude/skills/$skill_name/SKILL.md"
    fi
  done

  # .cursor/rules (Cursor)
  mkdir -p "$TARGET_PROJECT/.cursor/rules"
  cp -rf "$REPO_DIR/cursor-rules/"*.mdc "$TARGET_PROJECT/.cursor/rules/"

  echo "✅ Synced .agents/skills, .claude/skills, and .cursor/rules into $TARGET_PROJECT"
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
  *)
    usage
    ;;
esac
