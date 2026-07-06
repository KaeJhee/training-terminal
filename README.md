# Ghost Training Terminal

![version](https://img.shields.io/badge/version-v4.0.3-e8a020?style=flat-square)
![tracks](https://img.shields.io/badge/tracks-SQL%20%7C%20Python%20%7C%20JavaScript%20%7C%20Rust-3cb8c0?style=flat-square)
![tier system](https://img.shields.io/badge/tiers-5-3ab86e?style=flat-square)

A self-hosted, browser-based training terminal for SQL, Python, JavaScript,
and Rust practice. Five tiers per track, ten gating questions per tier, real
query execution against an embedded SQLite database (sql.js), Pyodide for
Python, and a sandboxed Web Worker for JavaScript — plus a pattern-match
grader for Rust, the first track graded without in-browser execution.
Progress persists in `localStorage`. Bloomberg-style multi-panel layout with
a learning layer in the right rail.

## What's new in v4.0

**Rust** joins as the fourth track — and the first graded by pattern-matching
instead of execution. There's no Rust runtime in the browser; a `RustEngine`
normalizes your submission and compares it against a canonical structure, with
an alternatives mechanic that accepts equivalent forms (e.g. `|&w|` vs
`|w| *w`) and grammar-lite feedback that names the specific mistake ("binding
needs `mut`", "wrong borrow syntax", "missing `;`") rather than a bare
"incorrect."

- **50 graded questions across five tiers**, from `let`/`mut` bindings and
  lowercase booleans up through a dot-product forward-pass capstone. The ramp
  covers ownership and borrowing, iterators and closures, traits / generics /
  lifetimes-in-context, and async / unsafe / FFI / smart pointers.
- **A full learning-content tree** — a whole-language cheatsheet plus per-tier
  concepts and worked examples, with ASCII diagrams for the ownership model
  (move invalidation, `&T` vs `&mut T`, the borrow checker's reader-XOR-writer
  rule).
- **`start rust`** is wired through the UI alongside the other three tracks:
  KPI rollups, the left-rail tier ladder, the ticker, and progress
  persistence all include Rust.
- The pattern-match grader built for a 10-question slice graded the full
  50-question bank **without a single change** — validating the approach for
  the C++/CUDA tracks it's designed to extend to.

See `CHANGELOG.md` for the build-artifact md5 and the per-track bundle audit.

## What was new in v3.10

Consolidation pass between v3.9 and v4.0. No new tracks, no new questions, no
new features — pure cleanup of technical debt that would have made Rust
authoring (v4.0) harder than it needed to be:

- **New tag syntax** `<<amber>>...<</amber>>` replaces the legacy
  `[amber]...[/]` form across every content file. The legacy form's
  `[a-z]{3,}` open-tag regex collided with code identifiers — `[prop]`,
  `[key]`, `[idx]` were already dodged in v3.9 with single-letter renames,
  and Rust would hit the same problem immediately with `[ref]`, `[mut]`,
  `[box]`, `[Vec]`, `[Option]`, `[Result]`. The new `<<…>>` form has no
  overlap with any planned-track syntax and uses an explicit named closer.
- **`build.py --migrate-tags`** — one-shot tool that walks every content
  file under `src/content/` and rewrites legacy syntax to the new form
  using a tag stack so `[/]` becomes the correctly-named `<</tag>>`.
  Already run once for v3.10; preserved in the source for any future
  fork or contributor still on legacy syntax.
- **SQL source markdown reconstructed** under `src/content/sql/`. v3.9
  shipped with the SQL bundle carried forward byte-for-byte from v3.8b
  because the original `.md` source files were lost; v3.10 reverse-converts
  the v3.9 bundle's ANSI strings back to markdown (in the new `<<tag>>`
  syntax directly). Verified by rebuilding and matching the v3.9 SQL bundle
  md5 exactly. The build pipeline is now symmetric across all three tracks.
- **JS Intermediate-tier ML calibration.** Q26 (Promise.all), Q27
  (Object.values), and Q29 (try/catch) were reframed for ML-adjacency —
  parallel checkpoint fetches, per-class accuracy counts, and async error
  handling around invalid logits. Same JS skill tested in each; framing
  brings the tier from v3.9's actual 60/0/40 ratio toward the 30/30/40 target.
- **Q47 redesigned** as `delayed_increment(start)` — a single free function
  instead of v3.9's two-part contract (define a Counter method *and* bind
  `next_value` at top level). The lexical-scope-in-callbacks lesson stays
  the same family: a regular function inside `.then` whose parameter is
  named `start` shadows the outer-scope `start`, and since
  `Promise.resolve()` with no argument resolves to undefined, you get NaN.
  An arrow function with no parameter closes over the outer `start`
  cleanly.

The post-migration bundle is **semantically identical** to v3.9 for any
content that wasn't a Task 3 or Task 4 target. It is **not byte-identical**
to v3.9 because the tag-open byte sequences differ; the SQL slice happens
to remain byte-identical because the reconstructed source rebuilds to the
same ANSI/HTML output. See `CHANGELOG.md` for the per-track md5 audit trail.

## What was new in v3.9

JavaScript joined SQL and Python as the third track:

- 50 graded questions across five tiers, scaling from variable bindings up
  through a semantic-search capstone (cosine-similarity over an embedding
  matrix, top-k retrieval).
- A new in-browser execution engine (`JsEngine`) that runs each grading
  round in a fresh Web Worker spun up from a Blob URL. Each worker is
  sandboxed at boot — network APIs (`fetch`, `XMLHttpRequest`, `WebSocket`,
  `EventSource`, `importScripts`, `BroadcastChannel`), persistent storage
  (`indexedDB`, `Cache`, `caches`), and `Notification` are deleted before
  user code runs. Execution is capped at 3000ms per question, with an
  outer 8000ms walltime.
- A new `approx` assertion type for floating-point ML primitives like
  softmax and cosine similarity. Required `tol` parameter (no default) plus
  optional `forbidden:[...]` companion field for "implement X without Y"
  questions.
- A whole-language cheatsheet plus per-tier concepts and worked examples,
  consistent with the SQL and Python content shape.
- The build pipeline gained a `globalThis.<api>`-deletion lint that scans
  fenced code blocks in JS content for references to sandbox-deleted APIs,
  preventing examples that would throw when the user tried to run them.

See `CHANGELOG.md` for the full change list.

## Layout

```
ghost-training/
├── index.html                     # build artifact — open this in a browser
├── build.py                       # markdown → ANSI/HTML bundler
├── CHANGELOG.md
├── README.md
└── src/
    ├── index.template.html        # HTML/CSS/JS scaffold with content placeholder
    └── content/
        ├── sql/                   # reconstructed in v3.10
        │   ├── README.md
        │   ├── cheatsheet.md
        │   ├── tier-introductory.md
        │   ├── tier-amateur.md
        │   ├── tier-intermediate.md
        │   ├── tier-experienced.md
        │   └── tier-master.md
        ├── python/
        │   └── (same structure)
        └── javascript/
            └── (same structure)
```

## Building

`build.py` reads the markdown content, parses inline `<<tag>>...<</tag>>`
color tags, splits tier files on the `---` divider into a concepts section
plus an examples array, and concatenates everything into `index.html` via
the template.

```bash
python3 build.py                # build (writes index.html, prints summary)
python3 build.py --check        # lint only (no write); exit 1 on warnings
python3 build.py --migrate-tags # rewrite legacy [tag] syntax to <<tag>> in place
```

The lint pass catches:
- unclosed `<<tag>>...<</tag>>` pairs at EOF
- named-closer mismatches (e.g. `<<amber>>foo<</dim>>`)
- unknown tag names (anything outside `bold|amber|teal|green|blue|purple|red|dim`)
- `<<qid:...>>` references that don't match any id in the question bank
- code blocks longer than 15 lines (soft warning)
- legacy `[tag]` syntax (configurable severity via `TAG_LEGACY_MODE` in
  `build.py`; defaults to `"error"` since v3.10)
- in JS content, code-block references to sandbox-deleted APIs
  (`globalThis.fetch`, etc.)

`index.html` is a single-file artifact. No bundler, no node_modules. Open it
directly or serve with `python3 -m http.server`.

## Markdown format

```markdown
# SECTION HEADER

  Two-space-indent prose. Inline color tags: <<amber>>SELECT<</amber>>,
  <<dim>>aside<</dim>>, <<bold>>emphasis<</bold>>. Question references:
  <<qid:sql_intro_03>> (clickable in the panel).

      Four-space-indent code. Auto-grouped into one [pre] block.
      <<amber>>SELECT<</amber>> * <<amber>>FROM<</amber>> customers;

  Tags can <<dim>>span across
  multiple lines

  with paragraph breaks in between, then close here.<</dim>>
```

For tier files, a `---` line divides the concepts section above from the
examples section below. Each example is a `# EXAMPLE N` heading.

## Authoring conventions

- Voice is direct, no padding. Explain "why" after the "what."
- Each tier's last example previews a concept from the next tier.
- Examples never duplicate the graded questions — they teach with adjacent
  problems so submitting an exact-match answer doesn't pass.
- Cheatsheets are whole-language references, not per-tier.
- ML-adjacent framing is welcome ("classification thresholds," "training loop
  intuition") but no question requires ML knowledge.
- Use `<<tag>>` syntax. The legacy `[tag]` form is rejected by the build as
  of v3.10. If you find yourself maintaining a fork still on legacy syntax,
  run `python3 build.py --migrate-tags` once to convert in place.
- Closers are named: `<<amber>>SELECT<</amber>>`, not `<<amber>>SELECT<</>>`.
  The named form catches mistakes (mismatched closer = lint failure) and is
  what the parser expects.

## Versioning

Loose SemVer with patch-style letters (e.g. `v3.8a`, `v3.8b`) when a
milestone splits across releases that must ship together. Each shipped
version updates the version string in five places:

1. Footer line in `src/index.template.html`
2. Mobile boot banner in app JS
3. Desktop boot banner in app JS
4. README badge (this file)
5. `CHANGELOG.md` entry

## Note on AI-assisted authoring

Drafts of the markdown content files in `src/content/` were produced with AI
assistance and human-edited before commit. The voice and the technical
calls are mine; the AI handled first drafts and structure.

— Ghost Strategies LLC
