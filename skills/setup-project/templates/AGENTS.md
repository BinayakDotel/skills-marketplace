# <<project_name>>

<<one_sentence>>

<!-- dev-flow:start (written by /setup-project; edit freely, keep this block under 60 lines) -->
## Stack

<<stack_line>>

## Where things are

| Path | What |
|---|---|
<<paths_rows>>

## Commands

Every dev-flow skill uses only these.

| Command | Does |
|---|---|
| `just test-q` | tests, quiet; prints `TRUNCATED` if output was cut |
| `just typecheck` | static checks |
| `just lint` | lint and format check |
| `just check` | typecheck + lint + tests; must pass before a PR |
| `just run` / `just stop` | start the app in the background / stop it (`just logs` to watch) |
| `just task <n> <todo\|in-progress\|in-review\|done>` | move a ticket (label + board) |
<<extra_command_rows>>

## Work

- Tickets: GitHub Issues in `<<repo>>`, board "<<board_title>>", one milestone per phase. See `docs/agents/issue-tracker.md`.
- Spec: `<<spec_path>>`. Decisions and lessons: `docs/DECISIONS.md`. Design: `docs/design/README.md`.
- Git: <<git_tool>>, base branch `<<base_branch>>`. The human merges.

## Models

| Work | Model |
|---|---|
| /tickets, /take | <<model_plan>> |
| /implement, UI translation | <<model_build>> |
| /address, /done | <<model_light>> |
| Stuck after two attempts | <<model_stuck>> |

## Always

- Start from the ticket and its Files. Search before opening; open files one at a time.
- Never bulk-read the repo, lockfiles, `node_modules`, generated code or fixtures (first 40 lines at most).
- Never read or print `.env*`. Never edit `AGENTS.md` or `.cursor/rules/*` during a ticket; propose changes in the report.
- Shortest complete answer. No restating the task, no pasted diffs.
<!-- dev-flow:end -->
