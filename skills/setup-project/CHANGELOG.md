# Changelog

## 1.0.1 · 2026-10-12

- Command contract: `dev` is now `run` (starts the app in the background) plus `stop` and `logs`; Next.js `typecheck` runs `next typegen` first so CI has the route types.

## 1.0.0 (2026-10-10)

First release in this repo.

- One-time repo setup: detects the stack, asks at most 6 questions, writes AGENTS.md (project profile), the justfile command contract, stack rules from packs (nextjs, convex, vitest, ui-web, llm, pnpm-monorepo, godot starter), GitHub issue tracking (labels, ticket template, `task.sh`, `project-env.sh`) and a design contract skeleton.
