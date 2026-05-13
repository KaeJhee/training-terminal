# Changelog

All notable changes to Ghost Training Terminal are documented here.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

Next milestone is v4.0 (Rust track). v3.10 cleared the structural prerequisites — symmetric build pipeline across all three tracks, tag syntax that doesn't collide with Rust identifiers, and the Q47 / Intermediate-tier calibration items. Authoring v4.0 against this base is straightforward.

- **v4.0** — Rust track (pattern-match + learning content). Authoring against `<<tag>>` syntax. Build pipeline already produces SQL/Python/JS bundles symmetrically.
- **v4.1** — C++ track + CUDA specialization (pattern-match + learning content).

---

## [v3.10] — 2026-05-06

Consolidation pass between v3.9 and v4.0. Pure technical-debt cleanup — no new tracks, questions, or features. The four items below were planned in v3.9's `[Unreleased]` section as prerequisites for Rust authoring; all four are done and verified.

### Build artifact

- **`index.html`** md5: `7f55f5c1045b0068a378d58b79b23478`
- **size:** 375,635 bytes (vs v3.9's 374,334; +1,301 bytes from version-string changes, four question rewrites, and the SQL bundle being rebuilt from source rather than overlaid)
- **build pipeline:** Symmetric across all three tracks. `build.py` reads `src/content/{sql,python,javascript}/*.md` and concatenates into `index.html` via `src/index.template.html`. The v3.9 two-step "build then overlay SQL bytes from v3.8b" workflow is gone.

### Per-track bundle audit (vs v3.9 reference)

| Track | v3.10 md5 | v3.9 reference | Status |
|---|---|---|---|
| sql | `aeeb91131bf238fb34e6cacd0c949390` | `aeeb91131bf238fb34e6cacd0c949390` | byte-identical (reconstructed from ANSI → markdown, rebuilds cleanly to v3.9 bytes) |
| python | `7e7270968e5d7ca25f919f03c76aa828` | `7e7270968e5d7ca25f919f03c76aa828` | byte-identical (only the source markdown's tag-token bytes changed; rendered ANSI/HTML output is unchanged) |
| javascript | `f28fcdd26a2a6aacf321ba6569fdfff5` | `f28fcdd26a2a6aacf321ba6569fdfff5` | byte-identical (same — content bundle is cheatsheet + tier prose + examples, not the question array; question reframings live in template body) |

The full `index.html` md5 differs from v3.9 because Q26/27/29/47's prompt strings and Q47's setup live in the template's `QUESTIONS.javascript` array, which is template body outside the content placeholder. The track content bundles themselves are unchanged byte-for-byte.

### Added

- **`build.py --migrate-tags`** — one-shot migration tool that walks every content file under `src/content/` and rewrites legacy `[tag]...[/]` syntax to `<<tag>>...<</tag>>` in place, using a tag stack so legacy `[/]` closers get rewritten to the correct named `<</tag>>` closer. Idempotent; preserved in source for any future fork or contributor still on legacy syntax. Used once for v3.10's migration: 12 files, 2,586 tag tokens rewritten total.
- **`TAG_LEGACY_MODE` config** at the top of `build.py` (`"warn" | "error" | "off"`). Set to `"error"` as of v3.10 ship — anyone slipping back to legacy syntax now gets an immediate build failure.
- **`warn_legacy_tag_usage` lint** — scans every content file for legacy `[tag]` opens, `[/]` closes, and `[qid:...]` refs. Per-file finding cap of one to keep the report short during migration.
- **Dual-syntax inline parser** in `build.py`. Recognizes both legacy and v3.10 tokens during the migration window. After cutover (with `TAG_LEGACY_MODE = "error"`) the parser still handles legacy syntax mechanically, but the lint blocks any build that tries to use it.
- **Named-closer mismatch detection.** `<<amber>>foo<</dim>>` is now a structural error; the v3.10 closer carries the tag name explicitly so the parser can validate it. (Legacy `[/]` was anonymous, so this class of bug couldn't be detected.)

### Changed

- **Tag syntax** migrated across every content file. `[amber]...[/]` → `<<amber>>...<</amber>>`. Legacy `[a-z]{3,}` regex collided with code identifiers; the new `<<...>>` form has no overlap with any planned-track syntax. The lossy v3.9 workaround of using single-letter names in code examples (`p` instead of `prop` in Proxy traps) is no longer needed.
- **SQL source markdown reconstructed.** `.work/reconstruct_sql.py` walks the v3.9 SQL bundle's ANSI strings and emits markdown directly in `<<tag>>` syntax (skipping the legacy intermediate). Cheatsheet + 5 tier files. The reconstructed source rebuilds to a SQL bundle byte-identical to v3.9.
- **Q26 (`js_int_06`) reframed for ML-adjacency.** "Three async functions fetch_a/b/c" → "fetch_checkpoint_a/b/c", "their sum" → "total size in MB". Same Promise.all + destructure + sum skill; same numbers (10+20+30=60); binding renamed `total` → `total_mb`.
- **Q27 (`js_int_07`) reframed for ML-adjacency.** `status_counts` (Open/Closed/InProgress/OnHold) → `class_correct` (cat/dog/fish/bird). Same Object.values + reduce skill; same total (22); binding renamed `total_orders` → `total_correct`.
- **Q29 (`js_int_09`) reframed for ML-adjacency.** "Parse JSON for `count` property" → "await `predict_logits(input)` and return max logit, or null on rejection / NaN value". Same try/catch + validate-result + return-null pattern, now exercised against an async source and a numerical-instability case. Test cases cover happy path, Promise rejection, NaN in array, and a valid negative-logit case (so users don't accidentally filter on positive only).
- **Q47 (`js_mas_07`) redesigned.** v3.9's two-part contract (define `Counter.prototype.tick` AND bind `next_value` at top level) collapsed to a single free function `delayed_increment(start)`. Same lexical-scope-in-callbacks lesson, different angle: a regular `function(start) { return start + 1; }` inside `.then` shadows the outer-scope `start` with its own parameter, and since `Promise.resolve()` with no argument resolves to `undefined`, you get `NaN`. An arrow function with no parameter closes over the outer `start` cleanly. Smoke test verifies the gotcha: the documented naive implementation actually produces `NaN` as the prompt claims.
- **Version bumped** v3.9 → v3.10 in five places: `src/index.template.html` footer, mobile boot banner, desktop boot banner, `CONTENT BUNDLE` comment, and `README.md` badge.

### Fixed

- **Legacy `[a-z]{3,}` regex collisions** with code identifiers — addressed structurally by the syntax migration. v3.9 worked around `[prop]`, `[key]`, `[idx]` in JS Master content with single-letter renames; those workarounds are no longer necessary. Rust authoring will not hit the same problem with `[ref]`, `[mut]`, `[box]`, `[Vec]`, `[Option]`, `[Result]`. Smoke test confirms 12/12 collision-prone identifiers pass through as literal text under the new parser.
- **Asymmetric build pipeline.** v3.9 needed a manual SQL-overlay step because the source markdown was unavailable; v3.10's reconstruction makes `python3 build.py` a single-step build for all three tracks.

### Documented

- **Authoring conventions for `<<tag>>` syntax** captured in `README.md` — named closers required (`<<amber>>foo<</amber>>`, not `<<amber>>foo<</>>`); mismatched closer is a lint failure; legacy syntax rejected by build by default.
- **Reconstruction history** captured in `src/content/sql/README.md` — explains where the SQL source came from, links to `.work/reconstruct_sql.py` for any future need to redo it.
- **Process improvements for v4.0** carried forward as inline comments in `build.py` (the migration tool stays around for forks; `TAG_LEGACY_MODE` is the kill switch). The "tag-syntax decision before authoring" note from v3.9's `[Unreleased]` is now a settled fact rather than a deferred decision.

### Known follow-ups for v4.0

- The cheatsheet/tier markdown still cross-references Q29 (in JS Intermediate's JSON section, "See `<<qid:js_int_09>>`") and Q47 (in JS Master's `THE THIS BINDING GOTCHA` section, "See `<<qid:js_mas_07>>`") with text that's now slightly imprecise — Q29 is no longer specifically about JSON.parse, and Q47 is no longer specifically about `this` binding. Both references stay defensible because the questions still exercise the broader skill (try/catch around async work; lexical-scope-in-callbacks). Edits to the surrounding teaching prose were out of scope for v3.10. Sweep candidate during v4.0 authoring.

---

## [v3.9] — 2026-04-28

Adds JavaScript as the third track, with native in-browser execution and a complete content tree (cheatsheet + 5 tier files + 50 graded questions). Includes new sandboxing infrastructure for JS execution and a new `approx` assertion type for floating-point ML primitives.

### Build artifact
- **`index.html`** md5: `fb49ffa82ee4cf837bf490edc63507e3`
- **size:** 374,334 bytes
- **build pipeline:** Two-step. `build.py` produces a fresh bundle from `src/content/{python,javascript}/*.md`; the `sql` slice is then overlaid byte-for-byte from the v3.8b bundle (see "SQL overlay carry-forward" note below). Python rebuild was verified to be byte-identical to v3.8b's embedded Python bundle, validating the build pipeline against regressions.
- **SQL overlay carry-forward.** The SQL portion of the embedded `CONTENT_BUNDLE` was carried forward verbatim from v3.8b's pre-rendered bundle, NOT regenerated from source markdown. The original SQL `.md` source files were not available during the v3.9 sprint. `src/content/sql/README.md` documents this. **v3.10 prerequisite:** reconstruct the SQL source markdown from the bundle (mechanical reverse-conversion from ANSI back to `[amber]...[/]` form) so the build pipeline is symmetric across all three tracks. Do not begin v4.0 Rust authoring until this is done — different build semantics for different tracks would make Rust integration harder to reason about.

### Tier ML-flavor ratio (final tally)

| Tier | Target (P/A/E) | Actual | Status |
|---|---|---|---|
| Introductory | 100/0/0 | **100/0/0** | on target |
| Amateur | 60/20/20 | 70/10/20 | mild drift; defensible (kept domain framing for thematic continuity) |
| Intermediate | 30/30/40 | **60/0/40** | off target on adjacent-framing — flagged for v3.10 realignment |
| Experienced | 20/20/60 | 50/0/50 | classes-half pure-JS by necessity; ML half on target |
| Master | 10/10/80 | **40/10/50** | structural concepts (generators, Proxy, this-binding) earn pure-JS framing; minor adjacency miss |

P = pure-JS, A = ML-adjacent framing, E = explicit-ML primitive. v3.10 will reframe Q26 / Q27 / Q29 to bring Intermediate to target without changing the JS skill being tested.

### Added
- **`JsEngine` class** in `index.template.html` parallel to `PythonEngine` and `SqlEngine`. Each grading round runs in a fresh Web Worker spun up from a Blob URL. The Worker source is a UUID marker assignment followed by `boot.js` (sandbox + assertion runtime). Single-use workers ensure the 3000ms execution budget is per-question, not per-session.
- **Sandbox at boot** — the Worker deletes network APIs (`fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `importScripts`, `BroadcastChannel`), persistent storage (`indexedDB`, `Cache`, `caches`), and `Notification` before any user code runs. `crypto` and `performance` are allowlist-trimmed; `Worker` construction is denied via Proxy (typeof check still returns `'function'`). `MessageChannel` retained per the v3.9 review. Marker-gated message handler drops any postMessage that doesn't carry the per-worker UUID.
- **`approx` assertion type** for floating-point ML primitives. Three forms: scalar (binding name + `tol`), array (flat array + `tol`), expression (read expression + `tol`). All require explicit `tol` (no default — inconsistent tolerances make grading feel arbitrary). NaN and ±Infinity always fail; shape mismatches fail before numeric compare. Optional `forbidden:[...]` companion field for "implement X without Y" questions. Failure detail format: `expected v ≈ 0.665200 (±0.001)\n   got      v = 0.700000 (Δ=0.0348)`.
- **`QUESTIONS.javascript`** — 50 questions across 5 tiers. Q1–Q10 introductory (variable bindings, simple collections, console.log, template literals). Q11–Q20 amateur (array methods, destructuring, default args, spread, light ML: one-hot, argmax). Q21–Q30 intermediate (closures, async/await, JSON, Promise.all, try/catch, plus softmax, cosine similarity, dot product, euclidean distance). Q31–Q40 experienced (classes, inheritance, getters/setters, fetch idioms, plus vec_add, vec_mean, stable_softmax, tiny feedforward, cross-entropy). Q41–Q50 master (generators, Proxy, Float32Array, memoization, this-binding gotcha, plus embedding lookup, layer normalization, top-k, matvec, and Q50 capstone: nearest-embedding semantic search).
- **JavaScript learning content** in `src/content/javascript/` — `cheatsheet.md` (565 words) plus 5 tier files (concepts + 3 worked examples per tier, ~4047 words total).
- **`globalThis.<api>`-deletion lint** in `build.py` — scans fenced code blocks in JS content for references to sandbox-deleted APIs (`globalThis.fetch`, `self.fetch`, `window.fetch`, etc.). Fires only on JS track content; does not fire on prose mentions, only on code-block usage. A code block telling the user to write `globalThis.fetch(...)` would mislead them since that throws inside the worker.
- **JS engine status** in the footer (`engines · python: ready · sql: ready · js: ready`).

### Changed
- **Track loop in `build.py`** now iterates `("sql", "python", "javascript")` instead of `("sql", "python")`.
- **Build summary** prints `js words: ~N` alongside the existing SQL and Python word counts.
- **Twelve hardcoded `['python','sql']` literals** in the template promoted to include `'javascript'` (KPI rollups, completion checks, tier-progression rollover, cmdGoto track loop, etc.).
- **Engine ternary** `track === 'python' ? this.py : this.sql` rewritten as a chained ternary covering the third track: `track === 'python' ? this.py : track === 'sql' ? this.sql : this.js`. Three call sites updated.
- **`TerminalApp` constructor** takes a `js` parameter alongside `py` and `sql`. Construction call site at `new TerminalApp(...)` updated.
- **Engine wiring** at the boot path adds `const js = new JsEngine();` alongside `py` and `sql`. JsEngine is synchronous-ready after construction (no async load like Pyodide); it only fails if `Worker` or `Blob` are unavailable.
- **Version bumped** from v3.8b to v3.9 across boot banners, footer, CONTENT_BUNDLE comment, and README badges.

### Fixed
- **Indirect-eval scope leak** discovered during Q5 review: `(0, eval)` at global scope only leaks `var` declarations onto `globalThis`; `const`/`let` create script-scope bindings invisible to subsequent eval. Fix: collapse user-code execution and assertion reads into a single async IIFE so reads share scope with declarations. Top-level `await` works for free as a side effect. The IIFE constraint is documented inline at the top of `runUserCode` in boot.js.
- **`[prop]` tag collision** in tier-master content: `target[prop]` was being parsed as a markdown color tag (since `prop` matched the build.py tag regex `[a-z]{3,}`). Renamed to `target[p]` in two places. Lint now passes clean.
- **Q39 (tiny_forward) assertion was too loose**: original test case had both row outputs positive pre-ReLU, so a "skipped ReLU" answer accidentally passed. Replaced with a 4-row forward pass where Row 1 is negative pre-ReLU (catches the missing-ReLU bug). Single test case keeps the assertion expression a flat array (preserves `approx` type's "flat arrays only" rule).
- **Q36 (vec_add) and Q49 (matvec) used `approx` with nested-array `expected`**, which violates the locked spec ("flat arrays only; nested arrays must use `expression` + `deepEq`"). Switched both to `expression` type. Both questions use integer arithmetic with no float drift, so plain `deepEq` is correct.

### Documented
- **Authoring principle for assertion tightness**, captured as a comment block in `QUESTIONS.javascript`: *if an alternate solution demonstrates the same or adjacent skills, accept it (the prompt is the contract, the assertion is the verifier); if it demonstrates nothing, tighten the assertion; when in doubt, lean simpler*. Discovered during Q23 (JSON parse/stringify) review when a regex-shortcut alternate solution beat tightened assertions and tightening became a defensiveness exercise.
- **Approx-tolerance defaults**, captured at the top of `QUESTIONS.javascript`: `1e-3` for single softmax-class probabilities, `1e-4` for cosine similarity, `1e-2` for tiny feedforward logits, `1e-9` for one-hot integer casts. New tolerances need a documented reason — inconsistent tolerances make grading feel arbitrary to users.
- **Tier ML-flavor ramp** target ratios: Introductory 100/0/0 (pure-JS / ML-adjacent / explicit-ML), Amateur ~60/20/20, Intermediate ~30/30/40, Experienced ~20/20/60, Master ~10/10/80. Final tally landed at 100/0/0, 70/10/20, 60/0/40, 50/0/50, 40/10/50 — Intermediate and Master both off target on adjacent-framing; flagged as v3.10 calibration candidate.
- **`[a-z]{3,}` tag-regex compatibility** with v3.8a parser preserved. JS-specific variable names that happen to be 3+ lowercase chars (`prop`, `key`, `idx`) collide with the tag parser; the convention going forward is to use single-letter or non-purely-lowercase names in code examples.

---

## [v3.8b] — 2026-04-26

Authored real SQL and Python learning content into the v3.8a infrastructure, plus three small infra improvements pulled forward from v3.8a's handoff notes.

### Added
- **SQL learning content** in `src/content/sql/` — `cheatsheet.md` (whole-language reference) plus 5 tier files (concepts + 2-3 worked examples per tier).
- **Python learning content** in `src/content/python/` — same structure.
- **Multi-line tag support in build.py parser.** Tags can now span paragraphs; balance is checked at EOF rather than per-line. EOF-balance approach chosen over paragraph-grouping for simpler implementation.
- **Clickable `[qid:...]` references** in the cheatsheet/concepts panel. Click handler calls `cmdGoto(qid)` which prints a preview of the referenced question. Terminal-side click handling deferred to a future polish.
- **`cmdGoto` resolver** — looks up question by id across all tracks, prints prompt + assertion type. Acts as a lightweight "show me this question" command without changing track.

### Fixed
- **Concepts auto-show on tier rollover.** v3.8a's CHANGELOG framed this as "appears one beat late" but tracing `getCurrentTier` revealed intra-track tier transitions never hit the `q === null` branch at all (the function auto-rolls forward as soon as a tier hits `GATE_SIZE`). The real bug was concepts never appearing on rollover; the fix is in the question-served path via a new `_maybeAutoShowConcepts` hook tracking `shownConcepts` per track.

### Changed
- Tag-regex tightened from `[a-z]+` to `[a-z]{3,}` so Python indexing like `obj[i]`, `cache[n]`, `d[k]` passes through as literal text in code blocks. Side effect: 1-2 char tag names now silently pass through as literal — design future tag names with 3+ chars.
- ANSI header close-code emit order changed from `\x1b[22m\x1b[39m` to `\x1b[39m\x1b[22m`. Renders identically. Means v3.8b output is not byte-identical to a hypothetical v3.8a re-encoding; idempotent build claim now holds within v3.8b but not across versions.

### Documented
- README updated with content authoring conventions.
- Tier validation walkthrough documented for manual verification (not yet performed in browser; needs human pass).

---

## [v3.8a] — 2026-04-25

Infrastructure-only release introducing the learning layer foundation. No user-facing learning content yet — that lands in v3.8b. This version proves the architecture works end-to-end.

### Added
- **Build step:** `build.py` reads content files from `src/content/<track>/` and concatenates them into `index.html` via `src/index.template.html`. Idempotent — md5 stable across runs.
- **Content file format:** Markdown with `[amber]...[/]` style ANSI color tags. Parser supports the full color palette used in the terminal.
- **`build.py --check`** mode lints content without writing — catches unclosed tags, missing question references, code blocks over 15 lines.
- **Three new in-track commands:**
  - `concepts` — show current tier's concepts block (auto-shown on tier entry)
  - `cheatsheet` — open the language reference panel in the right rail
  - `examples` — walk 2-3 worked problems with `next` / `back` navigation
- **Right-rail tab toggle:** `[QUESTION] [CHEATSHEET]` — defaults to question, cheatsheet shows on demand.
- **Action bar gets a `📖 REF` button** alongside Run/Submit/Hint that toggles the cheatsheet tab.
- **Mobile fallback:** on narrow viewports the rail hides, so `cheatsheet` prints to the terminal output instead of the panel.

### Changed
- File structure: content now lives in `src/content/<track>/<file>.md`, `index.html` is a build artifact regenerated by `build.py`.
- `[qid:...]` references render as styled links in the panel (clickable wiring deferred to v3.8b).

### Known limitations (resolved in v3.8b)
- Tags must close on the line they open. Multi-line `[dim]...[/]` blocks not yet supported by parser.
- `[qid:...]` references are styled but not yet click-handled.
- `concepts` auto-show fires one beat late on tier unlock (next question served, not unlock event).

---

## [v3.7] — 2026-04-22

### Added
- Full line-editing support in the terminal:
  - `←` `→` arrow keys move cursor character-by-character (wraps across newlines)
  - `Home` / `Ctrl+A` jump to start of current line
  - `End` / `Ctrl+E` jump to end of current line
  - `Delete` removes character at cursor (forward delete)
  - `Ctrl+K` kills from cursor to end of line
  - `Ctrl+U` kills from start of line to cursor
- `cursorPos` state tracking in `TerminalApp`
- `_bufferIndexToRowCol()` and `_moveCursorToPosition()` helpers for cursor math
- Fast path for insert/backspace at end-of-buffer (no full redraw)

### Changed
- `onData` now parses a wider set of ANSI key sequences (Home, End, Delete, Ctrl+Arrow)
- Every `inputBuffer` mutation now paired with `cursorPos` update
- `_onEnter` inserts `\n` at cursor (could be mid-buffer, not just append)

## [v3.6] — 2026-04-22

### Added
- `Tab` key inserts 4 spaces for indentation in TRACK mode (maintains IDLE-mode tab-completion)

## [v3.5] — 2026-04-21

### Fixed
- Ctrl+Enter double-newline bug: keyboard handler now fully suppresses xterm's default Enter processing in TRACK mode. Every Enter press routes through exactly one code path.

## [v3.4] — 2026-04-21

### Fixed
- Duplicate `doSubmit` method from v3.2 was silently overriding the v3.3 implementation. Removed orphan.
- Dead `lastInput` field removed.
- Enter now unconditionally creates a newline in TRACK mode — meta-commands (`exit`, `schema`, `help`, etc.) execute only via ▶ RUN / Ctrl+Enter or ✓ SUBMIT / Ctrl+Shift+Enter.

### Added
- `_tryMetaCommand(buf)` helper unifying how meta-commands are recognized in both Run and Submit flows.

## [v3.3] — 2026-04-21

### Added
- Persistent action bar below the terminal with three buttons:
  - **▶ RUN** (amber) — previews query, preserves buffer for editing
  - **✓ SUBMIT** (green) — grades the current query
  - **💡 HINT** — shows hint for active question
- Keyboard shortcuts: `Ctrl+Enter` = Run, `Ctrl+Shift+Enter` = Submit
- Action-bar status pill showing `TRACK · TIER · Q N of 10`
- `action-btn` CSS with hover/active/disabled states
- `updateActionBar()` method on `TerminalApp`

### Changed
- Enter in TRACK mode is now a newline only (never grades)
- Typed `submit` command removed — use the button

## [v3.2] — 2026-04-21

### Added
- SQL in-track commands: `tables`, `describe <table>`, `peek <table>`
- `SqlEngine.preview()`, `listTables()`, `describeTable()`
- `PythonEngine.preview()` — runs code with stdout capture and assertion-target probe
- SQL result renderer: column-aligned table with up to 10 rows
- Continuation prompt `...>` for multi-line queries
- `writeContinuationPrompt()`, `redrawInput()`, `renderedLines` tracking

## [v3.1] — 2026-04-21

### Added
- Question bank expanded to 100 total: 10 per tier × 5 tiers × 2 tracks
- Cross-terminal nav pills in header (`GARAGE · PORTFOLIO · BUDGET · TRAINING`)
- ResizeObserver on terminal container for clean re-fit across breakpoints
- Customers 9 (Riley Evans) and 10 (Pat Zhao) added to seed with NULL phone for `IS NULL` questions
- `reset` command now shows concrete count of questions to wipe

### Fixed
- SQL engine rebuilds database before every evaluation to prevent DML leakage
- Ticker animation uses `translate3d` + `backface-visibility` for iOS Safari GPU layer fix

## [v3.0] — 2026-04-20

### Added
- Bloomberg-style multi-panel UI: left rail (tier watchlist + KPIs), center terminal, right rail (active question + schema + activity feed)
- Ticker tape scrolling across top
- Activity log tracking last 10 events (correct/incorrect/unlock/enter/exit/reset)
- Live KPIs: session attempts, accuracy, streak, session timer

## [v2.x and earlier]

- v2.1: iOS Pyodide hardening — 90s timeout, pattern-match fallback, DEGRADED state
- v2.0: Real Pyodide + sql.js execution, 5-tier rename (novice removed, master added), tab completion, command history, export/import
- v1.x: Initial terminal with xterm.js, string-match stub validation, basic progression

---

## Versioning

Ghost Training Terminal uses a loose SemVer scheme:
- **Major** bumps on significant architectural shifts (rare)
- **Minor** bumps on new tracks or major feature additions
- **Patch-style letters** (e.g. v3.8a, v3.8b) indicate split sub-versions that must ship together to complete a milestone

Each shipped version updates the `v3.X` string in:
1. `index.html` footer
2. `index.html` boot banner (both mobile and desktop variants)
3. `README.md` version badge
