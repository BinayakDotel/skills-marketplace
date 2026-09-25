# Changelog

## 1.0.0 (2026-09-25)

First release in this repo.

- JSON spec in, printable A4 PDF out: `scripts/render_note.py` renders whiteboard and notebook variants with bundled fonts (Kalam, Patrick Hand, JetBrains Mono; OFL).
- Page-fit estimator (`--estimate`) and real-height measurement via headless Chrome/Edge; wkhtmltopdf on Linux; HTML fallback when neither exists.
- `scripts/source_outline.py` reads PDFs and long text files in slices instead of whole.
- Token rules in `SKILL.md` so a note costs little on free-tier plans.
- Model-neutral wording: works in any agent that reads `SKILL.md`, not only Claude.
