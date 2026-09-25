#!/usr/bin/env bash
# Sync one skill from this repo (the source of truth) to where it is used on this machine.
#   ./scripts/sync-skill.sh <name>          validate, symlink ~/.claude/skills/<name> -> repo, build dist/<name>.zip
#   ./scripts/sync-skill.sh <name> --copy   copy into ~/.claude/skills instead of symlinking
#   ./scripts/sync-skill.sh --all           every skill in skills/
# claude.ai has no upload API: when the zip changes, re-upload it at Settings > Capabilities > Skills.
# Git is left to you: this script never commits or pushes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

usage() { sed -n '2,5p' "$0" | sed 's/^# //'; exit 1; }
[ $# -ge 1 ] || usage

MODE=link; NAMES=()
for arg in "$@"; do
  case "$arg" in
    --copy) MODE=copy ;;
    --all)  for d in "$ROOT"/skills/*/; do NAMES+=("$(basename "$d")"); done ;;
    -h|--help) usage ;;
    -*) echo "unknown option: $arg"; usage ;;
    *) NAMES+=("$arg") ;;
  esac
done
[ ${#NAMES[@]} -ge 1 ] || usage

echo "validate"
python3 "$ROOT/scripts/validate.py" "${NAMES[@]}" | sed 's/^/  /'

mkdir -p "$HOME/.claude/skills" "$ROOT/dist"
for NAME in "${NAMES[@]}"; do
  SRC="$ROOT/skills/$NAME"
  DEST="$HOME/.claude/skills/$NAME"
  ZIP="$ROOT/dist/$NAME.zip"
  STAMP="$ROOT/dist/.$NAME.sha"
  echo "$NAME"

  # Claude Code personal skill
  if [ "$MODE" = link ]; then
    if [ -L "$DEST" ] && [ "$(readlink "$DEST")" = "$SRC" ]; then
      echo "  ~/.claude/skills/$NAME already links here"
    else
      rm -rf "$DEST"; ln -s "$SRC" "$DEST"; echo "  linked ~/.claude/skills/$NAME -> skills/$NAME"
    fi
  else
    rm -rf "$DEST"; cp -R "$SRC" "$DEST"
    find "$DEST" \( -name __pycache__ -o -name .DS_Store \) -prune -exec rm -rf {} + 2>/dev/null || true
    echo "  copied to ~/.claude/skills/$NAME"
  fi

  # zip for claude.ai (folder at the zip root, as the uploader expects)
  ( cd "$ROOT/skills" && rm -f "$ZIP" && zip -qrX "$ZIP" "$NAME" -x "*/__pycache__/*" "*.pyc" "*/.DS_Store" )
  NEW=$(cd "$ROOT/skills" && find "$NAME" -type f ! -path "*/__pycache__/*" ! -name .DS_Store ! -name "*.pyc" -print0 \
        | sort -z | xargs -0 shasum | shasum | cut -c1-12)
  OLD=$(cat "$STAMP" 2>/dev/null || echo none)
  echo "$NEW" > "$STAMP"
  if [ "$OLD" = "$NEW" ]; then
    echo "  dist/$NAME.zip rebuilt (unchanged since last sync)"
  else
    echo "  dist/$NAME.zip CHANGED: re-upload at claude.ai > Settings > Capabilities > Skills (remove the old $NAME first)"
  fi
done

git -C "$ROOT" status --short -- skills 2>/dev/null | sed 's/^/  git: /' || true
