---
name: stop-preview
description: Stop the local app started by /preview-pr without restarting the previous server or deleting its Convex deployment. Use when the user says /stop-preview.
license: MIT
disable-model-invocation: true
---

# /stop-preview

1. List the repo's worktrees and find the one with an ignored `.run/preview-pr` marker. If more than one is marked, ask which PR to stop. If none is marked, say no PR preview is recorded; do not stop an unrelated process.
2. Verify that this worktree still owns the running app using the repo's process record (in Kuhiro, `.run/pids`). If it does, run `just stop` from that worktree. The repo's stop recipe may kill any listener on its app port, so do not call it if an unrelated process now owns that port. If the recorded process is already gone, clear the stale marker and report that nothing was running.
3. Remove the marker after a successful stop. Report the PR number and worktree. Leave the worktree, its `.env.local`, and any selected Convex deployment intact; do not restart the server that ran before the preview.
