# wiki-doctor — the linter for agent knowledge bases

Your agents read your markdown wiki. Nobody lints it. `wiki-doctor check`
finds broken `[[wikilinks]]`, orphan pages, and stale claims — and ships
the forkable template for **the wiki your agents actually read**.

## 60-second demo

```bash
curl -o wiki-doctor.py https://raw.githubusercontent.com/empire-mind/wiki-doctor/main/wiki-doctor.py
python3 wiki-doctor.py examples/my-wiki
```

```
files=4 notes=4
BROKEN=1
  index.md :: [[ghost-page]] (note-not-found)
STALE_STAMPS=1 (>30d)
  old.md :: 2020-01-01 (2458d)
ORPHANS=2
  old.md
  scratch.md
```

Exit `0` = clean, `1` = problems found. Report-only — it never modifies
your wiki.

## What it checks

- **Broken wikilinks** — `[[page]]`, `[[page#section]]`, `[[page|display]]`,
  and relative-path links. Code-span-aware: text inside ``` fences and
  `inline code` is ignored, so your code samples don't break the build.
- **Orphans** — pages no other page links to (`index.md` exempt — it's
  the front door). Orphans rot silently; now they don't.
- **Stale stamps** — a `> Last synced: YYYY-MM-DD` stamp older than 30
  days is flagged, so agents stop trusting outdated claims.

## The template

`template/` is the forkable wiki: `index.md` front door, `MOC.md` map of
content, append-only `log.md`, `topics/` with linking rules. Copy it, run
the linter, keep the badge green. The conventions in
`template/topics/linking-rules.md` are exactly what the linter enforces —
no surprises.

## CI for your agent's brain

```yaml
# .github/workflows/lint.yml in your wiki repo
- run: python3 wiki-doctor.py .
```

One command, one badge. Dogfooded: this checker (in an earlier form) keeps
a 30-file, 186-wikilink production vault at zero broken links.

## Honest limits

- Link resolution is by note basename (case-insensitive), Obsidian-style —
  not by full path. When two notes share a basename the link still
  resolves first-match, but the collision is reported under
  `DUPLICATE_BASENAMES` so the shadow copy can't stay hidden.
- The stale-claim check is stamp-based, not semantic: it can't tell you
  two pages *contradict* each other. That detector is the research
  roadmap — see the `help wanted` issues.
- Speed target: under 5 seconds on a 500-page wiki (it's a single
  `os.walk` + regex pass).

## Development

```bash
python3 -m pytest tests/    # 19 tests, offline, stdlib + pytest only
```

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Contributing

**Every issue and external PR gets a first response within 7 calendar
days.** `good first issue` items are scoped for one evening — the orphan
detector edge cases and new lint rules are great starts. Full funnel in
[CONTRIBUTING.md](CONTRIBUTING.md). Security issues: see the org
[SECURITY.md](https://github.com/empire-mind/.github/blob/main/SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).
