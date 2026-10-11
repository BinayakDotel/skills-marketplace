---
name: setup-project
description: One-time setup of a repo for the dev-flow skills. Detects the stack, then writes the project profile (AGENTS.md), the justfile command contract, stack rules from packs, GitHub issue tracking (labels, ticket template, board script) and, for web UI, a design contract skeleton. Never edits skills. Use when starting a new repo or bringing an existing one into dev-flow.
license: MIT
disable-model-invocation: true
---

# /setup-project

Skills stay global and unchanged. This skill writes the project's own facts once, from the templates and packs next to this file (`<skill-dir>` is the folder containing this SKILL.md).

## 1. Detect (read, don't ask)

Look only at: `package.json` and lockfiles, `pnpm-workspace.yaml`, `next.config.*`, any `convex/` folder, `vitest.config.*`, `project.godot`, `*.csproj`, `pyproject.toml`, `Cargo.toml`, `justfile`, `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, `docs/`, `git remote -v`. At most 15 reads; never `node_modules`. Match packs with `<skill-dir>/packs/INDEX.md`.

## 2. Ask once

One batch, at most 6 questions, each with your recommendation:

1. The project in one sentence.
2. Packs: confirm the detected list.
3. Git: Graphite or plain git, and the base branch.
4. Tracker: GitHub Issues with a project board (recommended) or local markdown; the board title.
5. Models for tickets/take, implement, address/done, and when stuck.
6. Web UI: write the design contract skeleton now? (Yes if the project has or will have screens.)

## 3. Write

Show the file list first, then write.

- **`AGENTS.md`** from `templates/AGENTS.md`, the block under 60 lines. If it exists, replace only the block between `<!-- dev-flow:start -->` and `<!-- dev-flow:end -->`, or append the block. Keep every other tool's managed block as it is (Next.js writes one between `BEGIN:nextjs-agent-rules` and `END:nextjs-agent-rules`). If only `CLAUDE.md` exists, add the line `See AGENTS.md.` to it.
- **`justfile`**: merge each pack's `justfile.snippet`, keeping existing recipes. Every contract recipe must exist: `test-q`, `typecheck`, `lint`, `check`, `dev`, `task`. A recipe with no tool for this stack becomes `@echo "n/a for this stack"`.
- **`.cursor/rules/<rule>.mdc`** from each chosen pack's `rules/`, with every `<<placeholder>>` filled from detection. Packs never add always-on rules.
- **GitHub** (if chosen): `docs/agents/issue-tracker.md` and `.github/ISSUE_TEMPLATE/ticket.md` from `templates/`; `scripts/task.sh` and `scripts/project-env.sh` from `templates/` (make them executable); labels: `gh label create status:todo --color ededed`, `gh label create status:in-progress --color fbca04`, `gh label create status:in-review --color 0e8a16` (ignore "already exists").
- **`docs/DECISIONS.md`** from `templates/DECISIONS.md` if missing.
- **Web UI** (if chosen): `docs/design/README.md` from `templates/design-contract.md`, `docs/design/screens.json` containing `[]`, `scripts/shots.ts` from `packs/ui-web/`, and `.shots/` in `.gitignore`. Then tell the human the references and tokens come from the `design-package` skill, run with a strong model (Claude), not from this setup.

## 4. Hand over

Print the steps only the human can do, then stop:

1. `gh auth refresh -s project`
2. `gh project create --owner <owner> --title "<board title>"`; in its settings add a Status option named `In Review`; then `scripts/project-env.sh <owner> <project number>`.
3. One milestone per phase: `gh api repos/<owner>/<repo>/milestones -f title="Phase 1"`.
4. `just check` once; fix the setup (not the code) until it runs.

End with one line: `Next: /tickets <spec section> on <model for tickets>.`
