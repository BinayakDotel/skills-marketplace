# skills-marketplace

My agent skills. Each skill is a folder with a `SKILL.md` in the open [Agent Skills](https://agentskills.io/specification) format, so it works in Cursor, Claude (Code, desktop, claude.ai) and other agents that read the format.

## Skills

**General**

| Skill | What it does |
|---|---|
| [research](skills/research/) | Researches a topic on the web and returns a fact brief: every claim with a source link and an exact quote, legends kept apart from history, plus a JSON block apps can import. |
| [visual-notes](skills/visual-notes/) | Turns a topic or notes into a hand-drawn-style one-page study sheet (A4 PDF). |
| [conventional-commits](skills/conventional-commits/) | Writes Conventional Commits messages from a diff or a description. |

**Dev flow** (building software with AI agents, ticket by ticket)

| Skill | When you use it | What it does |
|---|---|---|
| [setup-project](skills/setup-project/) | once per repo | Writes the repo's facts: `AGENTS.md`, a `justfile` with fixed commands, stack rules in `.cursor/rules/`, GitHub board files. |
| [design-package](skills/design-package/) | once per project with screens (run in Claude) | Makes the design: colour and font tokens, reference screens, the design contract. |
| [tickets](skills/tickets/) | once per phase | Turns one spec section into small GitHub issues with acceptance checks, files and dependencies. |
| [take](skills/take/) | start of a ticket | Picks the next ticket, asks up to 8 questions, writes the decisions into the issue. No code. |
| [implement](skills/implement/) | build the ticket | Tests first, then code, `just check`, self-review, opens the PR. |
| [address](skills/address/) | after your PR comments | Fixes each comment on the same branch. |
| [done](skills/done/) | after merge | Marks merged tickets done and names the next one. |
| [ui-from-reference](skills/ui-from-reference/) | automatic, for screen tickets | Builds screens by copying the reference design, then compares screenshots. |

## How the dev flow works

- **Skills are global and never edited per project.** Each repo keeps only its own facts, written once by `/setup-project`.
- **Every repo has the same commands** (`just test-q`, `just check`, `just dev`, `just task <n> <status>`), so the skills work in any stack. Stack details come from packs in `skills/setup-project/packs/` (Next.js, Convex, Vitest, web UI, LLM code, pnpm monorepo, Godot).
- **Tickets live in GitHub Issues and a project board**, used through the `gh` command line.
- **One chat per step:**

```
/take (Grok)  →  /implement (Composer)  →  you review and merge  →  /done (Auto)
                                         ↘ /address (Auto) if you left comments
```

The dev-flow skills use Matt Pocock's `grilling`, `tdd`, `code-review`, `pr` and `handoff` from [mattpocock/skills](https://github.com/mattpocock/skills). Install those separately; don't edit them.

## Install

**Cursor and Claude Code (global, recommended).** From this repo:

```bash
./scripts/sync-skill.sh --all
npx skills add mattpocock/skills -g -a cursor --skill grilling tdd code-review pr handoff diagnosing-bugs -y
```

The first command links every skill into `~/.claude/skills` (Cursor reads it too), so edits here apply everywhere. Keep this clone on `main`. If Cursor doesn't list the skills after a restart, use `./scripts/sync-skill.sh --all --copy` instead.

**Claude Code plugin:**

```
/plugin marketplace add BinayakDotel/skills-marketplace
/plugin install research@binayak-skills
```

**claude.ai / Claude desktop:** `./scripts/sync-skill.sh <name>` builds `dist/<name>.zip`; upload it at Settings → Capabilities → Skills.

**Chat apps without skills** (ChatGPT, Grok): paste the skill's `SKILL.md` as the first message. Works for `research` (with web search on) and `conventional-commits`.

## Working on a skill

```bash
git switch -c my-change
# edit skills/<name>/...
python3 scripts/validate.py        # must print "ok" for every skill
git commit -am "..." && git push   # merge to main, then: git switch main && git pull
```

To add a skill: create `skills/<name>/SKILL.md` (frontmatter `name` = folder name), add a `CHANGELOG.md`, add it to `.claude-plugin/marketplace.json` and to the table above, then run `python3 scripts/validate.py`. Bump the version in `marketplace.json` when you change a skill.

## Layout

```
skills/<name>/                    one folder per skill
.claude-plugin/marketplace.json   catalog for Claude Code
scripts/validate.py               checks every skill (also runs in CI)
scripts/sync-skill.sh             links skills into ~/.claude/skills, builds zips for claude.ai
```

## Credits

The look of `visual-notes` is inspired by hand-drawn revision-notes pages such as the Developer Blz notebook series. No branding from them is used.

## License

[MIT](LICENSE). Fonts in `skills/visual-notes/assets/fonts/` are under the SIL Open Font License.
