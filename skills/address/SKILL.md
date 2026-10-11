---
name: address
description: Fix the review comments on the in-review ticket's PR on the same branch, re-run the checks and update the PR. Part of the dev-flow lifecycle (take, implement, address, done).
license: MIT
disable-model-invocation: true
argument-hint: "[#pr]"
---

# /address [#PR]

Project facts live in `AGENTS.md`. Read it first.

1. **Load.** The named PR, else the PR of the first `status:in-review` issue: `gh pr view <pr> --comments`.
2. **Branch.** `gh pr view <pr> --json headRefName -q .headRefName`, then `gt checkout <branch>` or `git switch <branch>`.
3. **Fix** each comment. A behavior change starts with a failing test (`tdd`). Then `just test-q` and `just typecheck`.
4. **Update.** Graphite: `gt modify -a`, then `gt submit --no-edit`. Plain git: `git add -A`, `git commit -m "<type(scope): subject>"`, `git push`.
5. **Report** one line per comment: what changed, or why not.

Shortest complete answer. End with one line: `Next: /done after you merge.`
