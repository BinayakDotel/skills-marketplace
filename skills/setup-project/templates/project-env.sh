#!/usr/bin/env bash
# One-time: writes .github/project.env for scripts/task.sh.
# usage: scripts/project-env.sh <owner> <project-number>
# The board's Status field needs the options: Todo, In Progress, In Review, Done.
set -euo pipefail
owner="$1"; num="$2"
q() { gh project field-list "$num" --owner "$owner" --format json --jq "$1"; }
opt() { q ".fields[] | select(.name == \"Status\") | .options[] | select(.name == \"$1\") | .id"; }
pid=$(gh project view "$num" --owner "$owner" --format json --jq .id)
fid=$(q '.fields[] | select(.name == "Status") | .id')
mkdir -p .github
cat > .github/project.env <<EOF
PROJECT_OWNER=$owner
PROJECT_NUMBER=$num
PROJECT_ID=$pid
STATUS_FIELD_ID=$fid
OPT_TODO=$(opt "Todo")
OPT_IN_PROGRESS=$(opt "In Progress")
OPT_IN_REVIEW=$(opt "In Review")
OPT_DONE=$(opt "Done")
EOF
grep -q '=$' .github/project.env && { echo "missing a Status option; check the board settings" >&2; exit 1; }
echo "wrote .github/project.env"
