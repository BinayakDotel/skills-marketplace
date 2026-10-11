#!/usr/bin/env bash
# Move a ticket: scripts/task.sh <issue> <todo|in-progress|in-review|done>
# Sets the status label and the board's Status field in one call.
# Needs gh with the "project" scope (gh auth refresh -s project) and .github/project.env
# (written once by scripts/project-env.sh).
set -euo pipefail
n="$1"; s="$2"
# shellcheck disable=SC1091
source "$(dirname "$0")/../.github/project.env"

case "$s" in
  todo)        label="status:todo";        opt="$OPT_TODO" ;;
  in-progress) label="status:in-progress"; opt="$OPT_IN_PROGRESS" ;;
  in-review)   label="status:in-review";   opt="$OPT_IN_REVIEW" ;;
  done)        label="";                   opt="$OPT_DONE" ;;
  *) echo "status must be todo, in-progress, in-review or done" >&2; exit 2 ;;
esac

for old in status:todo status:in-progress status:in-review; do
  [ "$old" = "$label" ] || gh issue edit "$n" --remove-label "$old" >/dev/null 2>&1 || true
done
[ -z "$label" ] || gh issue edit "$n" --add-label "$label" >/dev/null

item=$(gh project item-list "$PROJECT_NUMBER" --owner "$PROJECT_OWNER" --limit 500 --format json \
  --jq ".items[] | select(.content.number == $n) | .id")
if [ -z "$item" ]; then
  url=$(gh issue view "$n" --json url -q .url)
  item=$(gh project item-add "$PROJECT_NUMBER" --owner "$PROJECT_OWNER" --url "$url" --format json --jq .id)
fi
gh project item-edit --id "$item" --project-id "$PROJECT_ID" \
  --field-id "$STATUS_FIELD_ID" --single-select-option-id "$opt" >/dev/null
echo "#$n -> $s"
