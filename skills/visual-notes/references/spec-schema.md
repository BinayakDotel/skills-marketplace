# Spec schema for `render_note.py`

A spec is one JSON object. Either a single page (top-level `rows`) or a series (`pages: [ {…}, {…} ]`). In a series, every top-level field acts as a default that each page may override (`title`, `subtitle`, `variant`, `accent`, `brand`, `footer`, `stickies`); each page sets its own `page` label and `rows`.

## Top-level / page fields

| field | type | notes |
|---|---|---|
| `title` | string | Hand-lettered, uppercase looks best: `"PYTHON LISTS"` |
| `title_highlight` | string | A word of the title to put on a yellow marker (notebook style): `"PYTHON"` |
| `subtitle` | string | Second line under the title |
| `tagline` | string | Small pill under the subtitle; `tagline_color` sets its tint |
| `variant` | `"whiteboard"` \| `"notebook"` | Page chrome |
| `accent` | color name | Title color: purple, blue, green, pink, orange, red, teal, navy, gray |
| `brand` | `{name, tagline}` | Header line at the top (notebook style) |
| `page` | string | Footer pill, e.g. `"Page 02"` |
| `footer` | `{left, right}` | Footer texts (inline markup allowed) |
| `stickies` | list | Corner notes: `{text, color, pos: tl|tr|bl|br, tilt}` (max 4; keep text ≤ 6 words) |
| `rows` | list | Layout, see below |

## Layout

```json
"rows": [
  { "cols": [ [ {block}, {block} ], [ {block} ] ] },        // two columns
  { "cols": [ [ {block} ] ] },                                // full width
  { "cols": [ [ {block} ], [ {block} ], [ {block} ] ], "widths": [30, 40, 30] }   // three columns, custom widths (%)
]
```

Columns are laid out as table cells, so both columns of a row start at the same height; a much taller column leaves white space beside it. Balance by moving blocks between columns or splitting a row.

## Common block fields

`type` (required), `n` (section number shown in a circle; omit for callouts and revision), `title`, `subtitle` (italic line under the heading), `icon` (one emoji before the title, optional), `color` (border/heading color), `dashed` (dashed border), `fill` (tinted background), `note` (small dashed-top footnote inside the box).

## Inline markup (in any text field)

`**bold**` · `==highlight==` · `` `code` `` · `~~strike~~` · `{green:word}` (colors: purple, blue, green, pink, orange, red, yellow, teal, navy, gray) · `->` → arrow · `\n` line break. HTML is escaped, so `<div>` is safe to write literally.

## Blocks

### bullets / checks / stars / numbered
```json
{ "type": "checks", "n": 2, "title": "Key features", "color": "green",
  "items": ["**Ordered** -> keeps insertion order", "**Mutable** -> add, change, remove"],
  "note": "Optional footnote under the list." }
```

### text
```json
{ "type": "text", "n": 1, "title": "HTML (overview)", "text": ["First paragraph.", "Second paragraph."] }
```

### table
```json
{ "type": "table", "n": 5, "title": "Common operations", "color": "green",
  "head": ["Operation", "Syntax", "Example", "Result"],
  "rows": [["Add element", "`list.append(x)`", "`L.append(3)`", "`[1, 2, 3]`"]],
  "mono_cols": [1, 2, 3],
  "note": "Optional note." }
```
`mono_cols` sets whole columns in monospace; backticks do it per cell.

### code
```json
{ "type": "code", "n": 4, "title": "Creating & calling a function", "lang": "python", "color": "blue",
  "code": "def greet(name):\n    return f\"Hello, {name}!\"\n\nprint(greet(\"Alice\"))  # Hello, Alice!",
  "caption": "Define once, use many times." }
```
Languages with highlighting: python, html (also xml/svg), js, bash, sql, json. Anything else renders plain.

### chips
```json
{ "type": "chips", "n": 3, "title": "Links", "subtitle": "Create different types of links", "color": "blue",
  "items": [
    { "chip": "<a href=\"...\">…</a>", "desc": "Anchor tag, the hyperlink." },
    { "chip": "target", "desc": "Where to open the linked document.", "color": "green" } ] }
```
Chip colors cycle automatically; set `color` per item to override.

### kv
```json
{ "type": "kv", "n": 4, "title": "Formula box", "color": "pink",
  "items": [ { "k": "Access", "v": "d[key]" }, { "k": "Safe access", "v": "d.get(key)" } ],
  "mono": true }
```

### callout
```json
{ "type": "callout", "kind": "think", "text": "Define once, use many times!" }
{ "type": "callout", "kind": "remember", "title": "Remember:", "text": ["Lists are mutable.", "Indexing starts at 0."], "tilt": -1.5 }
{ "type": "callout", "kind": "analogy", "title": "Real-life analogy", "text": "A library is a toolbox: use ready-made tools instead of building every one." }
```
Kinds and their look: `think` (rounded cloud, centered), `tip` (purple box with bulb), `remember` (yellow sticky, slightly tilted), `memory` (tan sticky, "Memory trick"), `analogy` (green dashed box), `formula` (pink box), `warning` (red box), `example` (blue dashed box), `key` (teal dashed box, "Key idea"). `title` overrides the default label; `icon: false` hides the emoji; `color` overrides the tint.

### flow
```json
{ "type": "flow", "n": 9, "title": "Text-based diagram", "color": "blue",
  "steps": [ { "label": "User input" }, { "label": "Variable storage", "sub": "memory" }, "Processing", "Output" ],
  "caption": "This is how most simple programs work." }
```
Up to 6 steps in full width, 3–4 in a half column.

### compare
```json
{ "type": "compare", "n": 6, "title": "return vs print", "color": "pink",
  "left":  { "title": "return", "color": "green", "items": ["Sends a value to the caller", "Usable in expressions"] },
  "right": { "title": "print()", "color": "blue",  "items": ["Displays on screen", "Not usable in expressions"] } }
```

### stack
```json
{ "type": "stack", "n": 15, "title": "Pods", "color": "purple", "label": "POD",
  "layers": [ { "label": "Container 1", "color": "blue" }, { "label": "Container 2", "color": "blue" }, { "label": "Shared network & storage", "color": "gray" } ],
  "caption": "Containers in a pod share network and storage." }
```

### indexstrip
```json
{ "type": "indexstrip", "n": 4, "title": "Accessing list elements", "color": "blue",
  "values": ["10", "20", "30", "40", "50", "60"],
  "examples": ["`my_list[0]` -> 10", "`my_list[-1]` -> 60 (last)", "`my_list[1:4]` -> [20, 30, 40]"] }
```

### questions
```json
{ "type": "questions", "n": 20, "title": "Interview questions", "color": "purple",
  "groups": [
    { "title": "Docker basic", "color": "yellow", "items": ["What is Docker?", "Image vs container?"] },
    { "title": "Kubernetes basic", "color": "pink", "items": ["What is a Pod?", "Service types?"] } ] }
```
2–4 groups, 3–7 questions each, full-width row.

### revision
```json
{ "type": "revision", "title": "Quick revision points (last-minute)", "color": "pink", "icon": "🚀",
  "groups": [ ["List = ordered, mutable, allows duplicates.", "Use [ ] to create."],
              ["Indexing starts at 0.", "Slicing [start:end:step]."],
              ["Mutable means changes are permanent.", "len(list) gives the count."] ] }
```
Always the last block, full width, 2–3 groups.

## Minimal complete spec

```json
{
  "title": "PYTHON TUPLES", "subtitle": "Full revision notes", "variant": "whiteboard", "accent": "purple", "page": "Page 01",
  "rows": [
    { "cols": [
      [ { "type": "bullets", "n": 1, "title": "Definition", "items": ["An **ordered, immutable** collection.", "Written with ==( )==."] } ],
      [ { "type": "checks", "n": 2, "title": "Key features", "color": "green", "items": ["Ordered", "Immutable", "Allows duplicates"] } ]
    ] },
    { "cols": [ [ { "type": "revision", "groups": [["Tuple = ordered + immutable."], ["Single element needs a comma: `(5,)`"]] } ] ] }
  ]
}
```
