# Linking rules

- `[[page-name]]` resolves by note basename, case-insensitive.
- `[[page#section]]` and `[[page|display text]]` also work.
- Links inside ``` fenced code blocks and `inline code` are ignored.
- `index.md` is exempt from the orphan check (it's the front door —
  nothing needs to link *to* it).
- A `> Last synced: YYYY-MM-DD` stamp older than 30 days is flagged.
