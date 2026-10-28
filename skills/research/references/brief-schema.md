# research-brief/1: every field

One JSON object. Required fields are marked **req**. `brief.schema.json` in this folder is the same contract as a JSON Schema, for apps that import briefs.

The examples on this page show the shape only; they are not researched facts. For a real, sourced brief see `../examples/kasthamandap.json`.

## Top level

| Field | Type | | What goes in it | Example |
|---|---|---|---|---|
| `schema` | string | **req** | Always `research-brief/1` | `"research-brief/1"` |
| `topic` | string | **req** | Short name of the subject | `"Pashupatinath"` |
| `question` | string | **req** | The exact question answered, including any choice you made for an ambiguous topic | `"How did Pashupatinath temple originate, by legend and by record?"` |
| `language` | string | **req** | Language of the final content, short code | `"ne"` |
| `researched_on` | string | **req** | Date of the research, `YYYY-MM-DD` | `"2026-10-09"` |
| `web_access` | boolean | **req** | `false` if you could not search or open pages | `true` |
| `angle` | string | | The story in one line, with its spine (see SKILL.md *Story shape*) | `"The cow that found a god"` |
| `hooks` | string[] | | 2–3 opening scenes or questions an audience can picture; no source names; true on any day | `["Every day one cow's milk dripped onto the same spot in the forest. Why?"]` |
| `outline` | object[] | | 5–8 beats in the *Story shape* order; each `{beat, facts}` | see below |
| `versions` | object[] | **req** | One entry per competing account; `[]` if there is only one | see below |
| `facts` | object[] | **req** | The facts, usually 8–20 | see below |
| `disputed` | object[] | **req** | Real disagreements between good sources; `[]` if none | see below |
| `dont_say` | object[] | **req** | Popular claims that are wrong, unsupported or need attribution; `[]` if none | see below |
| `gaps` | string[] | **req** | What you could not find or open; `[]` if none | `["Could not open the temple trust's history page."]` |
| `notes` | string[] | | Sensitivities and practical cautions | `["Non-Hindus may not enter the main courtyard."]` |

## `facts[]`

| Field | Type | | Rule |
|---|---|---|---|
| `id` | string | **req** | `F1`, `F2`… in order of appearance |
| `claim` | string | **req** | One specific sentence. Legends name who says it. Practices are worded as recurring, with when they happen ("Every year on …"). Figures carry unit and year. Current facts carry "as of <date>". Nothing says "today" or "this year" for the research day. |
| `claim_local` | string | | Same sentence in `language` when that is not English |
| `type` | enum | **req** | `legend`, `history`, `practice`, `science`, `figure`, `current` |
| `version` | string or null | **req** | Version id for a legend fact that belongs to one account, else `null` |
| `confidence` | enum | **req** | `high` (primary source, or two independent reliable sources), `medium` (one reliable source), `low` (weak or conflicting) |
| `sources` | object[] | **req** | 1–3 entries; empty only when `web_access` is `false` |

## `facts[].sources[]`

| Field | Type | | Rule |
|---|---|---|---|
| `url` | string | **req** | The page you opened, not a search result URL |
| `title` | string | **req** | Page or article title as shown |
| `publisher` | string | **req** | Site, outlet, institution or book publisher |
| `published` | string or null | | `YYYY-MM-DD` if the page shows a date |
| `quote` | string | **req** | 5–25 consecutive words copied exactly, in the page's language. No ellipses, no joins. |
| `accessed` | string | **req** | `YYYY-MM-DD` |

Two quotes from one page are two entries with the same `url`.

## `versions[]`

```json
{ "id": "V1", "name": "Cow legend", "summary": "A cow is said to have poured her milk on one spot each day, which led people to the linga.", "facts": ["F3", "F4"] }
```

`summary` may only combine what its listed facts support.

## `outline[]`

```json
{ "beat": "Two legends explain how the linga was found", "facts": ["F3", "F5"] }
```

Only `high` and `medium` facts. Keep each version's beats separate. Each beat says only what its own facts support (an app may drop a beat whose fact the writer can't use), and names no source. Order: the hook moment, the story (two or three beats), the turn (the question the story raises), the answer, bring it home (what people do every time it comes round), a closing image that echoes the opening. Beats are true on any day: no "today" or "this year".

## `disputed[]`

```json
{ "point": "When the first temple was built", "positions": ["Before the 5th century (inscription X)", "Later rebuilding only (historian Y)"], "facts": ["F7", "F8"] }
```

## `dont_say[]`

```json
{ "claim": "The temple was built by one named king in one year.", "why": "Sources only record rebuilding; the original date is unknown.", "source": "https://example.org/page" }
```

`source` is optional; add it when a page shows the claim is wrong.

## Checking

`python3 scripts/check_brief.py brief.json` checks fields, ids, references, quote length and ellipses. Add `--fetch` to open each source and confirm the quote is on the page (needs internet; pages behind logins or heavy JavaScript may report "could not open").
