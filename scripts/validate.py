#!/usr/bin/env python3
"""Validate skills against the Agent Skills spec (agentskills.io/specification) and the marketplace catalog.

    python3 scripts/validate.py              every skill in skills/ + .claude-plugin/marketplace.json
    python3 scripts/validate.py visual-notes one skill (catalog is still checked for it)

Standard library only, so it runs the same locally and in CI.
"""
import json, pathlib, py_compile, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
CATALOG = ROOT / ".claude-plugin" / "marketplace.json"
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def frontmatter(text):
    """Return top-level frontmatter keys -> raw values, or raise if the block is malformed."""
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with a '---' line")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("frontmatter has no closing '---' line")
    fields = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue  # blank, nested (metadata:) or comment
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if not m:
            raise ValueError("frontmatter line is not 'key: value': %r" % line[:60])
        key, value = m.group(1), m.group(2).strip()
        # strict YAML parsers (e.g. the `skills` CLI) reject these in plain scalars; Claude tolerates them
        if value and value[0] not in "'\"|>" and (": " in value or " #" in value):
            raise ValueError("%s contains ': ' or ' #'; wrap the value in single quotes" % key)
        fields[key] = value.strip("\"'")
    return fields


def check_skill(d):
    errs = []
    md = d / "SKILL.md"
    if not md.is_file():
        return ["missing SKILL.md"]
    text = md.read_text(encoding="utf-8")
    try:
        fm = frontmatter(text)
    except ValueError as e:
        return [str(e)]
    extra = set(fm) - ALLOWED_KEYS
    if extra:
        errs.append("frontmatter keys outside the spec: %s" % sorted(extra))
    name, desc = fm.get("name", ""), fm.get("description", "")
    if not NAME_RE.match(name) or len(name) > 64:
        errs.append("name %r must be 1-64 chars of a-z, 0-9 and single hyphens" % name)
    if name != d.name:
        errs.append("name %r must match its folder %r" % (name, d.name))
    if not 1 <= len(desc) <= 1024:
        errs.append("description must be 1-1024 chars (is %d)" % len(desc))
    if "compatibility" in fm and not 1 <= len(fm["compatibility"]) <= 500:
        errs.append("compatibility must be 1-500 chars")
    lines = text.count("\n")
    if lines > 500:
        errs.append("SKILL.md is %d lines; the spec recommends under 500" % lines)
    for py in d.rglob("*.py"):
        try:
            py_compile.compile(str(py), cfile=None, doraise=True)
        except py_compile.PyCompileError as e:
            errs.append("does not compile: %s" % e.msg.strip().splitlines()[-1])
    for pyc in d.rglob("__pycache__"):
        for f in pyc.iterdir():
            f.unlink()
        pyc.rmdir()
    return errs


def check_catalog(names):
    try:
        cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return ["marketplace.json: %s" % e]
    errs, listed = [], {}
    for p in cat.get("plugins", []):
        src = p.get("source")
        if not isinstance(src, str):
            continue  # remote source (github, url, npm): nothing local to check
        # either "source": "./skills/<name>" (one skill per plugin) or a "skills" list under the source
        for s in p.get("skills") or ["."]:
            d = (ROOT / src / s).resolve()
            listed[d.name] = p.get("name")
            if not (d / "SKILL.md").is_file():
                errs.append("marketplace.json: plugin %r points at %s, which has no SKILL.md" % (p.get("name"), d.relative_to(ROOT)))
            elif "skills" not in p and p.get("name") != d.name:
                errs.append("marketplace.json: plugin %r should be named after its skill %r" % (p.get("name"), d.name))
    for n in names:
        if n not in listed:
            errs.append("marketplace.json: skill %r is not listed in any plugin" % n)
    return errs


def main():
    wanted = sys.argv[1:]
    dirs = [SKILLS / n for n in wanted] if wanted else sorted(p for p in SKILLS.iterdir() if p.is_dir())
    failed = False
    for d in dirs:
        errs = check_skill(d) if d.is_dir() else ["no such skill folder: %s" % d.relative_to(ROOT)]
        print(("FAIL " if errs else "ok   ") + d.name)
        for e in errs:
            print("     - " + e)
        failed |= bool(errs)
    errs = check_catalog([d.name for d in dirs])
    print(("FAIL " if errs else "ok   ") + "marketplace.json")
    for e in errs:
        print("     - " + e)
    sys.exit(1 if failed or errs else 0)


if __name__ == "__main__":
    main()
