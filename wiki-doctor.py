#!/usr/bin/env python3
"""wiki-doctor — the linter for agent knowledge bases.

Your agents read your markdown wiki. Nobody lints it. This checks:

- broken [[wikilinks]] (code-span-aware: skips ``` fences and `inline code`)
- orphan pages (no other page links to them)
- stale `Last synced:` stamps (>30 days)

Usage:
    wiki-doctor.py path/to/wiki     # human report on stdout
    wiki-doctor.py --json path/     # machine-readable
    wiki-doctor.py --no-orphans --no-stale path/   # links only

Exit 0 = clean, 1 = problems found. Report-only: mutates nothing.

Lineage: adapted from the link-integrity checker that keeps a 30-file,
186-wikilink production Obsidian vault at zero broken links
(empire-mind estate vault). Generalized here: the vault path is now an
argument, orphan detection added, JSON output added.
"""
import argparse
import datetime
import json
import os
import re
import sys

LINK_RE = re.compile(r"\[\[([^|\]#]+)(?:#[^|\]]*)?(?:\|[^\]]*)?\]\]")
STAMP_RE = re.compile(r">\s*Last synced:\s*(\d{4}-\d{2}-\d{2})")
STALE_DAYS = 30


def strip_code_spans(text):
    text = text.replace("\\|", "|")
    out = []
    in_fence = False
    for line in text.splitlines(True):
        if line.startswith("```"):
            in_fence = not in_fence
            out.append("\n" * line.count("\n"))
            continue
        if in_fence:
            out.append("\n" * line.count("\n"))
            continue
        kept = "".join(line.split("`")[::2])
        out.append(kept)
    return "".join(out)


def collect_notes(root):
    notes = {}   # lowercase basename -> relpath
    files = []
    inbound = {}  # basename -> set of relpaths linking to it
    for dirpath, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".md"):
                p = os.path.join(dirpath, f)
                rel = os.path.relpath(p, root)
                files.append(p)
                bn = f[:-3].lower()
                notes[bn] = rel
                inbound.setdefault(bn, set())
    return notes, files, inbound


def check(root):
    notes, files, inbound = collect_notes(root)
    broken, stale = [], []
    today = datetime.date.today()
    for path in files:
        with open(path, encoding="utf-8") as fh:
            text = strip_code_spans(fh.read())
        rel = os.path.relpath(path, root)
        self_bn = os.path.basename(path)[:-3].lower()
        for m in LINK_RE.finditer(text):
            target = m.group(1).strip()
            if "/" in target:
                base = os.path.normpath(os.path.join(os.path.dirname(path), target))
                if os.path.isdir(base):
                    continue
                if os.path.isfile(base + ".md"):
                    continue
                bn = os.path.basename(target).lower()
                if bn in notes:
                    inbound[bn].add(rel)
                    continue
                broken.append((rel, m.group(0), "path-target-missing"))
            else:
                bn = target.lower()
                if bn in notes:
                    if bn != self_bn:
                        inbound[bn].add(rel)
                    continue
                broken.append((rel, m.group(0), "note-not-found"))
        sm = STAMP_RE.search(text)
        if sm:
            d = datetime.date.fromisoformat(sm.group(1))
            age = (today - d).days
            if age > STALE_DAYS:
                stale.append((rel, sm.group(1), age))
    orphans = sorted(rel for bn, rel in notes.items()
                     if not inbound[bn] and bn != "index")
    return {"files": len(files), "notes": len(notes),
            "broken": broken, "stale": stale, "orphans": orphans}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="wiki-doctor",
                                 description="lint an agent-readable markdown wiki")
    ap.add_argument("path", help="wiki root directory")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-orphans", action="store_true")
    ap.add_argument("--no-stale", action="store_true")
    args = ap.parse_args(argv)

    root = os.path.abspath(os.path.expanduser(args.path))
    if not os.path.isdir(root):
        print(f"wiki-doctor: not a directory: {args.path}", file=sys.stderr)
        return 2
    r = check(root)
    if args.no_orphans:
        r["orphans"] = []
    if args.no_stale:
        r["stale"] = []
    problems = bool(r["broken"] or r["stale"] or r["orphans"])

    if args.json:
        print(json.dumps({
            "files": r["files"], "notes": r["notes"],
            "broken": [{"file": f, "link": l, "why": w} for f, l, w in r["broken"]],
            "stale": [{"file": f, "stamp": s, "age_days": a} for f, s, a in r["stale"]],
            "orphans": r["orphans"]}, indent=2))
    else:
        print(f"files={r['files']} notes={r['notes']}")
        if r["broken"]:
            print(f"BROKEN={len(r['broken'])}")
            for rel, link, why in r["broken"][:50]:
                print(f"  {rel} :: {link} ({why})")
        if r["stale"]:
            print(f"STALE_STAMPS={len(r['stale'])} (>{STALE_DAYS}d)")
            for rel, stamp, age in r["stale"][:50]:
                print(f"  {rel} :: {stamp} ({age}d)")
        if r["orphans"]:
            print(f"ORPHANS={len(r['orphans'])}")
            for rel in r["orphans"][:50]:
                print(f"  {rel}")
        if not problems:
            print("CLEAN")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
