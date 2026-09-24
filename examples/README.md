# examples/my-wiki — the demo with all three finding classes

```bash
python3 ../../wiki-doctor.py my-wiki
```

Expected (verify, or open a bug):

- `BROKEN=1` — `index.md :: [[ghost-page]]` (note-not-found). Note that
  `[[not-a-real-link]]` inside the fenced code block and
  `[[also-ignored]]` in inline code in `guide.md` are *not* flagged.
- `STALE_STAMPS=1` — `old.md` carries `> Last synced: 2020-01-01`.
- `ORPHANS=2` — `scratch.md` and `old.md` have no inbound links.

Compare with `python3 ../../wiki-doctor.py ../../template` → CLEAN.
