# Content rules: writing the words

The renderer makes the page look right; these rules make it *teach* right.

## Before writing

Answer three questions and let them drive the block list:
1. **Who reads it?** A beginner needs definition → example → analogy first. A practitioner needs syntax → operations → pitfalls first. An interviewee needs questions → short answers → memory trick.
2. **What must survive a week later?** Pick 3–6 things. Each becomes a `==highlight==`, and all of them appear again in the revision strip.
3. **Where does it go wrong?** Every topic has a classic mistake (mutable default args, `rmtree`, off-by-one slicing, injection in RAG). Give it a `warning`, `compare` ("it is NOT / it IS") or a "Be careful!" callout.

## Block budget for one page

8–11 blocks. A good default mix:
- 2–3 bullet/check lists (definition, features, important points)
- 1–2 tables
- 1 code block (or `chips` for command/tag references)
- 1 `kv` (terms or formulas)
- 2 callouts (one analogy or memory trick, one tip/warning/think)
- 1 `compare`, `flow`, `stack` or `indexstrip` (the visual anchor)
- 1 `questions` (optional, interview/exam prep)
- 1 `revision` (always)

If the list runs past 11, split into pages by sub-topic and number them "Page 01, 02…".

## Writing the lines

- One idea per bullet, 6–15 words. Lead with the thing ("**Mutable** -> we can change, add or remove elements"), not with "This means that…".
- Tables: 3–4 columns, 4–8 rows. Column 1 is the name, the last column is the result or the "use it for". Put syntax in backticks.
- Code: one focused example, ≤ 12 lines, ≤ 47 chars per line in a half column (≤ 96 full width). Comments explain *why*, outputs go in comments (`# Output: 25`).
- Chips: the literal thing typed (`docker ps -a`, `<a href="…">`), then a plain-English description of ≤ 12 words.
- `kv`: 4–7 pairs; keys are nouns, values are one line.
- Analogies must map term by term ("Query = what I'm looking for, Key = the label on the shelf, Value = the book itself"). A vague simile is worse than none.
- Memory tricks are short and sayable: "Q asks, K labels, V carries." "AIE RPCS" for list methods.
- Interview questions are questions, phrased as asked ("What is the difference between an image and a container?"), grouped basic → advanced.
- Revision strip: 6–9 lines total across 2–3 groups, each ≤ 12 words, each restating a highlighted term from the page.

## Accuracy

- Do not invent numbers; if a number is illustrative (a made-up attention weight), say so in the subtitle or note.
- Prefer the current name of a tool or API; if unsure whether something still exists or is deprecated, leave it out or verify first.
- Keep version-specific claims ("introduced in Python 3.4") only when sure.

## Numbering and order

Number blocks in reading order: left column top to bottom, right column top to bottom, then the next row. Callouts and the revision strip are unnumbered. Keep the sequence didactic: definition → how it works → example → operations → pitfalls → comparison → questions → revision.

## QA checklist (run on the spec, before rendering; never on a rendered file)

- [ ] `render_note.py ... --estimate` reports every page ≤ 1300 px and no code-wrap warning; otherwise cut lines or split into `pages`.
- [ ] Every numbered block has a number; numbers are sequential in reading order.
- [ ] Both columns of each row estimate within ~120 px of each other (move a block or shorten items).
- [ ] Title ≤ 2 lines; with stickies, ≤ 6 words.
- [ ] At least one example, one analogy/trick, one warning/compare, one revision strip (last).
- [ ] Highlighted terms reappear in the revision strip.
- [ ] Facts checked; illustrative numbers labelled "(illus.)".
