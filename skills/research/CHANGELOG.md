# Changelog

## 1.1.0 (2026-10-20)

Briefs now carry a story, not only sourced facts, so scripts written from them stop sounding like reports ("according to UNESCO, the newspaper wrote …").

- Story questions in the breakdown: who or what is at the centre, the most vivid moment, numbers that can be shown, the text's own words, the question the topic raises, what families do today.
- *Story shape*: `angle` is the story's spine; `hooks` are scenes or questions; `outline` follows hook → story → turn → answer → bring it home → closing image, each beat stating only what its own facts support.
- No source, publication or institution names in `angle`, `hooks` or `outline`; `claim_local` attributes a legend to its story or text, never to a website or organisation.
- Prefer facts that describe what happened over facts about who reported it, and sources that tell it in detail.
- The `research-brief/1` format is unchanged: existing apps keep importing.

## 1.0.0 (2026-10-09)

First release in this repo.

- Researches a topic on the web and returns a short summary plus one JSON brief (`research-brief/1`): facts with source links and exact 5–25 word quotes, legend kept apart from history, competing versions, disputed points, popular myths to avoid, gaps and an optional story angle, hooks and outline.
- `references/brief.schema.json` (JSON Schema) and `references/brief-schema.md` describe the format for apps that import briefs.
- `references/source-guide.md`: where to look and what to distrust, by topic type.
- `scripts/check_brief.py` checks structure, ids and quote rules; `--fetch` also confirms each quote is on its page. Standard library only.
- `examples/kasthamandap.json`: a finished brief with sources checked on 2026-10-09.
- Model-neutral wording: works in any agent that reads `SKILL.md`, and can be pasted as instructions into chat apps without skill support.
