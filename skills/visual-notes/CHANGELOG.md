# Changelog

## 1.0.2 (2026-09-26)

- Description no longer names another creator; the style credit moved to the repo README.

## 1.0.1 (2026-09-25)

- Renderer no longer leaves `<name>.print.measure.html` next to the PDF when Chrome's page measurement times out.

## 1.0.0 (2026-09-25)

First release in this repo.

- JSON spec in, printable A4 PDF out: `scripts/render_note.py` renders whiteboard and notebook variants with bundled fonts (Kalam, Patrick Hand, JetBrains Mono; OFL).
- Page-fit estimator (`--estimate`) and real-height measurement via headless Chrome/Edge; wkhtmltopdf on Linux; HTML fallback when neither exists.
- `scripts/source_outline.py` reads PDFs and long text files in slices instead of whole.
- Token rules in `SKILL.md` so a note costs little on free-tier plans.
- Model-neutral wording: works in any agent that reads `SKILL.md`, not only Claude.
