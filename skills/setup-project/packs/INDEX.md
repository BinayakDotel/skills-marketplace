# Packs

A pack adds rules (scoped by globs, never always-on) and justfile recipes for one stack. `/setup-project` picks packs by these hints and fills the `<<placeholders>>`.

Common placeholders: `<<pm>>` is the package manager (`npm`, `pnpm`, `bun`); `<<pmx>>` runs a local binary (`npx`, `pnpm exec`, `bunx`). When the app is at the repo root, `<<web_dir>>/` becomes empty (globs like `app/**`, not `./app/**`).

| Pack | Detect | Adds | Placeholders |
|---|---|---|---|
| `nextjs` | `next` in package.json, `next.config.*` | `rules/nextjs.mdc`; `dev`, `typecheck`, `lint` | `<<web_dir>>` (empty or `apps/web`), `<<core_dir>>`, `<<pm>>`, `<<pmx>>` |
| `convex` | `convex` in package.json, a `convex/` folder | `rules/convex.mdc` | `<<convex_dir>>` |
| `vitest` | `vitest` in package.json | `rules/testing.mdc`; `test-q` | `<<pmx>>`, `<<fixtures_dir>>` |
| `ui-web` | any web UI (with `nextjs`) | `rules/ui.mdc`, `shots.ts`; `shots`, `ref-css` | `<<web_dir>>`, `<<pmx>>` |
| `llm` | AI SDKs (`ai`, `@google/genai`, `openai`, `@anthropic-ai/sdk`) or a prompts folder | `rules/llm.mdc` | `<<llm_globs>>` |
| `pnpm-monorepo` | `pnpm-workspace.yaml` | `rules/monorepo.mdc` | `<<core_pkg>>` |
| `godot` | `project.godot` | `rules/godot.mdc`; `test-q`, `lint`, `typecheck`, `dev` (starter) | `<<theme_path>>`, `<<test_runner>>` |

Every repo also gets `check: typecheck lint test-q` and `task n s: ./scripts/task.sh {{n}} {{s}}`.
