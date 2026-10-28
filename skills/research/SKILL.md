---
name: research
description: 'Research a topic on the web and return a sourced fact brief for a script, video, article or story. Every claim carries a source link and an exact short quote from that page, legend is kept apart from recorded history, competing versions are listed separately, and disputed points, common myths and gaps are flagged. Ends with one JSON block in a fixed format (research-brief/1) that apps can import and check. Use when the user types /research, asks to research or fact-check a topic, wants "the real story" or "facts with sources" behind a festival, legend, temple, place, custom, historical event or recent news, or is preparing content that has to be accurate.'
license: MIT
compatibility: 'Needs web search and page opening (turn web search on in claude.ai, ChatGPT or Grok). Python 3 is optional, for scripts/check_brief.py.'
---

# Research brief

Find out what is actually known about a topic and hand back a brief that someone can write from without re-checking everything. Whoever reads the brief will trust it, so accuracy beats completeness: ten solid facts are worth more than thirty guesses.

When the brief is for a story (a narrated video, an article), it must also carry the story: a person or object to follow, moments you can see, a question that pulls the audience through, and why it matters to their own life. Facts that only say *who reported what* make a report, not a story. And the story must still be true when someone watches it years later (see *Any day, any year*).

## Input

- A topic or question, usually with the user's own idea and notes. Treat their notes as leads to check, never as facts.
- Sometimes: what it is for (for example a 60–90 s narrated video), a target language, things to include or avoid.

If the topic is ambiguous (two places with one name, two festivals with similar names), pick the likely one, say which in `question`, and carry on. Ask a question only when the topic cannot be identified at all.

## Workflow

1. **Break it down** (silently): 4–8 sub-questions. For the origin of a temple, festival or custom: what each legend or text says (one version at a time), which text and roughly how old, what recorded history or archaeology shows and when, what people do today, and what is commonly said but wrong. For a story, add the story questions:
   - Who or what is at the centre: a person, a god in a legend, a community, an object, a journey?
   - What is the single most vivid moment, and what exactly happens in it: who does what, holding what, where?
   - Which numbers could be shown on screen (how many people, how many days, how far)?
   - If a text tells it, what are its actual words at the key moment?
   - What question does the topic make people ask ("why would an army salute a bundle of crops?"), and which fact answers it?
   - When does it happen? Its place in the calendar (which month, lunar day or season; every year, every twelve years), so the story can say "every year on …" instead of "today".
   - What does an ordinary family do with it each time it comes round, step by step, and what does it mean for their lives?
2. **Search wide, then deep.** Use encyclopedic overviews to map names, dates and versions, then open the sources they cite and better ones (see *Source quality*). Search in English and in the topic's own language and script (for Nepal topics, also in Nepali/Devanagari). Budget: about 6–12 searches and 5–10 opened pages.
3. **Open every page you cite.** Never cite a search snippet, a page you could not open, or your own memory. If a page is paywalled or will not load, leave it out and add it to `gaps`.
4. **Record facts while reading**, one claim per fact, each with the exact words that support it. Prefer facts that describe something happening (who, what, where, with what) over facts about who wrote or listed it. A quote is 5–25 consecutive words copied character for character from the page, in the page's own language and spelling. No ellipses inside a quote and no stitching of separate sentences. If no short passage supports a claim, the claim is unsupported: drop it, or reword it to what the page actually says.
5. **Label and rate** each fact (tables below).
6. **Keep versions apart.** When legends or accounts differ, give each one a `versions` entry and tie its facts to it. Never blend two versions into one smooth story.
7. **Hunt the myths.** Popular claims you found to be wrong or unsupported go into `dont_say`. Real disagreement between good sources goes into `disputed`.
8. **Shape the story** when the user is making content (see *Story shape*): one `angle`, 2–3 `hooks`, and an `outline` of 5–8 beats that cite fact ids. Only high- and medium-confidence facts may appear in the outline.
9. **Self-check** (list below), then reply.

## Fact types

| type | Meaning | How to word the claim |
|---|---|---|
| `legend` | what a scripture, text or folk tradition says happened | Name the story or text that tells it: "The Devi Mahatmya says…", "Local legend says…" (never the website you read it on) |
| `history` | documented events: inscriptions, records, archaeology, dated accounts | Plain statement with the date |
| `practice` | what people do, how it is observed, every time it comes round | Habitual present, with when it happens: "Every year on Navami of Dashain, …" |
| `science` | a natural or scientific explanation | Plain statement |
| `figure` | a number, measurement or statistic | Include the unit and the year it applies to |
| `current` | news, or anything likely to change: this year's date of a festival, a price, a count | Include "as of <date>"; the custom itself is a `practice` fact |

## Confidence

- `high`: a primary source, or two independent reliable sources agree.
- `medium`: one reliable source.
- `low`: only weak sources, or reliable sources disagree. Low facts never go into `outline`.

A claim may not say more than its quote supports. Dates may also come from the source's own publication date (`published`). Watch for words that sneak in extra meaning: "oldest", "first", "only", "always", exact numbers.

## Any day, any year

A video or article made from the brief stays up for years, so everything in it must be true on any day it is read or watched.

- Word `angle`, `hooks`, `outline` and `claim_local` for any day: never "today", "tomorrow", "this year" or "now" for the research day.
- Something that recurs (a festival, a ritual, a season, a harvest) is a `practice` fact worded as recurring, with its calendar anchor from a source: "Every year on Navami of Dashain, the temple opens to the public for one day." Use the festival day or lunar day (tithi) the source gives: festivals that follow the moon fall on a different calendar date every year, so this year's date is a separate `current` fact with the year. Word something as recurring only when a source says it recurs.
- A number that changes (a price, a count of visitors, a population) is a `figure` with its year. Never work out a new number (days between two dates, a total, an age) in a claim, a hook or the outline.
- If the user asks about this year's event, still research what happens every time; keep this year's specifics as dated `current` facts.

## Story shape

For content, the `angle`, `hooks` and `outline` are the story's spine; the writer builds on them.

- `angle`: the story in one line, with its spine: "The bundle of crops a whole army salutes", not "Fulpati: history and significance".
- `hooks`: scenes or questions an audience can picture, at most two sentences each, each resting on facts in the brief. Never a summary, the topic's name, or a scene that is true only on one day ("This morning the queue already…").
- `outline`, in this order:
  1. the hook moment;
  2. the story itself, following one person, object or journey, in two or three beats;
  3. the turn: the question the story raises;
  4. the answer, from the facts (the text's words, the evidence, the reason);
  5. bring it home: what people do every time it comes round, and what it says about their lives;
  6. a closing image that echoes the opening.
- Each beat says only what its own facts support, so a writer who drops one fact can drop its beat.
- No source, publication or institution names in `angle`, `hooks` or `outline`. The sources live in `sources`, where they belong.
- `claim_local` is plain spoken language, the way you would tell it. For a legend, attribute it to the story or text ("कथा अनुसार", "दुर्गा सप्तशतीमा"), never to a website, newspaper or organisation. A practice is told as recurring ("हरेक वर्ष दशैंको नवमीमा …"), never as "आज" or "यो वर्ष".

## Source quality (best first)

1. Primary texts and their translations (scriptures, chronicles, inscriptions), official records, archaeological reports.
2. Academic work: university presses, journals, scholarly encyclopedias, museum and UNESCO pages.
3. Government and institutional sites: the body that manages a site, national archives, departments of archaeology, official calendars.
4. Established news outlets with a named author and a date.
5. Wikipedia and general encyclopedias: fine for orientation and for finding sources. Cite them only for uncontroversial basics, and prefer the source they cite.

Prefer sources that tell what happened in detail (the text itself, a scholar's account, a long-form feature) over ones that only mention it. Never rely only on blogs, tour-company pages, content farms, social posts, AI-written pages or forums. Many sites copy one unsourced sentence from each other; that counts as one source, not ten. More per topic type in `references/source-guide.md` (if present).

## Output

Reply with exactly two parts:

1. **A short summary for the user**, 6–10 lines: the answer in one sentence; what is solid; which parts are legend and which versions exist; what is disputed or unverified; anything sensitive.
2. **One fenced `json` block** with the brief, and nothing after it.

The shape, shortened to one entry per list (the full brief behind it is `examples/kasthamandap.json`):

```json
{
  "schema": "research-brief/1",
  "topic": "Kasthamandap",
  "question": "How did Kasthamandap come to be, and how did it give Kathmandu its name?",
  "language": "ne",
  "researched_on": "2026-10-09",
  "web_access": true,
  "angle": "The city named after one wooden pavilion",
  "hooks": ["One wooden pavilion gave Kathmandu its name."],
  "outline": [{ "beat": "Kathmandu is named after a wooden pavilion", "facts": ["F1"] }],
  "versions": [{ "id": "V1", "name": "Single-tree legend", "summary": "Legend says all its timber came from one tree.", "facts": ["F2"] }],
  "facts": [
    {
      "id": "F1",
      "claim": "The name Kathmandu comes from Kasthamandap, a wooden pavilion.",
      "claim_local": "काठमाडौंको नाम काष्ठमण्डप नामको काठको पाटीबाट आएको हो।",
      "type": "history",
      "version": null,
      "confidence": "high",
      "sources": [
        {
          "url": "https://en.wikipedia.org/wiki/Kathmandu",
          "title": "Kathmandu",
          "publisher": "Wikipedia",
          "published": null,
          "quote": "The Nepali name Kathmandu comes from Kasthamandap.",
          "accessed": "2026-10-09"
        }
      ]
    }
  ],
  "disputed": [{ "point": "How old the site is", "positions": ["7th century CE (archaeology)", "5th century (one carbon-dated joint)"], "facts": ["F4", "F8"] }],
  "dont_say": [{ "claim": "It was built from a single tree.", "why": "That is the legend; attribute it: 'legend says'." }],
  "gaps": ["Could not open the 1143 CE manuscript that first mentions the pavilion."],
  "notes": ["The 2015 collapse killed people; keep that part respectful."]
}
```

**Field rules**

- `schema` is always `"research-brief/1"`. `researched_on` and `accessed` are `YYYY-MM-DD`. `language` is the language of the final content as a short code (`ne`, `en`, `hi`).
- Ids: facts `F1`, `F2`… and versions `V1`, `V2`… in order of appearance. Every id used in `outline`, `versions` or `disputed` must exist.
- `claim`: one specific sentence (names, dates, numbers), in English unless the user asked otherwise. `claim_local`: the same sentence in `language` when that is not English; otherwise leave it out.
- `version`: the version id for a legend fact that belongs to one account; otherwise `null`.
- `sources`: 1–3 per fact, each with its own exact quote. Two quotes from the same page are two entries.
- `facts`: usually 8–20. Fewer is fine for a narrow topic; never pad.
- If you cannot search or open pages: say so in the summary, set `web_access` to `false`, give facts from memory with `confidence: "low"` and empty `sources`, and add "No web access: verify everything" to `gaps`.

Every field with examples: `references/brief-schema.md`. Machine-readable schema for apps: `references/brief.schema.json`. A finished brief: `examples/kasthamandap.json`.

## Self-check before replying

- Every fact has at least one source, and every quote is copied, not paraphrased.
- No claim says more than its quote (or the source's date) supports.
- Legends are attributed to their story or text ("…says"), never stated as history.
- For content: the outline follows *Story shape*, and `angle`, `hooks` and `outline` name no source.
- Everything is true on any day: no "today", "tomorrow" or "this year" outside a dated `current` fact; recurring practices carry when they happen; no number you worked out yourself.
- Versions stay separate, and the outline does not merge them.
- Every referenced id exists, the JSON parses, and nothing follows the JSON block.
- If you can run Python: `python3 <skill-dir>/scripts/check_brief.py <file>` prints `ok`. It also reads a whole reply saved as `.md` and checks its last `json` block. `--fetch` also checks that each quote appears on its page.

## Sensitive topics

Religion, caste, ethnicity, politics, living people and tragedies: report what sources say with attribution, give the major viewpoints fairly, keep neutral wording, and record sensitivities in `notes` (for example places where photography is not allowed, or rites a community keeps private). For recent events, prefer reports from the last few days and put the date in the claim.

## Keep it cheap

- Do not paste page text or long working notes into the chat: only the summary and the JSON.
- Do not restate the JSON in prose.
- Stop searching once every sub-question has a high- or medium-confidence fact or is listed in `gaps`.
- `<skill-dir>` is the folder containing this file. Read the files in `references/` only when a field or a source question is unclear.
