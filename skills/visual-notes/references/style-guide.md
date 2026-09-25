# Style guide: what makes these pages work

Derived from the two families of reference pages: the **Developer Blz notebook series** (HTML, Docker, Kubernetes) and the **Python revision-notes whiteboard series** (Basics, Lists, Tuples, Dictionaries, Functions, Libraries, File system).

## The feeling to reproduce

A careful student's best notebook page: hand-lettered headings, everything boxed and numbered, colour used to sort ideas, small drawings only where they explain, and a last-minute revision strip at the bottom. Dense but never crowded, because every box holds exactly one kind of thing.

## Anatomy of a page

1. **Title zone**: big hand-lettered title (uppercase, purple or navy), decorative ≡ marks either side; a plain subtitle ("Full revision notes"); optionally a small pill tagline. Notebook variant adds a brand line above ("Developer Blz · Code · Learn · Grow · Together" style) and a yellow marker behind one word of the title.
2. **Corner stickies** (optional, max 4): tilted post-its with a slogan or a reminder, 3–6 words each ("Learn HTML step by step", "Small tags, big websites").
3. **Body**: 2 columns of boxes, occasionally a full-width row. 8–11 numbered boxes per page. Numbers run left column top-to-bottom, then right column, per row.
4. **Revision strip**: dashed pink (or yellow) full-width box, 2–3 columns of ✓ lines, headed "Quick revision points (last-minute)".
5. **Footer**: a slogan left ("Practice today, build tomorrow"), a page pill centre ("Page 03"), a slogan right.

## Box types seen in the references and their renderer equivalents

| Seen on the pages | Block |
|---|---|
| "1. DEFINITION" bullet lists with yellow-highlighted key terms | `bullets` with `==term==` |
| "KEY FEATURES" with ✓ marks | `checks` |
| Operation / Syntax / Example / Result grids | `table` |
| Tag or command pills with a description beside each (HTML links, images; kubectl; docker) | `chips` |
| "Formula box", "Access: d[key]" lines | `kv` |
| "Think:" cloud, "Tip:" bubble, "Remember:" sticky, "Memory trick", "Real-life analogy", "Be careful!" | `callout` kinds think / tip / remember / memory / analogy / warning |
| "Example" code with syntax colours (tags red, attributes green, strings red/blue) | `code` |
| Index strip with positive and negative indexes | `indexstrip` |
| "User input → Variable storage → Processing → Output" | `flow` |
| "RETURN vs PRINT" split by a dashed line | `compare` |
| Pod containing containers; control-plane stacks | `stack` |
| "20. INTERVIEW QUESTIONS" in four coloured columns | `questions` |
| "Quick revision points (last-minute)" | `revision` |

## Colour semantics

- **Purple**: titles, concept headings, "Think" clouds.
- **Blue**: mechanisms, code, syntax, pipelines.
- **Green**: definitions, features, correct/positive, analogies.
- **Pink**: comparisons, revision strip, formulas.
- **Orange**: warnings, tips, "important points".
- **Yellow**: marker highlight inside text, sticky notes, "remember".
- **Red**: "it is NOT", errors, dangerous commands (`rmtree`).
- **Teal / navy / gray**: key ideas, notebook titles, neutral layers.

Alternate colours between neighbouring boxes; never stack three boxes of the same colour. Use at most 5 colours on a page besides yellow highlight.

## Typography

- Headings and bold: Kalam 700 (hand-lettered marker). Body: Patrick Hand (clean print handwriting). Code and chips: JetBrains Mono.
- Body 14.5 px, code 11.4 px, headings 16.5 px uppercase. Do not change sizes in the spec; if text does not fit, cut words.
- Emphasis order: `==highlight==` for the one term to remember, `**bold**` for names of things, `` `code` `` for anything typed literally.

## Variants

- `whiteboard`: the Python revision series. Clean white sheet, thin border, purple title. Best for concept notes and anything code-heavy (more contrast for code blocks).
- `notebook`: the Developer Blz series. Lined paper, spiral binding, brand header, marker behind the first title word, stickies. Best for reference sheets, tool overviews and multi-page series with consistent branding.

## What to avoid

- Long paragraphs; prose wider than 15 words per line.
- Decorative icons on every heading (one emoji per heading at most, and only in notebook variant where it echoes the reference style).
- Un-numbered boxes in the body (numbers are the reader's map).
- Code blocks that wrap: shorten lines or move the block to a full-width row.
- Empty half-columns: rebalance or make the row full width.
- More than 2 pages for one topic; split into sub-topics instead ("Lists", "List methods").
- Copying the reference brand names; give the user their own brand line or none.
