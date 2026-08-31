# Codebase Inspection with pygount

Analyze repositories for lines of code, language breakdown, file counts, and code-vs-comment ratios.

## When to Use
- User asks for LOC (lines of code) count
- User wants a language breakdown of a repo
- User asks about codebase size or composition

## Prerequisites
```
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

## Basic Summary (Most Common)
```
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**IMPORTANT:** Always use `--folders-to-skip` to exclude dependency/build directories, otherwise pygount will hang.

## Common Folder Exclusions
```
# Python projects
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# General
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## Filter by Language
```
# Only count Python
pygount --suffix=py --format=summary .

# Only count Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## Output Formats
```
# Summary table (recommended)
pygount --format=summary .

# JSON for programmatic use
pygount --format=json .
```

## Interpreting Results
The summary table columns: **Language**, **Files**, **Code**, **Comment**, **%**.

Special pseudo-languages: `__empty__` (empty files), `__binary__` (images, compiled), `__generated__` (auto-generated), `__duplicate__` (identical content), `__unknown__` (unrecognized types).

## Pitfalls
1. Always exclude .git, node_modules, venv -- without `--folders-to-skip`, pygount will crawl everything and may take minutes.
2. Markdown shows 0 code lines -- pygount classifies all Markdown as comments.
3. JSON files show low code counts -- use `wc -l` for accurate JSON line counts.
4. Large monorepos -- use `--suffix` to target specific languages rather than scanning everything.
