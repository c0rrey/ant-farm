#!/usr/bin/env bash
# rename-templates.sh — Rename 10 orchestration template files and update all
# codebase references.  Uses git mv for renames and sed for find/replace.
#
# Usage:
#   ./scripts/rename-templates.sh            # execute renames + reference updates
#   ./scripts/rename-templates.sh --dry-run   # show what would change, touch nothing

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES_DIR="$REPO_ROOT/orchestration/templates"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "=== DRY RUN — no changes will be made ==="
  echo
fi

# ---------------------------------------------------------------------------
# Rename pairs: OLD NEW  (all relative to orchestration/templates/)
# ---------------------------------------------------------------------------

RENAME_PAIRS=(
  "scout.md                    recon-planner.md"
  "pantry.md                   prompt-composer.md"
  "queen-state.md              orchestrator-state.md"
  "crumb-gatherer-skeleton.md  implementer-skeleton.md"
  "nitpicker-skeleton.md       reviewer-skeleton.md"
  "forager.md                  researcher.md"
  "forager-skeleton.md         researcher-skeleton.md"
  "surveyor.md                 spec-writer.md"
  "surveyor-skeleton.md        spec-writer-skeleton.md"
  "architect-skeleton.md       task-decomposer-skeleton.md"
)

# ---------------------------------------------------------------------------
# Find/replace pairs — ORDERED longest-first to prevent partial matches.
# Specifically, skeleton variants come before their base name.
# ---------------------------------------------------------------------------

REPLACE_PAIRS=(
  "crumb-gatherer-skeleton.md  implementer-skeleton.md"
  "surveyor-skeleton.md        spec-writer-skeleton.md"
  "forager-skeleton.md         researcher-skeleton.md"
  "nitpicker-skeleton.md       reviewer-skeleton.md"
  "architect-skeleton.md       task-decomposer-skeleton.md"
  "queen-state.md              orchestrator-state.md"
  "pantry.md                   prompt-composer.md"
  "scout.md                    recon-planner.md"
  "forager.md                  researcher.md"
  "surveyor.md                 spec-writer.md"
)

# ---------------------------------------------------------------------------
# Exclusion patterns for find/replace (not for git mv)
# ---------------------------------------------------------------------------

EXCLUDE_DIRS=(
  ".crumbs"
  "docs/scratch"
  "node_modules"
  ".git"
)

EXCLUDE_FILES=(
  "CHANGELOG.md"
  "scripts/build-review-prompts.sh"
  "scripts/rename-templates.sh"
  "scripts/setup.sh"
)

# ---------------------------------------------------------------------------
# Step 1: Rename files with git mv
# ---------------------------------------------------------------------------

echo "=== Step 1: Renaming template files ==="
echo

for pair in "${RENAME_PAIRS[@]}"; do
  old=$(echo "$pair" | awk '{print $1}')
  new=$(echo "$pair" | awk '{print $2}')
  src="$TEMPLATES_DIR/$old"
  dst="$TEMPLATES_DIR/$new"

  if [[ -f "$src" && -f "$dst" ]]; then
    # Both exist — keep the old (has latest edits), remove the stale new-name copy
    echo "  CONFLICT $old + $new both exist — removing stale $new, then git mv"
    if [[ "$DRY_RUN" == false ]]; then
      git -C "$REPO_ROOT" rm "$dst"
      git -C "$REPO_ROOT" mv "$src" "$dst"
    fi
  elif [[ -f "$src" ]]; then
    echo "  git mv $old -> $new"
    if [[ "$DRY_RUN" == false ]]; then
      git -C "$REPO_ROOT" mv "$src" "$dst"
    fi
  elif [[ -f "$dst" ]]; then
    echo "  SKIP $old (already renamed to $new)"
  else
    echo "  WARNING: $old not found and $new does not exist either"
  fi
done

echo
echo "=== Step 1 complete ==="
echo

# ---------------------------------------------------------------------------
# Step 2: Codebase-wide find/replace
# ---------------------------------------------------------------------------

echo "=== Step 2: Updating references across codebase ==="
echo

# Build the find command exclusions
FIND_EXCLUDES=()
for dir in "${EXCLUDE_DIRS[@]}"; do
  FIND_EXCLUDES+=( -not -path "$REPO_ROOT/$dir/*" )
done

# Collect all text files that could contain references, respecting exclusions.
# We search for files that match at least one of our old names.
for pair in "${REPLACE_PAIRS[@]}"; do
  old=$(echo "$pair" | awk '{print $1}')
  new=$(echo "$pair" | awk '{print $2}')

  echo "  Replacing '$old' -> '$new'"

  # Find files containing the old name, excluding specified dirs and files.
  # Use grep -rl for discovery, then sed for replacement.
  matching_files=()

  while IFS= read -r file; do
    # Check if this file is in the exclude list (relative to repo root)
    rel_path="${file#"$REPO_ROOT"/}"
    skip=false
    for excl in "${EXCLUDE_FILES[@]}"; do
      if [[ "$rel_path" == "$excl" ]]; then
        skip=true
        break
      fi
    done
    for excl_dir in "${EXCLUDE_DIRS[@]}"; do
      if [[ "$rel_path" == "$excl_dir"/* ]]; then
        skip=true
        break
      fi
    done
    if [[ "$skip" == true ]]; then
      continue
    fi
    matching_files+=("$file")
  done < <(grep -rl --include='*.md' --include='*.sh' --include='*.py' \
               --include='*.json' --include='*.yaml' --include='*.yml' \
               --include='*.toml' --include='*.txt' --include='*.js' \
               --include='*.ts' \
               "$old" "$REPO_ROOT" 2>/dev/null || true)

  if [[ ${#matching_files[@]} -eq 0 ]]; then
    echo "    (no files contain '$old')"
  else
    for file in "${matching_files[@]}"; do
      rel="${file#"$REPO_ROOT"/}"
      echo "    $rel"
      if [[ "$DRY_RUN" == false ]]; then
        sed -i '' "s|$old|$new|g" "$file"
      fi
    done
  fi

  echo
done

echo "=== Step 2 complete ==="
echo

# ---------------------------------------------------------------------------
# Step 3: Run structural tests
# ---------------------------------------------------------------------------

if [[ "$DRY_RUN" == false ]]; then
  echo "=== Step 3: Running structural tests ==="
  echo
  cd "$REPO_ROOT"
  pytest tests/test_orchestration.py -v
  echo
  echo "=== All done ==="
else
  echo "=== Dry run complete — no changes were made ==="
  echo "  Run without --dry-run to execute."
fi
