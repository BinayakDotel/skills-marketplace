# Changelog

## 1.0.0 (2026-10-10)

First release in this repo, rewritten from the per-project versions: project facts now come from `AGENTS.md`, tickets live in GitHub Issues, and Graphite is optional.

- Builds the in-progress ticket test-first with `just test-q`, runs `just check` and `code-review`, writes the Outcome into the issue, opens the PR (Graphite or plain git) with `Closes #<n>`, moves the ticket to review.
