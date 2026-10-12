---
name: implement
description: Implement the in-progress ticket test-first, run the project's checks and a two-axis code review, write the Outcome, open the PR and move the ticket to review. Part of the dev-flow lifecycle (take, implement, address, done).
license: MIT
disable-model-invocation: true
argument-hint: "[#issue]"
---

# /implement [#N]

Project facts (commands, tracker, git tool, base branch, models) live in `AGENTS.md`. Read it first.

1. **Load.** The named issue, else the one labelled `status:in-progress`: `gh issue view <n> --json title,body`. No `## Decisions` section → stop and say `/take` must run first. If the issue is not labelled `status:in-progress`, run `just task <n> in-progress` first.
2. **Scope.** Read only the files under `## Files`. Needs more than ~5 files → propose a split and stop.
3. **Build** with the `tdd` skill: red → green with `just test-q` only; the repo is green after every step. If the ticket touches screens, components or styles, also follow `ui-from-reference`.
4. **Gates.** `just check` passes. Then `code-review` with fixed point = the base branch and spec = this issue. Fix the real findings; list the rest in the Outcome.
5. **Outcome.** Add `## Outcome` to the issue body: what changed, why, one risk, how to verify. Temp file + `gh issue edit <n> --body-file <tmp>`.
6. **Ship.**
   - Graphite: `gt create -am "<type(scope): subject>"`, then `gt submit --no-edit` (if rejected, `--no-interactive`).
   - Plain git: `git switch -c <n>-<slug>` before step 3; now `git add -A`, `git commit -m "<type(scope): subject>"`, `git push -u origin HEAD`, `gh pr create --fill`.
   - PR body in the `pr` skill's format, written to a temp file, ending with `Closes #<n>`: `gh pr edit <pr> --body-file <tmp>`.
7. **Hand over.** `just task <n> in-review`. Report the PR link and the Outcome. No pasted diffs.

## Rules

- Never commit to the base branch. Never `reset`, `rebase`, force-push or merge; the human merges.
- Never edit files listed in another `status:in-progress` or `status:in-review` issue.
- Never bundle a refactor with a feature. Never add a dependency without one sentence of why.
- Never read or print `.env*` files.
- Two failed attempts at the same problem: stop, add a dated lesson to `docs/DECISIONS.md`, ask.

Shortest complete answer. End with one line: `Next: /address on <model> (after review comments) or /done (after merge).`
