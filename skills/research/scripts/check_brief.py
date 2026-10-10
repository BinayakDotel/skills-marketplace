#!/usr/bin/env python3
"""Check a research brief (research-brief/1) for structure, ids and quote rules.

    python3 check_brief.py brief.json             structure, ids, quote rules
    python3 check_brief.py reply.md               same, on the last ```json block of a saved reply
    python3 check_brief.py brief.json --fetch     also open every source and look for its quote
    cat reply.md | python3 check_brief.py -       read from stdin

Prints `ok` or `FAIL` with one line per problem; exit status 1 on any error.
Standard library only.
"""
import html, json, re, sys, unicodedata, urllib.error, urllib.request
from html.parser import HTMLParser

SCHEMA = "research-brief/1"
TYPES = {"legend", "history", "practice", "science", "figure", "current"}
CONFIDENCE = {"high", "medium", "low"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FACT_ID = re.compile(r"^F[1-9]\d*$")
VERSION_ID = re.compile(r"^V[1-9]\d*$")
QUOTE_WORDS = (5, 25)


def load(path):
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    stripped = text.lstrip()
    if stripped.startswith("{"):
        return json.loads(stripped)
    blocks = re.findall(r"```json\s*\n(.*?)\n```", text, flags=re.S)
    if not blocks:
        raise ValueError("no JSON object and no ```json block found")
    return json.loads(blocks[-1])


def check(b):
    errs, warns = [], []
    need = {"schema": str, "topic": str, "question": str, "language": str, "researched_on": str,
            "web_access": bool, "facts": list, "versions": list, "disputed": list,
            "dont_say": list, "gaps": list}
    for key, typ in need.items():
        if key not in b:
            errs.append("missing top-level field %r" % key)
        elif not isinstance(b[key], typ):
            errs.append("%r should be %s" % (key, typ.__name__))
    if errs:
        return errs, warns
    if b["schema"] != SCHEMA:
        errs.append("schema is %r, expected %r" % (b["schema"], SCHEMA))
    if not DATE_RE.match(b["researched_on"]):
        errs.append("researched_on must be YYYY-MM-DD")

    facts = {}
    for i, f in enumerate(b["facts"]):
        where = "facts[%d]" % i
        fid = f.get("id", "")
        if not FACT_ID.match(str(fid)):
            errs.append("%s: id %r should look like F1, F2…" % (where, fid))
        elif fid in facts:
            errs.append("%s: duplicate id %s" % (where, fid))
        facts[fid] = f
        where = fid or where
        if not str(f.get("claim", "")).strip():
            errs.append("%s: empty claim" % where)
        if f.get("type") not in TYPES:
            errs.append("%s: type %r is not one of %s" % (where, f.get("type"), sorted(TYPES)))
        if f.get("confidence") not in CONFIDENCE:
            errs.append("%s: confidence %r is not high/medium/low" % (where, f.get("confidence")))
        srcs = f.get("sources")
        if not isinstance(srcs, list):
            errs.append("%s: sources must be a list" % where)
            continue
        if not srcs and b["web_access"]:
            errs.append("%s: no sources (allowed only when web_access is false)" % where)
        if not srcs and f.get("confidence") != "low":
            errs.append("%s: a fact without sources must be confidence low" % where)
        if len(srcs) > 3:
            warns.append("%s: %d sources; 1-3 is enough" % (where, len(srcs)))
        for j, s in enumerate(srcs):
            sw = "%s.sources[%d]" % (where, j)
            if not str(s.get("url", "")).startswith(("http://", "https://")):
                errs.append("%s: url must start with http(s)://" % sw)
            q = str(s.get("quote", "")).strip()
            if not q:
                errs.append("%s: empty quote" % sw)
            else:
                if "…" in q or "..." in q:
                    errs.append("%s: quote contains an ellipsis; copy one unbroken passage" % sw)
                n = len(q.split())
                if not QUOTE_WORDS[0] <= n <= QUOTE_WORDS[1]:
                    warns.append("%s: quote is %d words (aim for %d-%d)" % (sw, n, *QUOTE_WORDS))
            for k in ("accessed", "published"):
                v = s.get(k)
                if v is not None and not DATE_RE.match(str(v)):
                    errs.append("%s: %s must be YYYY-MM-DD or null" % (sw, k))
    if not 1 <= len(facts) <= 40:
        errs.append("brief has %d facts" % len(facts))
    elif not 8 <= len(facts) <= 20:
        warns.append("%d facts (usually 8-20; fine for a narrow topic)" % len(facts))

    versions = {}
    for i, v in enumerate(b["versions"]):
        vid = v.get("id", "")
        if not VERSION_ID.match(str(vid)):
            errs.append("versions[%d]: id %r should look like V1, V2…" % (i, vid))
        versions[vid] = v
        for fid in v.get("facts", []):
            if fid not in facts:
                errs.append("%s: lists unknown fact %s" % (vid, fid))
    for fid, f in facts.items():
        ver = f.get("version")
        if ver is not None and ver not in versions:
            errs.append("%s: version %r is not in versions" % (fid, ver))

    for i, o in enumerate(b.get("outline", []) or []):
        for fid in o.get("facts", []):
            if fid not in facts:
                errs.append("outline[%d]: unknown fact %s" % (i, fid))
            elif facts[fid].get("confidence") == "low":
                errs.append("outline[%d]: uses low-confidence fact %s" % (i, fid))
    for i, d in enumerate(b["disputed"]):
        for fid in d.get("facts", []):
            if fid not in facts:
                errs.append("disputed[%d]: unknown fact %s" % (i, fid))
    return errs, warns


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def _norm(s, loose=False):
    s = unicodedata.normalize("NFKC", html.unescape(s)).lower()
    s = s.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " ", "​": "", "‍": "", "‌": ""}))
    if loose:
        s = re.sub(r"[^\w]+", "", s)
    return re.sub(r"\s+", " ", s).strip()


def fetch_check(b, timeout=20):
    """Return (missing, unreachable) lists of human-readable lines."""
    pages, missing, unreachable = {}, [], []
    for f in b["facts"]:
        for s in f.get("sources", []):
            url = s.get("url", "")
            if url not in pages:
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research-brief checker)"})
                    with urllib.request.urlopen(req, timeout=timeout) as r:
                        raw = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
                    p = _Text()
                    p.feed(raw)
                    pages[url] = " ".join(p.out)
                except (urllib.error.URLError, OSError, ValueError) as e:
                    pages[url] = None
                    unreachable.append("%s: %s" % (url, getattr(e, "reason", e)))
            page = pages[url]
            if page is None:
                continue
            q = s.get("quote", "")
            if _norm(q) in _norm(page) or _norm(q, True) in _norm(page, True):
                continue
            missing.append("%s: quote not found on %s: %r" % (f.get("id"), url, q[:80]))
    return missing, unreachable


def main():
    args = [a for a in sys.argv[1:] if a != "--fetch"]
    if len(args) != 1:
        print(__doc__.strip())
        sys.exit(2)
    try:
        brief = load(args[0])
    except (OSError, ValueError) as e:
        print("FAIL %s\n     - %s" % (args[0], e))
        sys.exit(1)
    errs, warns = check(brief)
    if not errs and "--fetch" in sys.argv:
        missing, unreachable = fetch_check(brief)
        errs += missing
        warns += ["could not open " + u for u in unreachable]
    print(("FAIL " if errs else "ok   ") + args[0])
    for e in errs:
        print("     - " + e)
    for w in warns:
        print("     ~ " + w)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
