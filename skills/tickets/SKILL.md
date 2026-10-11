---
name: tickets
description: Turn one section or phase of a spec into small, ordered tickets (at most ~5 files each) with acceptance criteria, Files, dependencies and a milestone, and create them in the issue tracker and on the project board. Use when planning the next phase of work from a spec. Part of the dev-flow lifecycle.
license: MIT
disable-model-invocation: true
argument-hint: "<spec path or section> [milestone]"
---

# /tickets <spec section> [milestone]

Project facts live in `AGENTS.md`. Read it, then only the named spec section and `.github/ISSUE_TEMPLATE/ticket.md`.

1. **Survey.** Search the code for files the section touches. Note what already exists.
2. **Slice.** Draft tickets in dependency order. Each one is a vertical slice that ships alone in one PR:
   - at most ~5 files, testable on its own, one observable result;
   - title `<area>: <outcome>` (e.g. `briefs: import a pasted brief`);
   - body from the template: Goal, Acceptance (checkboxes a reviewer can verify), Files (mark new ones), Depends (draft numbers), Reference (spec §, design screen), Out of scope.
   - UI work and its logic are separate tickets when together they pass ~5 files.
3. **Confirm.** Show one line per ticket: number, title, file count, depends. At most 12 per batch. Wait for "go" or edits.
4. **Create** in order, replacing draft numbers with real ones as you go:
   `gh issue create --title "<title>" --body-file <tmp> --label status:todo --milestone "<milestone>" --project "<project title from AGENTS.md>"`
5. **Report** the numbers and titles.

Shortest complete answer. End with one line: `Next: /take on <model for take in AGENTS.md>.`
