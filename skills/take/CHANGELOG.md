# Changelog

## 1.0.0 (2026-10-10)

First release in this repo, rewritten from the per-project versions: project facts now come from `AGENTS.md`, tickets live in GitHub Issues, and Graphite is optional.

- Picks the next ticket from GitHub Issues (earliest milestone, dependencies closed), moves it to in progress with `just task`, grills at most 8 open decisions and writes Decisions and Files into the issue. No code.
