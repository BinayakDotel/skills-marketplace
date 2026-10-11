# Design contract

The approved look for this project. The `ui-from-reference` skill follows it; nothing else decides the design. Change it here first, then in code. The `design-package` skill (run with a strong model) fills this file and the references.

**How the references work.** Each screen in `screens/` is static HTML. If it is written with the app's own Tailwind classes (compiled into `screens/_ref.css` by `just ref-css`), copy class strings verbatim. Elements marked `data-component="Name"` (plus `data-variant`, `data-size`, `data-state`) are components from the inventory below; unmarked wrappers are screen layout.

## Screens

Previews render the presentational screen with fixture data and no sign-in.

| Id | Screen | Route | Reference | Preview |
|---|---|---|---|---|

The same list, for `just shots`, lives in `docs/design/screens.json`.

## Tokens

Defined in `<<tokens_path>>`. Only these colour names exist.

| Role | Tailwind | Light | Dark |
|---|---|---|---|

## Type

| Role | Tailwind | Font | Used for |
|---|---|---|---|

## Layout

- Phone:
- Desktop:

## Components

| Component | File | Variants / props | Notes |
|---|---|---|---|

### State maps

| State | Status variant | Label |
|---|---|---|

## Default states

- Empty:
- Loading:
- Error:
- Disabled:

## Rules

-

## Check

`just shots <id>` → `.shots/compare.html` (reference and implementation side by side, phone and desktop, light and dark). After changing tokens or a reference: `just ref-css`.
