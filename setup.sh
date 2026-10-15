#!/usr/bin/env bash
# setup.sh: install the claude-project-template into a project.
#
# Usage:
#   ./setup.sh [path]          install into path (default: current directory)
#   ./setup.sh --hub [path]    also install the repo-evaluation skill and
#                              ignore repos/ (for an evaluation workspace)
#
# Behavior:
#   - Non-clobbering: existing files are left untouched and reported SKIP.
#   - Idempotent: running it twice changes nothing.
#   - Creates CLAUDE.md containing "@AGENTS.md" (works on Windows, no symlink).
#   - Merges gitignore.additions into .gitignore (no duplicates).
#   - Never runs git; never writes outside the target directory.

set -euo pipefail

HUB=0
TARGET_ARG=""
for arg in "$@"; do
  case "$arg" in
    --hub) HUB=1 ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    -*) echo "error: unknown option $arg" >&2; exit 1 ;;
    *) TARGET_ARG="$arg" ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/template"
OPTIONAL_HUB="$SCRIPT_DIR/optional/hub"

[ -d "$TEMPLATE" ] || { echo "error: template/ not found next to setup.sh" >&2; exit 1; }

TARGET="${TARGET_ARG:-$PWD}"
[ -d "$TARGET" ] || { echo "error: $TARGET is not a directory" >&2; exit 1; }
TARGET="$(cd "$TARGET" && pwd)"

CREATED=0
SKIPPED=0
GITIGNORE_ADDED=0

copy_tree() {
  # copy every file under $1 into $2, skipping files that already exist
  local src="$1" dst="$2" rel
  while IFS= read -r rel; do
    if [ -e "$dst/$rel" ]; then
      SKIPPED=$((SKIPPED + 1)); echo "  SKIP  $rel (exists)"
    else
      mkdir -p "$(dirname "$dst/$rel")"
      cp "$src/$rel" "$dst/$rel"
      CREATED=$((CREATED + 1)); echo "  NEW   $rel"
    fi
  done < <(cd "$src" && find . -type f -not -name '.DS_Store' -not -name 'gitignore.additions' | sed 's|^\./||' | sort)
}

add_gitignore_line() {
  if grep -qxF "$1" "$GITIGNORE"; then :; else
    printf '%s\n' "$1" >> "$GITIGNORE"
    GITIGNORE_ADDED=$((GITIGNORE_ADDED + 1))
    echo "  NEW   .gitignore entry: $1"
  fi
}

echo "Installing claude-project-template into: $TARGET"
[ "$HUB" -eq 1 ] && echo "Mode: evaluation hub"
echo

# Decide "existing codebase?" BEFORE we add files, ignoring VCS and OS noise.
EXISTING=0
if [ -n "$(find "$TARGET" -mindepth 1 -maxdepth 1 \
      -not -name .git -not -name .gitignore -not -name .DS_Store \
      -not -name AGENTS.md -not -name CLAUDE.md -not -name PLAN.md \
      -not -name .claude -not -name docs -not -name README.md \
      -not -name LICENSE -not -name repos 2>/dev/null | head -n 1)" ]; then
  EXISTING=1
fi

# 1. Payload (gitignore.additions is merged in step 3, never copied)
copy_tree "$TEMPLATE" "$TARGET"

if [ "$HUB" -eq 1 ]; then
  copy_tree "$OPTIONAL_HUB" "$TARGET"
fi

# 2. CLAUDE.md imports AGENTS.md
echo
if [ -e "$TARGET/CLAUDE.md" ]; then
  if grep -qF '@AGENTS.md' "$TARGET/CLAUDE.md"; then
    echo "  OK    CLAUDE.md already imports AGENTS.md"
  else
    echo "  NOTE  CLAUDE.md exists and was NOT changed. Add this line to it:"
    echo "          @AGENTS.md"
  fi
else
  printf '@AGENTS.md\n' > "$TARGET/CLAUDE.md"
  CREATED=$((CREATED + 1))
  echo "  NEW   CLAUDE.md (contains: @AGENTS.md)"
fi

if [ -f "$TARGET/.claude/settings.json" ] && ! grep -q plan_guard "$TARGET/.claude/settings.json"; then
  echo "  NOTE  .claude/settings.json exists without the plan_guard hooks (not changed)."
  echo "        Merge the \"hooks\" block and the two Edit() deny rules from:"
  echo "        $TEMPLATE/.claude/settings.json"
  echo
fi

# 3. .gitignore merge
echo
GITIGNORE="$TARGET/.gitignore"
touch "$GITIGNORE"
while IFS= read -r line; do
  [ -z "$line" ] && continue
  case "$line" in \#*) continue ;; esac
  add_gitignore_line "$line"
done < "$TEMPLATE/gitignore.additions"
[ "$HUB" -eq 1 ] && add_gitignore_line "repos/"
[ "$GITIGNORE_ADDED" -eq 0 ] && echo "  OK    .gitignore already up to date"

# 4. Report + next steps
echo
echo "Done: $CREATED files created, $SKIPPED skipped, $GITIGNORE_ADDED gitignore entries added."
echo
echo "Next steps:"
N=1
step() { echo "  $N. $1"; N=$((N + 1)); }
step "Fill the TODOs in AGENTS.md (overview, Commands, style)."
if [ "$HUB" -eq 1 ]; then
  step "Put repos under repos/ (git clone --depth 1 <url> repos/<name>)"
  echo "     or start claude with --add-dir <path> for repos already on disk."
  step "Start claude and run: /repo-evaluation"
elif [ "$EXISTING" -eq 1 ]; then
  step "Existing codebase detected. First Claude session: run /onboard"
else
  step "Empty project. Fill PLAN.md milestones + T1 (with Done when), then say: resume"
fi
step "Run /agents once in Claude Code to confirm the subagents loaded."
step "Commit: AGENTS.md CLAUDE.md PLAN.md .claude/ docs/ .gitignore"
