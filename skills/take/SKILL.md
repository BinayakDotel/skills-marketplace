---
name: take
description: Take the next (or named) ticket from the issue tracker, move it to in progress, grill only its open decisions (max 8 questions), and write Decisions and Files into the ticket. No code. Part of the dev-flow lifecycle (take, implement, address, done).
license: MIT
disable-model-invocation: true
argument-hint: "[#issue]"
---

# /take [#N]

Project facts (commands, tracker, git tool, base branch, models) live in `AGENTS.md`. Read it first. Read nothing else project-wide.

1. **Sync.** Graphite: `gt sync -f`. Plain git: `git switch <base> && git pull --ff-only`.
2. **Pick.** The named issue; otherwise the first open issue in the earliest open milestone with label `status:todo` whose `Depends:` issues are all closed:
   - `gh issue list --label status:todo --milestone "<milestone>" --json number,title --limit 10`
   - `gh issue view <n> --json title,body,milestone`
   - for each `Depends: #x`: `gh issue view <x> --json state -q .state`
3. **Claim (do this before anything else).** Run `just task <n> in-progress` and show its output line (`#<n> -> in-progress`). If it fails, stop and report the error. Then check out the base: `gt checkout <base>` or `git switch <base>`.
4. **Read.** The files under `## Files`, nothing more. For gaps, search the code, then open extra files one at a time.
5. **Grill.** Use the `grilling` skill on the decisions the ticket leaves open: at most 8 questions, one batch, each with your recommendation. Look up facts yourself; ask only for decisions.
6. **Write.** Add `## Decisions` and append any new paths to `## Files`. Write the whole body to a temp file, then `gh issue edit <n> --body-file <tmp>`.
   If the work needs more than ~5 files, propose a split in the `tickets` format and stop.
7. **Stop.** Do not build.

Shortest complete answer. End with one line: `Next: /implement on <model for implement in AGENTS.md>.`
