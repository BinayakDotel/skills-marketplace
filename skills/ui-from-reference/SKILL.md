---
name: ui-from-reference
description: Build or change web UI by translating the project's approved reference screens and design tokens into components, then checking screenshots against the references side by side. Use for any ticket that touches screens, components or styles in a repo that has docs/design/README.md.
license: MIT
---

# UI from reference

You translate; you don't design. The project's design contract is `docs/design/README.md`: tokens, the component inventory, the screen list and the rules. If the screen or state you need has no reference in `docs/design/screens/`, stop and ask for one instead of inventing it.

## Steps

1. **Read** `docs/design/README.md` and only the screen files the ticket names. Skip `_ref.css`.
2. **Map** each element to a component from the inventory. If the reference marks elements with `data-component="Name"` (and `data-variant`, `data-size`, `data-state`), each marked element is that component with those props. Search the components folder first and reuse what exists. Create a component only if the inventory lists it; give it typed props and no data fetching.
3. **Copy classes.** If the contract says the references use the app's own Tailwind classes, copy each class string verbatim into the component; don't retype, reorder or "improve" it. Otherwise style only through the contract's tokens. Either way: no hex values, no arbitrary values (`w-[13px]`, `text-[#abc]`) unless the contract allows them.
4. **States.** Implement every state the reference shows. For a state it doesn't show (empty, loading, error, disabled), use the contract's default pattern.
5. **Preview.** Each screen renders with fixture data at the contract's preview route, with no sign-in or backend needed. Presentational screen components take props; the page container loads data.
6. **Compare.** `just shots <screen-id>` saves the preview and the reference at phone and desktop widths, in light and dark, and writes `.shots/compare.html`. If you can view images, compare them; otherwise ask the human to open `compare.html`. Fix layout, spacing, type and colour differences; ignore placeholder art.
7. **Accessibility.** Clickable things are buttons or links with a visible focus ring; inputs have labels; motion respects `prefers-reduced-motion`.

## Don't

- Restyle anything outside the ticket.
- Add a UI library, font or icon set the contract doesn't list.
- Change tokens, references or `_ref.css`. Propose changes in your report instead.
