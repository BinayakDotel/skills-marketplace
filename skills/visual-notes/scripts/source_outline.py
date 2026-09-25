#!/usr/bin/env python3
"""Read a source cheaply: outline first, then only the pages you need.

  python source_outline.py doc.pdf                 # outline: page ranges + headings + word counts (~500 tokens)
  python source_outline.py doc.pdf --pages 4-9     # cleaned text of those pages (default cap 8000 chars; --max N)
  python source_outline.py doc.pdf --grep "attention"   # pages mentioning a term, one line of context each
  python source_outline.py notes.md                # outline of a text/markdown file (headings + line numbers)
  python source_outline.py notes.md --lines 40-120 # a line range of a text file

Engines for PDF: pdftotext (poppler) if installed, else pypdf, else PyMuPDF. No dependencies for text files.
"""
import re, shutil, subprocess, sys
from pathlib import Path

def pdf_pages(path):
    """Return a list of page texts."""
    if shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, errors="replace").stdout
        return out.split("\f")[:-1] or [out]
    try:
        from pypdf import PdfReader
        return [(p.extract_text() or "") for p in PdfReader(str(path)).pages]
    except ImportError:
        pass
    try:
        import fitz
        return [p.get_text() for p in fitz.open(str(path))]
    except ImportError:
        raise SystemExit("No PDF text engine: install poppler (pdftotext) or `pip install pypdf`.")

HEAD = re.compile(r"^(?:\d+(?:\.\d+)*\s+\S|[A-Z][A-Za-z0-9 ,:&/()'-]{3,70}$|#{1,4}\s)")

def is_heading(line):
    l = line.strip()
    if not (4 <= len(l) <= 80) or l.endswith((".", ",", ";")): return False
    if l.startswith("#"): return True
    words = l.split()
    caps = sum(1 for w in words if w[:1].isupper())
    return bool(HEAD.match(l)) and (caps >= max(1, len(words) * 0.6) or l.isupper())

def outline_pdf(pages):
    total_words = sum(len(p.split()) for p in pages)
    print("%d pages, ~%d words (~%d tokens if read whole)" % (len(pages), total_words, int(total_words * 1.4)))
    found = 0
    for i, txt in enumerate(pages, 1):
        heads = [l.strip() for l in txt.splitlines() if is_heading(l)][:3]
        if heads:
            print("p%-3d %5d w  %s" % (i, len(txt.split()), " | ".join(h[:60] for h in heads))); found += 1
        if found >= 60: print("... (outline truncated; use --grep or --pages)"); break
    if not found:
        for i, txt in enumerate(pages, 1):
            first = re.sub(r"\s+", " ", txt.strip())[:70]
            print("p%-3d %5d w  %s" % (i, len(txt.split()), first))
            if i >= 40: print("..."); break

def rng(spec, n):
    a, _, b = spec.partition("-"); a = int(a); b = int(b) if b else a
    return range(max(1, a), min(n, b) + 1)

def clean(t): return re.sub(r"[ \t]+", " ", re.sub(r"\n{3,}", "\n\n", t)).strip()

def main():
    args = sys.argv[1:]
    if not args: raise SystemExit(__doc__)
    path = Path(args[0]); mx = int(args[args.index("--max") + 1]) if "--max" in args else 8000
    if path.suffix.lower() == ".pdf":
        pages = pdf_pages(path)
        if "--pages" in args:
            sel = rng(args[args.index("--pages") + 1], len(pages)); out = []
            for i in sel: out.append("--- page %d ---\n%s" % (i, clean(pages[i - 1])))
            txt = "\n".join(out); print(txt[:mx] + ("\n... [truncated at %d chars; narrow --pages]" % mx if len(txt) > mx else ""))
        elif "--grep" in args:
            term = args[args.index("--grep") + 1].lower(); hits = 0
            for i, p in enumerate(pages, 1):
                for l in p.splitlines():
                    if term in l.lower(): print("p%-3d %s" % (i, l.strip()[:110])); hits += 1; break
                if hits >= 40: print("..."); break
            if not hits: print("no pages mention", term)
        else:
            outline_pdf(pages)
    else:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        if "--lines" in args:
            sel = rng(args[args.index("--lines") + 1], len(lines)); txt = "\n".join("%4d  %s" % (i, lines[i - 1]) for i in sel)
            print(txt[:mx] + ("\n... [truncated; narrow --lines]" if len(txt) > mx else ""))
        else:
            print("%d lines, ~%d words" % (len(lines), sum(len(l.split()) for l in lines)))
            n = 0
            for i, l in enumerate(lines, 1):
                if is_heading(l): print("%4d  %s" % (i, l.strip()[:80])); n += 1
                if n >= 60: print("..."); break
            if not n: print("(no headings found; use --lines a-b to read a range)")

if __name__ == "__main__":
    main()
