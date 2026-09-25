#!/usr/bin/env python3
"""
render_note.py — turn a note spec (JSON) into a self-contained "sketchnote cheat-sheet" HTML page.

Usage:
  python render_note.py spec.json out.html            # HTML with fonts embedded (offline-safe)
  python render_note.py spec.json out.html --pdf      # also write out.pdf  (needs wkhtmltopdf)
  python render_note.py spec.json out.html --pdf-only # write only out.pdf (HTML kept only if no PDF engine)
  python render_note.py spec.json out.html --estimate # print estimated page heights + code-wrap warnings, no rendering
  python render_note.py spec.json out.html --png      # also write out.png  (needs wkhtmltoimage)
  python render_note.py spec.json out.html --fonts link   # link Google Fonts instead of embedding

The spec format is documented in references/spec-schema.md. Nothing in this file
needs editing for normal use: all visual decisions live in the CSS below and are
driven by the spec's variant/accent/color fields.
"""
import base64, html, json, math, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONT_DIR = HERE.parent / "assets" / "fonts"

# ---------------------------------------------------------------- palette
INK = {
    "purple": "#5b21b6", "blue": "#1d4ed8", "green": "#15803d", "pink": "#be185d",
    "orange": "#c2410c", "red": "#b91c1c", "yellow": "#a16207", "teal": "#0f766e", "navy": "#1e3a5f", "gray": "#374151",
}
TINT = {
    "purple": "#ede9fe", "blue": "#dbeafe", "green": "#dcfce7", "pink": "#fce7f3",
    "orange": "#ffedd5", "red": "#fee2e2", "yellow": "#fef9c3", "teal": "#ccfbf1", "navy": "#e0e7ff", "gray": "#f3f4f6",
}
LINE = {
    "purple": "#7c3aed", "blue": "#2563eb", "green": "#16a34a", "pink": "#db2777",
    "orange": "#ea580c", "red": "#dc2626", "yellow": "#eab308", "teal": "#0d9488", "navy": "#3b5998", "gray": "#6b7280",
}
CYCLE = ["pink", "green", "blue", "orange", "purple", "yellow", "teal"]

def ink(c): return INK.get(c, INK["purple"])
def tint(c): return TINT.get(c, TINT["purple"])
def line(c): return LINE.get(c, LINE["purple"])

# ---------------------------------------------------------------- inline markup
def esc(s): return html.escape(str(s), quote=False)

def md(s):
    """Inline markup: **bold**, ==highlight==, `code`, {color:text}, ~~strike~~, -> arrow, \\n line break."""
    if s is None: return ""
    t = esc(s)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r"`([^`]+)`", r'<code class="ic">\1</code>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"==(.+?)==", r"<mark>\1</mark>", t)
    t = re.sub(r"~~(.+?)~~", r"<s>\1</s>", t)
    t = re.sub(r"\{(purple|blue|green|pink|orange|red|yellow|teal|navy|gray):(.+?)\}",
               lambda m: '<span style="color:%s;font-weight:700">%s</span>' % (ink(m.group(1)), m.group(2)), t)
    t = t.replace("-&gt;", "&rarr;").replace("&lt;-", "&larr;").replace("=&gt;", "&rArr;")
    t = t.replace("\n", "<br>")
    return t

# ---------------------------------------------------------------- code highlighting
KW = {
    "python": r"\b(def|return|if|elif|else|for|while|in|not|and|or|import|from|as|class|try|except|finally|with|lambda|pass|break|continue|yield|None|True|False|is|global|nonlocal|raise|async|await|del)\b",
    "js": r"\b(const|let|var|function|return|if|else|for|while|of|in|import|from|export|default|class|new|this|try|catch|finally|throw|async|await|null|undefined|true|false|typeof)\b",
    "bash": r"^\s*(pip|python|python3|npm|npx|node|docker|kubectl|git|cd|ls|mkdir|rm|cp|mv|cat|echo|export|source|uv|curl)\b",
    "sql": r"\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|ON|GROUP BY|ORDER BY|LIMIT|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|AS|AND|OR|NOT|NULL)\b",
}
BUILTIN = r"\b(print|len|type|range|sum|min|max|sorted|list|dict|set|tuple|str|int|float|bool|open|enumerate|zip|map|filter|input|isinstance|super|self)\b"

def hl_generic(code, lang):
    """Single-pass tokenizer so inserted markup is never re-matched."""
    kw = KW.get(lang)
    parts = [r"(?P<cm>#.*$|//.*$)" if lang in ("python", "bash", "js") else r"(?P<cm>--.*$)",
             r"(?P<st>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')"]
    if kw: parts.append("(?P<kw>%s)" % kw.strip("^"))
    if lang == "python": parts.append("(?P<bi>%s)" % BUILTIN)
    parts.append(r"(?P<nu>(?<![\w.])\d+(?:\.\d+)?\b)")
    rx = re.compile("|".join(parts), re.M)
    def sub(m):
        kind = m.lastgroup; text = esc(m.group(0))
        if kind == "kw" and lang == "bash" and not re.match(KW["bash"], m.string[m.string.rfind("\n", 0, m.start()) + 1:m.end()]):
            return text
        return '<span class="%s">%s</span>' % (kind, text)
    out, pos = [], 0
    for m in rx.finditer(code):
        out.append(esc(code[pos:m.start()])); out.append(sub(m)); pos = m.end()
    out.append(esc(code[pos:]))
    return "".join(out)

def hl_html(code):
    s = esc(code)
    s = re.sub(r"(&lt;!--.*?--&gt;)", r'<span class="cm">\1</span>', s, flags=re.S)
    def tag(m):
        inner = m.group(2)
        inner = re.sub(r'([\w-]+)=(&quot;.*?&quot;|".*?")', r'<span class="at">\1</span>=<span class="st">\2</span>', inner)
        return '<span class="tg">&lt;%s</span>%s<span class="tg">&gt;</span>' % (m.group(1), inner)
    s = re.sub(r"&lt;(/?[\w!-]+)(.*?)&gt;", tag, s, flags=re.S)
    return s

def highlight(code, lang):
    lang = (lang or "text").lower()
    if lang in ("html", "xml", "svg"): return hl_html(code)
    if lang == "json": return hl_generic(code, "js")
    if lang in ("python", "js", "bash", "sql"): return hl_generic(code, lang)
    return esc(code)

# ---------------------------------------------------------------- blocks
def head(b, default_color="purple"):
    """Numbered section heading."""
    n = b.get("n"); title = b.get("title")
    if not title: return ""
    c = b.get("color", default_color)
    num = '<span class="num" style="background:%s;border-color:%s">%s</span>' % (tint(c), line(c), esc(n)) if n not in (None, "") else ""
    icon = '<span class="ico">%s</span>' % esc(b["icon"]) if b.get("icon") else ""
    sub = '<div class="sub">%s</div>' % md(b["subtitle"]) if b.get("subtitle") else ""
    return '<div class="bh" style="color:%s">%s%s<span class="bt">%s</span></div>%s' % (ink(c), num, icon, md(title), sub)

def box(b, inner, default_color="purple", extra_cls=""):
    c = b.get("color", default_color)
    style = "border-color:%s" % line(c)
    if b.get("dashed"): style += ";border-style:dashed"
    if b.get("fill"): style += ";background:%s" % tint(c)
    return '<div class="blk %s" style="%s">%s%s</div>' % (extra_cls, style, head(b, c), inner)

def r_bullets(b, marker="•"):
    items = b.get("items", [])
    cls = {"•": "ul", "✓": "ul chk", "★": "ul star", "1": "ol"}[marker]
    tag = "ol" if marker == "1" else "ul"
    lis = "".join("<li>%s</li>" % md(i) for i in items)
    note = '<div class="note">%s</div>' % md(b["note"]) if b.get("note") else ""
    return box(b, "<%s class=\"%s\">%s</%s>%s" % (tag, cls, lis, tag, note))

def r_text(b):
    paras = b.get("text", "")
    if isinstance(paras, str): paras = [paras]
    return box(b, "".join("<p>%s</p>" % md(p) for p in paras))

def r_table(b):
    c = b.get("color", "green"); mono = set(b.get("mono_cols", []))
    th = "".join("<th>%s</th>" % md(h) for h in b.get("head", []))
    rows = []
    for r in b.get("rows", []):
        tds = "".join('<td class="%s">%s</td>' % ("mono" if i in mono else "", md(v)) for i, v in enumerate(r))
        rows.append("<tr>%s</tr>" % tds)
    inner = '<table class="tb"><thead style="background:%s"><tr>%s</tr></thead><tbody>%s</tbody></table>' % (tint(c), th, "".join(rows))
    note = '<div class="note">%s</div>' % md(b["note"]) if b.get("note") else ""
    return box(b, inner + note, c)

def r_code(b):
    cap = '<div class="cap">%s</div>' % md(b["caption"]) if b.get("caption") else ""
    lab = '<span class="lang">%s</span>' % esc(b.get("lang", "")) if b.get("lang") else ""
    inner = '<pre class="code">%s%s</pre>%s' % (lab, highlight(b.get("code", ""), b.get("lang")), cap)
    return box(b, inner, b.get("color", "blue"), "codeblk")

def r_chips(b):
    rows = []
    for i, it in enumerate(b.get("items", [])):
        c = it.get("color", CYCLE[i % len(CYCLE)])
        rows.append('<tr><td class="chipc"><span class="chip" style="background:%s;border-color:%s">%s</span></td><td class="chipd">%s</td></tr>'
                    % (tint(c), line(c), md(it.get("chip", "")), md(it.get("desc", ""))))
    return box(b, '<table class="chips">%s</table>' % "".join(rows), b.get("color", "blue"))

def r_kv(b):
    rows = "".join('<tr><td class="k" style="color:%s">%s</td><td class="v %s">%s</td></tr>' % (ink(it.get("color", CYCLE[i % len(CYCLE)])), md(it.get("k", "")), "mono" if (it.get("mono") or b.get("mono")) else "", md(it.get("v", "")))
                   for i, it in enumerate(b.get("items", [])))
    return box(b, '<table class="kv">%s</table>' % rows, b.get("color", "blue"))

def r_callout(b):
    kind = b.get("kind", "tip")
    presets = {
        "think":   ("purple", "💭", "Think:",          "cloud"),
        "tip":     ("purple", "💡", "Tip:",            "tipbox"),
        "remember":("yellow", "📌", "Remember:",       "sticky"),
        "memory":  ("orange", "🧠", "Memory trick:",   "sticky"),
        "analogy": ("green",  "🧩", "Real-life analogy:", "dashbox"),
        "formula": ("pink",   "🧮", "Formula box:",    "formula"),
        "warning": ("red",    "⚠️", "Be careful!",     "warnbox"),
        "example": ("blue",   "✏️", "Example:",        "dashbox"),
        "key":     ("teal",   "🔑", "Key idea:",       "dashbox"),
    }
    c, ico, deftitle, cls = presets.get(kind, presets["tip"])
    c = b.get("color", c)
    title = b.get("title", deftitle)
    body = b.get("text", "")
    if isinstance(body, list):
        body = '<ul class="ul">%s</ul>' % "".join("<li>%s</li>" % md(i) for i in body)
    else:
        body = "<p>%s</p>" % md(body)
    rot = ' style="-webkit-transform:rotate(%sdeg);transform:rotate(%sdeg)"' % (b.get("tilt", -1.2), b.get("tilt", -1.2)) if cls == "sticky" else ""
    return ('<div class="co %s"%s><div class="coin" style="border-color:%s;background:%s">'
            '<div class="cot" style="color:%s">%s %s</div>%s</div></div>') % (cls, rot, line(c), tint(c) if cls != "cloud" else "#fff", ink(c), ico if b.get("icon", True) else "", md(title), body)

def r_flow(b):
    steps = b.get("steps", [])
    cells = []
    for i, s in enumerate(steps):
        c = s.get("color", CYCLE[i % len(CYCLE)]) if isinstance(s, dict) else CYCLE[i % len(CYCLE)]
        label = s.get("label", "") if isinstance(s, dict) else s
        sub = ('<div class="fsub">%s</div>' % md(s.get("sub"))) if isinstance(s, dict) and s.get("sub") else ""
        cells.append('<td class="fcell"><div class="fbox" style="border-color:%s;background:%s">%s%s</div></td>' % (line(c), tint(c), md(label), sub))
        if i < len(steps) - 1: cells.append('<td class="farrow">&rarr;</td>')
    cap = '<div class="cap">%s</div>' % md(b["caption"]) if b.get("caption") else ""
    return box(b, '<table class="flow"><tr>%s</tr></table>%s' % ("".join(cells), cap), b.get("color", "blue"))

def r_compare(b):
    def col(side):
        t = '<div class="cph" style="color:%s">%s</div>' % (ink(side.get("color", "green")), md(side.get("title", "")))
        return t + '<ul class="ul">%s</ul>' % "".join("<li>%s</li>" % md(i) for i in side.get("items", []))
    inner = '<table class="cmp"><tr><td class="cpl">%s</td><td class="cpr">%s</td></tr></table>' % (col(b.get("left", {})), col(b.get("right", {})))
    return box(b, inner, b.get("color", "pink"))

def r_revision(b):
    groups = b.get("groups") or [b.get("items", [])]
    tds = "".join('<td><ul class="ul chk">%s</ul></td>' % "".join("<li>%s</li>" % md(i) for i in g) for g in groups)
    c = b.get("color", "pink")
    title = b.get("title", "Quick revision points (last-minute)")
    return ('<div class="rev" style="border-color:%s;background:%s"><div class="revt" style="color:%s">%s %s</div>'
            '<table class="revg"><tr>%s</tr></table></div>') % (line(c), tint(c), ink(c), esc(b.get("icon", "🚀")), md(title), tds)

def r_questions(b):
    tds = []
    for i, g in enumerate(b.get("groups", [])):
        c = g.get("color", CYCLE[i % len(CYCLE)])
        lis = "".join('<li><span class="qn" style="background:%s;color:%s">%d</span>%s</li>' % (tint(c), ink(c), j + 1, md(q)) for j, q in enumerate(g.get("items", [])))
        tds.append('<td class="qcol"><div class="qbox" style="border-color:%s"><div class="qh" style="background:%s;color:%s">%s</div><ul class="ql">%s</ul></div></td>' % (line(c), tint(c), ink(c), md(g.get("title", "")), lis))
    return box(b, '<table class="qs"><tr>%s</tr></table>' % "".join(tds), b.get("color", "purple"))

def r_indexstrip(b):
    vals = b.get("values", []); n = len(vals)
    pos = "".join('<td class="ix">%d</td>' % i for i in range(n))
    neg = "".join('<td class="ix neg">%d</td>' % (i - n) for i in range(n))
    cells = "".join('<td class="cell">%s</td>' % md(v) for v in vals)
    inner = ('<div class="ixlab pos">%s</div><table class="strip"><tr>%s</tr><tr>%s</tr><tr>%s</tr></table><div class="ixlab neg">%s</div>'
             % (md(b.get("pos_label", "Positive indexes")), pos, cells, neg, md(b.get("neg_label", "Negative indexes"))))
    ex = '<ul class="ul">%s</ul>' % "".join("<li>%s</li>" % md(i) for i in b.get("examples", [])) if b.get("examples") else ""
    return box(b, inner + ex, b.get("color", "blue"))

def r_stack(b):
    """Vertical nested boxes, e.g. Pod → containers; or a 'layers' picture."""
    layers = "".join('<div class="layer" style="border-color:%s;background:%s">%s</div>' % (line(l.get("color", CYCLE[i % len(CYCLE)])), tint(l.get("color", CYCLE[i % len(CYCLE)])), md(l.get("label", l) if isinstance(l, dict) else l))
                     for i, l in enumerate(b.get("layers", [])))
    cap = '<div class="cap">%s</div>' % md(b["caption"]) if b.get("caption") else ""
    return box(b, '<div class="stack" style="border-color:%s"><div class="stackt">%s</div>%s</div>%s' % (line(b.get("color", "purple")), md(b.get("label", "")), layers, cap), b.get("color", "purple"))

RENDER = {
    "bullets": lambda b: r_bullets(b, "•"), "checks": lambda b: r_bullets(b, "✓"), "stars": lambda b: r_bullets(b, "★"),
    "numbered": lambda b: r_bullets(b, "1"), "text": r_text, "table": r_table, "code": r_code, "chips": r_chips,
    "kv": r_kv, "callout": r_callout, "flow": r_flow, "compare": r_compare, "revision": r_revision,
    "questions": r_questions, "indexstrip": r_indexstrip, "stack": r_stack,
}

def render_block(b):
    fn = RENDER.get(b.get("type", "bullets"))
    if not fn: raise SystemExit("Unknown block type: %s" % b.get("type"))
    return fn(b)

def render_rows(rows):
    out = []
    for row in rows:
        cols = row.get("cols", [])
        n = max(1, len(cols))
        widths = row.get("widths") or [100.0 / n] * n
        tds = []
        for col, w in zip(cols, widths):
            tds.append('<td class="col" style="width:%s%%">%s</td>' % (w, "".join(render_block(b) for b in col)))
        out.append('<table class="row"><tr>%s</tr></table>' % "".join(tds))
    return "".join(out)

# ---------------------------------------------------------------- page chrome
def stickies_html(items):
    out = []
    for i, s in enumerate(items or []):
        if isinstance(s, str): s = {"text": s}
        pos = s.get("pos", ["tl", "tr", "bl", "br"][i % 4]); c = s.get("color", ["yellow", "pink", "blue", "green"][i % 4])
        tilt = s.get("tilt", [-4, 3, 2, -3][i % 4])
        out.append('<div class="pin %s" style="background:%s;border-color:%s;-webkit-transform:rotate(%sdeg);transform:rotate(%sdeg)">%s</div>' % (pos, tint(c), line(c), tilt, tilt, md(s["text"])))
    return "".join(out)

def font_css(mode):
    if mode == "system": return ""
    if mode == "link":
        return ('<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&family=Patrick+Hand&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">')
    faces = []
    spec = [("Kalam", 400, "kalam-latin-400-normal.woff"), ("Kalam", 700, "kalam-latin-700-normal.woff"),
            ("Patrick Hand", 400, "patrick-hand-latin-400-normal.woff"),
            ("JetBrains Mono", 400, "jetbrains-mono-latin-400-normal.woff"), ("JetBrains Mono", 700, "jetbrains-mono-latin-700-normal.woff")]
    for fam, w, fn in spec:
        p = FONT_DIR / fn
        if not p.exists(): continue
        b64 = base64.b64encode(p.read_bytes()).decode()
        faces.append("@font-face{font-family:'%s';font-weight:%d;font-style:normal;src:url(data:font/woff;base64,%s) format('woff')}" % (fam, w, b64))
    if not faces: return font_css("link")
    return "<style>%s</style>" % "".join(faces)

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#e9ecef;font-family:'Patrick Hand','Comic Sans MS','Segoe Print',cursive;color:#1f2937;font-size:14.5px;line-height:1.32}
mark{background:#fde047;padding:0 3px;border-radius:3px;color:inherit}
a{color:#1d4ed8;text-decoration-thickness:1px;text-underline-offset:2px}
b{font-family:'Kalam',cursive;font-weight:700;font-size:.96em}
code.ic{font-family:'JetBrains Mono',Consolas,monospace;font-size:12.5px;background:#f3f4f6;padding:0 4px;border-radius:4px;color:#1e3a5f}
.page{position:relative;width:800px;margin:0 auto 18px;background:#fff;padding:26px 30px 22px;border:1.5px solid #4b5563;border-radius:6px;overflow:hidden;page-break-after:always}
.page:last-child{page-break-after:auto;margin-bottom:0}
body{padding:18px 0}
.page.notebook{background:#fbfbf7;border-color:#9ca3af;padding-left:62px;
  background-image:-webkit-repeating-linear-gradient(top,transparent 0,transparent 27px,#cfe0f5 27px,#cfe0f5 28px);
  background-image:repeating-linear-gradient(180deg,transparent 0,transparent 27px,#cfe0f5 27px,#cfe0f5 28px)}
.page.notebook:before{content:'';position:absolute;left:0;top:0;bottom:0;width:34px;background:#eceff3;border-right:2px solid #9ca3af;
  background-image:-webkit-repeating-linear-gradient(top,transparent 0,transparent 8px,#1f2937 8px,#1f2937 22px,transparent 22px,transparent 30px);
  background-image:repeating-linear-gradient(180deg,transparent 0,transparent 8px,#1f2937 8px,#1f2937 22px,transparent 22px,transparent 30px);
  background-size:14px 30px;background-repeat:repeat-y;background-position:10px 0}
.brand{text-align:center;font-family:'Kalam',cursive;font-weight:700;font-size:20px;color:#111827;margin:-6px 0 2px}
.brand .tag{display:block;font-family:'Patrick Hand',cursive;font-weight:400;font-size:13px;color:#4b5563}
.title{text-align:center;margin:2px 0 4px}
.title h1{font-family:'Kalam',cursive;font-weight:700;font-size:42px;letter-spacing:1px;margin:0;line-height:1.05}
.page.has-stickies .title h1{padding:0 108px;font-size:36px}
.title h1 .dash{font-size:30px;vertical-align:8px;opacity:.7;margin:0 10px}
.title h1 .hl{background:#fde047;padding:0 10px;border-radius:6px}
.title .subtitle{font-family:'Kalam',cursive;font-weight:700;font-size:22px;color:#374151;margin-top:2px}
.title .tagline{display:inline-block;margin-top:6px;padding:2px 12px;border-radius:14px;font-size:14px;color:#374151}
.pin{position:absolute;padding:5px 9px;border:1.5px solid;border-radius:3px;font-family:'Kalam',cursive;font-weight:700;font-size:12.5px;line-height:1.15;color:#1f2937;max-width:118px;z-index:2;box-shadow:1px 2px 3px rgba(0,0,0,.12)}
.pin.tl{left:44px;top:14px}.pin.tr{right:20px;top:14px}.pin.bl{left:44px;top:64px}.pin.br{right:20px;top:64px}
.page.notebook .pin.tl,.page.notebook .pin.bl{left:72px}
.row{width:100%;border-collapse:separate;border-spacing:10px 0;margin:0 -10px;table-layout:fixed}
.col{vertical-align:top}
.blk{border:1.8px solid;border-radius:14px 11px 13px 10px/10px 13px 11px 14px;padding:7px 10px 8px;margin:0 0 9px;background:#fff}
.bh{font-family:'Kalam',cursive;font-weight:700;font-size:16.5px;letter-spacing:.3px;text-transform:uppercase;margin:0 0 5px;padding-bottom:2px;border-bottom:2px solid #e5e7eb}
.bh .num{display:inline-block;min-width:20px;height:20px;line-height:17px;text-align:center;border:1.5px solid;border-radius:50%;font-size:12.5px;margin-right:7px;color:#1f2937;vertical-align:1px}
.bh .ico{margin-right:6px;font-size:15px}
.sub{font-size:13px;color:#4b5563;margin:-3px 0 6px;font-style:italic}
p{margin:0 0 5px}
ul.ul,ol.ol{margin:0;padding-left:16px}
ul.ul li,ol.ol li{margin:0 0 2px}
ul.ul.chk{list-style:none;padding-left:2px}
ul.ul.chk li:before{content:'\\2713';color:#15803d;font-weight:700;margin-right:6px}
ul.ul.star{list-style:none;padding-left:2px}
ul.ul.star li:before{content:'\\2605';color:#f59e0b;margin-right:6px}
.note{margin-top:6px;font-size:13px;color:#4b5563;border-top:1px dashed #d1d5db;padding-top:4px}
.cap{margin-top:5px;font-size:13px;color:#4b5563;font-style:italic}
table.tb{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:2px}
table.tb th,table.tb td{border:1px solid #9ca3af;padding:3px 6px;text-align:left;vertical-align:top}
table.tb th{font-weight:700;color:#1f2937}
table.tb td.mono,table.tb td code.ic{font-family:'JetBrains Mono',monospace;font-size:12px}
pre.code{position:relative;margin:0;background:#f8fafc;border:1.2px solid #cbd5e1;border-radius:8px;padding:7px 9px;font-family:'JetBrains Mono',Consolas,monospace;font-size:11.4px;line-height:1.42;white-space:pre-wrap;word-wrap:break-word;color:#1e293b}
pre.code .lang{position:absolute;right:8px;top:4px;font-size:10px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px}
.kw{color:#1d4ed8;font-weight:700}.st{color:#b91c1c}.cm{color:#15803d;font-style:italic}.nu{color:#c2410c}.bi{color:#6d28d9}.tg{color:#b91c1c}.at{color:#15803d}
table.chips{border-collapse:separate;border-spacing:0 5px;width:100%}
.chipc{width:47%;vertical-align:top;padding-right:8px}
.chip{display:inline-block;border:1.2px solid;border-radius:6px;padding:2px 7px;font-family:'JetBrains Mono',monospace;font-size:11.5px;font-weight:700;color:#1f2937;line-height:1.3}
.chipd{vertical-align:top;font-size:13.5px;line-height:1.3}
table.kv{border-collapse:collapse}
table.kv td{padding:2px 6px 2px 0;vertical-align:top;font-size:14px}
table.kv td.k{font-weight:700;white-space:nowrap}
table.kv td.v{font-size:13.5px}
table.kv td.v.mono{font-family:'JetBrains Mono',monospace;font-size:12px}
.co{margin:0 0 10px}
.coin{border:1.8px solid;border-radius:10px;padding:7px 10px}
.cot{font-family:'Kalam',cursive;font-weight:700;font-size:15px;margin-bottom:2px}
.co.cloud .coin{border-radius:28px;border-style:solid;padding:9px 16px;text-align:center}
.co.dashbox .coin{border-style:dashed}
.co.sticky{padding:4px 2px}
.co.sticky .coin{border-radius:2px;box-shadow:2px 3px 4px rgba(0,0,0,.15)}
.co.formula .coin{border-radius:6px}
.co.warnbox .coin{border-radius:6px}
.co p{margin:0}
table.flow{border-collapse:collapse;width:100%;margin-top:4px;table-layout:fixed}
.fcell{vertical-align:middle;padding:0}
.fbox{border:1.6px solid;border-radius:8px;padding:5px 3px;text-align:center;font-weight:700;font-size:12.5px;line-height:1.15;word-wrap:break-word}
.fsub{font-weight:400;font-size:11px;color:#4b5563;margin-top:2px}
.farrow{width:16px;text-align:center;color:#374151;font-size:18px;vertical-align:middle}
table.cmp{width:100%;border-collapse:collapse}
.cpl,.cpr{width:50%;vertical-align:top;padding:2px 8px}
.cpl{border-right:2px dashed #93c5fd}
.cph{font-family:'Kalam',cursive;font-weight:700;font-size:15px;text-align:center;text-decoration:underline;margin-bottom:4px}
.rev{border:2px dashed;border-radius:14px;padding:8px 12px 6px;margin:2px 0 10px}
.revt{font-family:'Kalam',cursive;font-weight:700;font-size:16px;text-transform:uppercase;margin-bottom:4px}
table.revg{width:100%;border-collapse:collapse;table-layout:fixed}
table.revg td{vertical-align:top;padding:0 8px 0 0;font-size:13.5px}
table.revg td+td{border-left:1.5px solid rgba(0,0,0,.15);padding-left:10px}
table.qs{width:100%;border-collapse:separate;border-spacing:6px 0;margin:0 -6px;table-layout:fixed}
.qcol{vertical-align:top}
.qbox{border:1.6px solid;border-radius:10px;overflow:hidden;background:#fff}
.qh{font-family:'Kalam',cursive;font-weight:700;font-size:13.5px;text-align:center;padding:3px 4px;text-transform:uppercase}
ul.ql{list-style:none;margin:0;padding:6px 7px}
ul.ql li{font-size:12.5px;margin:0 0 5px;line-height:1.25}
.qn{display:inline-block;width:16px;height:16px;line-height:16px;border-radius:50%;text-align:center;font-size:10.5px;font-weight:700;margin-right:5px}
.ixlab{font-size:12.5px;font-weight:700;text-align:center;margin:2px 0}
.ixlab.pos{color:#1d4ed8}.ixlab.neg{color:#b91c1c}
table.strip{border-collapse:collapse;margin:0 auto}
table.strip td{text-align:center;padding:1px 0;min-width:56px}
table.strip td.ix{font-size:12.5px;color:#1d4ed8;font-weight:700}
table.strip td.ix.neg{color:#b91c1c}
table.strip td.cell{border:1.6px solid #374151;padding:4px 8px;font-family:'JetBrains Mono',monospace;font-size:13px;background:#fff}
.stack{border:1.6px solid;border-radius:10px;padding:6px 8px;text-align:center;background:#fff}
.stackt{font-family:'Kalam',cursive;font-weight:700;font-size:14px;margin-bottom:4px}
.layer{border:1.4px solid;border-radius:6px;padding:4px 6px;margin:0 auto 5px;font-size:13px;font-weight:700;width:86%}
.footer{margin-top:4px;padding-top:6px;border-top:1.5px dashed #9ca3af;font-family:'Kalam',cursive;font-weight:700;font-size:13px;color:#374151;width:100%}
.footer td{vertical-align:middle}
.footer .pg{display:inline-block;padding:2px 14px;border-radius:12px;background:#dbeafe;color:#1e3a5f;font-size:14px}
.deco{position:absolute;font-size:22px;opacity:.9}
@media print{body{background:#fff}.page{border:none;border-radius:0;width:100%;margin:0}@page{size:A4 portrait;margin:8mm}}
"""

def render_page(spec, defaults):
    g = lambda k, d=None: spec.get(k, defaults.get(k, d))
    variant = g("variant", "whiteboard"); accent = g("accent", "purple")
    title = g("title", "Untitled"); hl = g("title_highlight")
    title_html = md(title)
    if hl and hl in title: title_html = title_html.replace(esc(hl), '<span class="hl">%s</span>' % esc(hl), 1)
    t = '<div class="title"><h1 style="color:%s"><span class="dash">&#8801;</span>%s<span class="dash">&#8801;</span></h1>' % (ink(accent), title_html)
    if g("subtitle"): t += '<div class="subtitle">%s</div>' % md(g("subtitle"))
    if g("tagline"): t += '<div class="tagline" style="background:%s">%s</div>' % (tint(g("tagline_color", "pink")), md(g("tagline")))
    t += "</div>"
    brand = ""
    if g("brand"):
        b = g("brand"); brand = '<div class="brand">%s<span class="tag">%s</span></div>' % (md(b.get("name", "")), md(b.get("tagline", "")))
    decos = "".join('<span class="deco" style="%s">%s</span>' % (d.get("style", ""), esc(d.get("text", ""))) for d in g("decor", []))
    body = render_rows(spec.get("rows", []))
    f = g("footer", {}); page = spec.get("page", defaults.get("page") if "pages" not in defaults else None)
    footer = ('<table class="footer"><tr><td style="width:36%%">%s</td><td style="text-align:center">%s</td><td style="width:36%%;text-align:right">%s</td></tr></table>'
              % (md(f.get("left", "")), ('<span class="pg">%s</span>' % md(page)) if page else "", md(f.get("right", "")))) if (f or page) else ""
    stick = g("stickies") if "stickies" in spec or "pages" not in defaults else spec.get("stickies")
    return '<div class="page %s%s">%s%s%s%s%s%s</div>' % (variant, " has-stickies" if stick else "", stickies_html(stick), decos, brand, t, body, footer)

def render(spec, fonts="embed"):
    pages = spec.get("pages") or [spec]
    body = "".join(render_page(p, spec) for p in pages)
    title = spec.get("title") or pages[0].get("title", "Notes")
    return ("<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>%s</title>%s<style>%s</style></head><body>%s</body></html>" % (esc(title), font_css(fonts), CSS, body))

def page_heights(png_path):
    """Heights of each .page in a PNG preview, found via the grey gutters between pages."""
    try:
        from PIL import Image
        import numpy as np
    except Exception:
        return []
    im = Image.open(png_path).convert("RGB"); a = np.array(im)
    grey = (np.abs(a.astype(int) - np.array([233, 236, 239])).sum(axis=2) < 12).all(axis=1)
    idx = np.where(grey)[0]
    if len(idx) == 0: return [a.shape[0]]
    runs, start, prev = [], idx[0], idx[0]
    for i in idx[1:]:
        if i != prev + 1: runs.append((start, prev)); start = i
        prev = i
    runs.append((start, prev))
    return [int(runs[i + 1][0] - runs[i][1] - 1) for i in range(len(runs) - 1) if runs[i + 1][0] - runs[i][1] > 40]

def find_chrome():
    """Locate a Chrome/Chromium/Edge binary for headless PDF export (macOS, Linux, Windows)."""
    cands = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge",
             "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Chromium.app/Contents/MacOS/Chromium",
             "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
             r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
             r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
             r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"]
    for c in cands:
        if os.path.sep in c or ":" in c:
            if os.path.exists(c): return c
        elif shutil.which(c): return shutil.which(c)
    return None


def fit_zoom(html_path):
    """Zoom so the tallest page fits one A4 sheet (printable height ≈ 1085px at 96dpi with 5mm margins)."""
    if not shutil.which("wkhtmltoimage"): return 0.9
    tmp = html_path.with_suffix(".fit.png")
    subprocess.run(["wkhtmltoimage", "-q", "--width", "860", "--enable-local-file-access", str(html_path), str(tmp)], check=False)
    hs = page_heights(tmp) if tmp.exists() else []
    if tmp.exists(): tmp.unlink()
    if not hs: return 0.9
    tallest = max(hs); zoom = min(1.0, 1085.0 / tallest)
    print("page heights (px at 800 wide):", hs, "→ tallest", tallest)
    return round(zoom, 3)

# ---------------------------------------------------------------- estimate (no browser needed)
PAGE_LIMIT = 1300           # px at 800 px wide; above this the page is dense (warning)
PAGE_HARD = 1400            # above this it will not fit one A4 sheet legibly (stop)
CODE_HALF, CODE_FULL = 50, 104

def _plain(t):
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", str(t))
    return re.sub(r"[*=`{}]", "", t)

def _lines(t, cpl): return max(1, math.ceil(len(_plain(t)) / max(8, cpl)))

def est_block(b, ncols):
    """Rough pixel height of one block at 800 px page width (calibrated on 30 rendered pages, ±8%)."""
    cpl = 50 if ncols >= 2 else 104
    lh = 19.5
    t = b.get("type", "bullets")
    h = 42 if (b.get("title") or b.get("n")) else 16
    if t in ("bullets", "checks", "stars", "numbered"):
        h += sum(_lines(i, cpl - 4) * lh for i in b.get("items", [])) + 6
        if b.get("note"): h += _lines(b["note"], cpl) * lh + 6
    elif t == "text":
        paras = b.get("text", ""); paras = [paras] if isinstance(paras, str) else paras
        h += sum(_lines(x, cpl) * lh + 6 for x in paras)
    elif t == "table":
        head = b.get("head", []); rows = b.get("rows", [])
        nc = max(1, len(head) or max((len(r) for r in rows), default=1))
        ccpl = max(8, int(cpl / nc) - 2)
        h += (28 if head else 0) + sum(max((_lines(c, ccpl) for c in r), default=1) * 22 + 5 for r in rows)
    elif t == "code":
        h += len(b.get("code", "").split("\n")) * 17 + 24 + (18 if b.get("caption") else 0)
    elif t == "chips":
        h += sum(max(1, _lines(it.get("desc", ""), cpl - 18)) * 24 + 6 for it in b.get("items", []))
    elif t == "kv":
        h += sum(_lines(it.get("v", ""), cpl - 14) * lh + 6 for it in b.get("items", []))
    elif t == "callout":
        h = 34 + _lines(b.get("text", ""), cpl - 2) * lh + 10
    elif t == "flow":
        steps = b.get("steps", []); per = 6 if ncols == 1 else 3
        h += math.ceil(len(steps) / per) * 58 + (18 if b.get("caption") else 0)
    elif t == "compare":
        side = lambda k: 24 + sum(_lines(i, int(cpl / 2) - 4) * lh for i in b.get(k, {}).get("items", []))
        h += max(side("left"), side("right")) + 8
    elif t == "revision":
        groups = b.get("groups") or [b.get("items", [])]; g_cpl = max(14, int(104 / max(1, len(groups))) - 5)
        h = 40 + max((sum(_lines(i, g_cpl) * lh for i in g) for g in groups), default=0) + 16
    elif t == "questions":
        groups = b.get("groups", []); g_cpl = max(14, int(cpl / max(1, len(groups))) - 5)
        h += max((30 + sum(_lines(q, g_cpl) * lh + 4 for q in g.get("items", [])) for g in groups), default=0) + 10
    elif t == "indexstrip":
        h += 96 + sum(_lines(i, cpl) * lh for i in b.get("examples", []))
    elif t == "stack":
        h += 30 + len(b.get("layers", [])) * 34 + (18 if b.get("caption") else 0)
    return h

def est_page(spec):
    h = 96 + (34 if spec.get("subtitle") else 0) + (30 if spec.get("tagline") else 0) + 60
    for row in spec.get("rows", []):
        cols = row.get("cols", []); n = max(1, len(cols))
        h += max((sum(est_block(b, n) for b in col) for col in cols), default=0) + 12
    return int(h * 0.96)   # calibrated: estimates run ~2–5% high, never low enough to hide an overflow

def code_warnings(spec, label):
    out = []
    for row in spec.get("rows", []):
        n = max(1, len(row.get("cols", [])))
        for col in row.get("cols", []):
            for b in col:
                if b.get("type") == "code":
                    lim = CODE_FULL if n == 1 else CODE_HALF
                    long = [l for l in b.get("code", "").split("\n") if len(l) > lim]
                    if long: out.append("%s: %d code line(s) longer than %d chars will wrap (%s...)" % (label, len(long), lim, long[0][:40]))
    return out

def estimate(spec):
    pages = spec.get("pages") or [spec]
    lines, worst = [], 0
    for i, pg in enumerate(pages):
        merged = dict(spec); merged.pop("pages", None); merged.update(pg)
        h = est_page(merged); worst = max(worst, h)
        label = merged.get("page") or ("page %d" % (i + 1))
        state = "OK" if h <= PAGE_LIMIT else ("DENSE: trim a few lines or it prints small" if h <= PAGE_HARD else "OVER by ~%d px: cut or split" % (h - PAGE_HARD))
        lines.append("%s: ~%d px %s" % (label, h, state))
        lines += code_warnings(merged, label)
    return lines, worst, len(pages)

# ---------------------------------------------------------------- pdf
def ensure_local_fonts():
    """Register the bundled fonts with fontconfig (Linux) so wkhtmltopdf embeds subsets instead of the full font per page."""
    if not shutil.which("fc-cache"): return False
    dest = Path.home() / ".local/share/fonts"
    try:
        dest.mkdir(parents=True, exist_ok=True); changed = False
        for f in FONT_DIR.glob("*.woff"):
            if not (dest / f.name).exists(): shutil.copy(f, dest / f.name); changed = True
        if changed: subprocess.run(["fc-cache", "-f"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def chrome_measure(chrome, html_path, timeout=60):
    """Exact .page heights via headless Chrome --dump-dom (fresh profile, so it cannot hang on a running Chrome)."""
    tmp = html_path.with_name(html_path.stem + ".measure.html")
    try:
        src = html_path.read_text(encoding="utf-8")
        inject = '<script>document.body.setAttribute("data-h",[...document.querySelectorAll(".page")].map(p=>p.offsetHeight).join(","))</script></body>'
        tmp.write_text(src.replace("</body>", inject, 1), encoding="utf-8")
        r = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=900,1200", "--virtual-time-budget=5000",
                            "--user-data-dir=" + tempfile.mkdtemp(), "--dump-dom", tmp.resolve().as_uri()],
                           capture_output=True, text=True, timeout=timeout)
        m = re.search(r'data-h="([^"]*)"', r.stdout)
        return [int(x) for x in m.group(1).split(",")] if m and m.group(1) else None
    except Exception:
        return None   # e.g. timeout: the caller falls back to the estimate
    finally:
        tmp.unlink(missing_ok=True)   # never leave the temp file next to the deliverables

def chrome_print(chrome, html_path, pdf, timeout=120):
    """Print with headless Chrome. It sometimes writes the PDF and never exits, so wait for the file to settle, then stop it."""
    import time
    if pdf.exists(): pdf.unlink()
    proc = subprocess.Popen([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--user-data-dir=" + tempfile.mkdtemp(),
                             "--print-to-pdf=" + str(pdf.resolve()), html_path.resolve().as_uri()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import time as _t
    last, deadline = -1, _t.time() + timeout
    while _t.time() < deadline and proc.poll() is None:
        _t.sleep(2)
        size = pdf.stat().st_size if pdf.exists() else -1
        if size > 0 and size == last: break
        last = size
    if proc.poll() is None: proc.kill()
    return pdf.exists() and pdf.stat().st_size > 0


def pdf_page_count(pdf):
    try:
        data = pdf.read_bytes()
        n = len(re.findall(rb"/Type\s*/Page[^s]", data))
        return n or None
    except Exception:
        return None

def make_pdf(spec, out_html, pdf, fonts, expected_pages):
    """Write pdf from spec. Returns (engine, pages) or (None, None)."""
    engine = "wkhtmltopdf" if shutil.which("wkhtmltopdf") else ("chrome" if find_chrome() else None)
    if not engine: return None, None
    local_fonts = engine == "wkhtmltopdf" and ensure_local_fonts()
    pages = spec.get("pages") or [spec]
    ests = []
    for pg in pages:
        merged = dict(spec); merged.pop("pages", None); merged.update(pg); ests.append(est_page(merged))
    if engine == "chrome":
        # Chrome maps CSS px straight onto paper: keep the page 800 px wide and zoom the body so the tallest page fits A4 (733 x 1040 px printable at 8 mm margins).
        chrome = find_chrome()
        tmp = out_html.with_name(out_html.stem + ".print.html")
        tmp.write_text(render(spec, fonts), encoding="utf-8")
        hs = chrome_measure(chrome, tmp) or ests
        zoom = min(733 / 800, 1040 / max(max(hs), 1))
        extra = "<style>@page{size:A4 portrait;margin:8mm}@media print{body{zoom:%.3f}.page{width:800px!important;margin:0 auto!important}}</style>" % zoom
        tmp.write_text(tmp.read_text(encoding="utf-8").replace("</head>", extra + "</head>", 1), encoding="utf-8")
        ok = chrome_print(chrome, tmp, pdf)
        tmp.unlink(missing_ok=True)
        if not ok: return None, None
        n = pdf_page_count(pdf)
        return engine, n
    zooms = [min(1.22, 1.22 * 1100 / max(1, h)) for h in ests]
    for attempt in range(2):
        tmp = out_html.with_name(out_html.stem + ".print.html")
        extra = "<style media=\"print\">.page{width:100%%!important}%s</style>" % "".join(".page:nth-of-type(%d){zoom:%.3f}" % (i + 1, zz) for i, zz in enumerate(zooms))
        tmp.write_text(render(spec, "system" if local_fonts else fonts).replace("</head>", extra + "</head>", 1), encoding="utf-8")
        subprocess.run(["wkhtmltopdf", "-q", "--page-size", "A4", "--margin-top", "5mm", "--margin-bottom", "5mm", "--margin-left", "5mm", "--margin-right", "5mm",
                        "--enable-local-file-access", "--print-media-type", str(tmp), str(pdf)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tmp.unlink(missing_ok=True)
        n = pdf_page_count(pdf) if pdf.exists() else None
        if n is None or n <= expected_pages: return engine, n
        zooms = [zz * 0.9 for zz in zooms]   # a page spilled over: shrink once and retry
    return engine, n

def main():
    args = sys.argv[1:]
    if len(args) < 2: raise SystemExit(__doc__)
    src, out = Path(args[0]), Path(args[1])
    fonts = "link" if "--fonts" in args and args[args.index("--fonts") + 1] == "link" else "embed"
    spec = json.loads(src.read_text(encoding="utf-8"))
    lines, worst, npages = estimate(spec)
    if "--estimate" in args:
        print("\n".join(lines)); return
    warn = [l for l in lines if "wrap" in l or "DENSE" in l]
    if warn: print("\n".join(warn))
    if any("OVER" in l for l in lines) and "--force" not in args:
        print("\n".join(l for l in lines if "px" in l)); raise SystemExit("A page is too tall for one A4 sheet: shorten or split it (or pass --force).")
    out.parent.mkdir(parents=True, exist_ok=True)
    pdf_only = "--pdf-only" in args
    want_pdf = "--pdf" in args or pdf_only
    out.write_text(render(spec, fonts), encoding="utf-8")
    if want_pdf:
        pdf = out.with_suffix(".pdf")
        engine, n = make_pdf(spec, out, pdf, fonts, npages)
        if engine and pdf.exists():
            print("wrote %s (%d KB, %s page(s), %s)" % (pdf, pdf.stat().st_size // 1024, n if n else "?", engine))
            if pdf_only: out.unlink(missing_ok=True)
            elif not pdf_only: print("wrote", out)
            if n and n > npages: print("WARNING: %d PDF pages for %d note page(s); a page spilled over. Shorten the longest page." % (n, npages))
        else:
            print("No PDF engine (wkhtmltopdf or Chrome) found; delivering the HTML instead:", out, "(open in a browser and print to A4 with background graphics on).")
    else:
        print("wrote", out, "(%d KB)" % (out.stat().st_size // 1024))
    if "--png" in args:
        if shutil.which("wkhtmltoimage"):
            png = out.with_suffix(".png")
            subprocess.run(["wkhtmltoimage", "-q", "--width", "860", "--enable-local-file-access", str(out), str(png)], check=False)
            print("wrote", png)
        else:
            print("wkhtmltoimage not found: skip PNG preview.")

if __name__ == "__main__":
    main()
