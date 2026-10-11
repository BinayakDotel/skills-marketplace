# Issue tracker: GitHub

Tickets live in GitHub Issues for `<<repo>>` and on the project board "<<board_title>>". Use the `gh` CLI, never an MCP server.

## Conventions

- One ticket per issue, body from `.github/ISSUE_TEMPLATE/ticket.md`.
- Status is a label, mirrored to the board's Status column by `just task`: `status:todo`, `status:in-progress`, `status:in-review`. Done means closed.
- Phases are milestones. Dependencies are a `Depends: #12, #14` line in the body.
- PR bodies end with `Closes #<n>`, so merging closes the ticket.

## When a skill says "publish to the issue tracker"

`gh issue create --title "<title>" --body-file <tmp> --label status:todo --milestone "<milestone>" --project "<<board_title>>"`

## When a skill says "fetch the relevant ticket"

`gh issue view <n> --json title,body,labels,milestone`

## Comments

`gh issue comment <n> --body-file <tmp>`
