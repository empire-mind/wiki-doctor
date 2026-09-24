# Getting started

1. Fork this template (or copy the `template/` directory).
2. Write pages. Link them from [[MOC]].
3. Run the lint:

```bash
python3 /path/to/wiki-doctor.py .
```

4. Keep it green. The CI workflow (`.github/workflows/lint.yml` in the
   wiki-doctor repo — copy it into yours) runs the same check on every PR.

See [[linking-rules]] for the conventions that keep the lint passing.
