# SQL content

As of v3.10, the SQL source markdown lives here in the same shape as
`src/content/python/` and `src/content/javascript/` — `cheatsheet.md` plus
`tier-{introductory,amateur,intermediate,experienced,master}.md`. The build
pipeline treats all three tracks identically.

## Reconstruction history

v3.9 carried the SQL portion of the embedded `CONTENT_BUNDLE` forward
byte-for-byte from v3.8b's pre-rendered output because the original `.md`
sources were not available during the v3.9 sprint. v3.10 reverse-converted
the v3.9 ANSI strings back to markdown using `.work/reconstruct_sql.py`,
emitted directly in the new `<<tag>>...<</tag>>` syntax (skipping the
intermediate legacy form).

The reconstructed source rebuilds to a SQL bundle byte-identical to v3.9.
The HTML for the SQL cheatsheet is regenerated from the reconstructed
markdown by `build.py`; we did not roundtrip from v3.9's embedded HTML.

If you ever need to redo the reconstruction (e.g. for a different fork,
or to validate a future bundle change), the script is at
`.work/reconstruct_sql.py` in the repo. It reads from a cached
`.work/sql.v39.json` (the SQL slice of v3.9's bundle) and writes
markdown files into this directory.
