---
name: design-package
description: Design a web app's look once, as files a weaker coding model can follow exactly - Tailwind v4 tokens with the default palette off, static reference screens written in the app's own classes with data-component markers, a components gallery, placeholder art and the design contract. Use when starting the UI of a new project or redesigning one, before any UI tickets; run it with a strong model.
license: MIT
argument-hint: "[screens or spec section]"
---

# Design package

You are the designer; the coding agent that comes later only translates. Make every decision here so nothing is left to it: exact classes, every state, every label.

## Inputs

The spec or screen list, existing mockups or brand notes, and the stack (this skill assumes Tailwind v4; for other stacks keep the same files but write tokens as CSS variables). Ask at most 4 questions in one batch, each with your recommendation: audience and devices, mood (two or three words), languages and scripts, light/dark.

## Output (paths are the defaults `ui-from-reference` and the `ui-web` pack expect)

| File | What |
|---|---|
| `<app>/theme.css` | `:root` colour variables, a dark override under `prefers-color-scheme`, `@theme inline` that maps them and starts with `--color-*: initial;`, fonts as `var(--font-x, "Family")`, custom `@utility` rules for safe areas. Template: `references/theme.css`. |
| `docs/design/screens/_ref.src.css` | `@import "tailwindcss" source(none); @source "./*.html"; @import "<path to theme.css>";` |
| `docs/design/screens/_ref.css` | built by `just ref-css` (`npx @tailwindcss/cli -i … -o …`); commit it |
| `docs/design/screens/00-components.html` | every component, variant and state, including empty, loading, error and disabled |
| `docs/design/screens/<ID>-<name>.html` | one per screen, real sample data, inside the app shell |
| `public/fixtures/art-N.svg` | placeholder images used by references and preview fixtures alike |
| `docs/design/README.md` | the contract, from `setup-project/templates/design-contract.md`: screens table with routes and preview routes, tokens table, type, layout, component inventory with files and props, state maps (status → label), default states, rules |
| `docs/design/screens.json` | `[{ "id", "name", "reference", "preview" }]` for `just shots` |

## How to write the references

- Head boilerplate from `references/head.html`. Only the app's Tailwind classes; no `<style>` blocks, no inline styles except values that are data (a progress width, an image `src`).
- Mark every component instance: `data-component="Button" data-variant="ghost" data-size="sm"`. Use the same name in the inventory. Unmarked wrappers are screen layout.
- Generate the files from one small script with a helper per component, so a component's class string is identical everywhere. Ship the HTML, not the script.
- Pick one class string per component and state; never two spellings of the same thing. Focus ring, disabled and hover states live in the class string.
- Real content in the product's languages (test the longest strings and non-Latin scripts). Labels say what happens next.
- Phone and desktop from the same markup with responsive prefixes. No horizontal scroll at 390 px.

## Check before you hand over

1. `just ref-css`, then screenshot every file at 390 × 844 and 1280 × 800, light and dark (Playwright; set the viewport to the page height so fixed bars sit at the bottom). Look at every image; fix overlaps, overflow and truncation.
2. Text contrast ≥ 4.5:1 for every text token on every background token, both themes.
3. Every `data-component` name is in the inventory and every inventory row appears in `00-components.html`.
4. `docs/DECISIONS.md`: one entry saying the design package exists and how to change it.

Then the coding model builds with `ui-from-reference`, one ticket per screen, primitives first.
