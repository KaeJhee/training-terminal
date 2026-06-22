# Ghost Training Terminal — Version Prompts

This file tracks the prompts used to drive each version of the terminal forward,
along with handoff notes recorded at the end of each version. Each prompt is
designed to be pasted into a fresh Claude session with the current `index.html`
attached (or the GitHub repo URL shared).

---

## End goal — restated

> Ghost Training Terminal teaches someone a new programming language OR helps
> experienced developers level up. Six tracks across five tiers
> (Introductory → Amateur → Intermediate → Experienced → Master), 10 hand-authored
> questions per tier. Each track has ML-adjacent flavor. All learning content is
> authored in Markdown files under `src/content/`, concatenated into the single
> deployable `index.html` by `build.py`.

**Planned track sequence:**
1. SQL — shipped in v3.x
2. Python — shipped in v3.x
3. JavaScript — v3.9
4. Rust — v4.0
5. C++ + CUDA — v4.1 (combined, see rationale below)

**Current version:** v3.7 (full line editing — cursor nav, Home/End, mid-buffer editing)

---

## Revisions applied to the plan

Two plan refinements we agreed on before locking these prompts:

**1. v3.8 split into v3.8a + v3.8b.**
Originally v3.8 was doing two heavy things in one version: introducing the build
system AND authoring 12 content files (SQL + Python, 6 files each). Splitting
keeps each session focused. v3.8a ships the infrastructure (build.py, new commands,
UI tabs, content file format) proving the architecture works. v3.8b authors the
actual content now that the format is validated.

**2. CUDA folded into v4.1 (formerly v4.1 C++ + v4.2 CUDA).**
CUDA is C++ with extensions. ~60% of the C++ Experienced/Master content touches
concepts that transfer directly to CUDA (memory layout, move semantics, templates,
SIMD intrinsics). The pattern-match infrastructure for C++ is the same one CUDA
uses. Combining them avoids two round-trips through the same codebase. CUDA
content gets authored as a specialization branch off C++ Intermediate, exactly as
originally planned — just shipped in the same version.

---

## Version index

| Version | Scope | Status |
|---------|-------|--------|
| [v3.8a](#v38a--learning-layer-infrastructure) | Build system + command UI + content file format | ✅ Shipped 2026-04-25 |
| [v3.8b](#v38b--sqlpython-learning-content) | Author SQL and Python learning content | ✅ Shipped 2026-04-26 |
| [v3.9](#v39--javascript-track) | New track: JS (native execution) | ✅ Shipped 2026-04-28 |
| [v3.10](#v310--consolidation-tag-syntax-sql-source-rebuild) | Consolidation: tag syntax migration, SQL source reconstruction, JS calibration fixes | ✅ Shipped 2026-05-06 |
| [v4.0](#v40--rust-track) | New track: Rust (pattern-match, first of kind) | Pending |
| [v4.1](#v41--c-track--cuda-specialization) | New tracks: C++ (pattern-match) + CUDA (specialization) | Pending |

---

## v3.8a — Learning layer infrastructure

**Duration estimate:** 1-2 sessions
**Risk level:** medium (new build step; file format decisions)

```
Ghost Training Terminal v3.8a — build the learning layer infrastructure.

CONTEXT
- Pick up from v3.7 (latest deployed). The current index.html is attached.
- End goal: teach someone a new language or help experienced devs level up
  across 6 tracks (SQL, Python existing + JavaScript, Rust, C++, CUDA planned).
- This version is INFRASTRUCTURE ONLY — no content authoring. v3.8b will
  author the SQL and Python learning content using the format built here.

SCOPE FOR THIS VERSION
1. Introduce a build step:
   - Create src/index.template.html containing the app shell with content
     placeholders like {{CONTENT_BUNDLE}} (one placeholder embeds all content
     as a JSON object).
   - Create src/content/<track>/ folder structure holding cheatsheet.md and
     tier-<tier>.md files. Populate with PLACEHOLDER content (just "TBD" +
     the section headers) — real content comes in v3.8b.
   - Write build.py that:
     * Reads content files from src/content/
     * Parses [amber]...[/] style ANSI color tags into terminal escape codes
     * Produces a JSON object: { track: { cheatsheet: "...", tiers: { ... } } }
     * Substitutes into template at {{CONTENT_BUNDLE}}
     * Writes final index.html in repo root
   - build.py must also lint:
     * All color tags have matching closers
     * All referenced question IDs exist in the bank
     * Code blocks don't exceed 15 lines (readable in right rail)
2. Three new in-track commands: concepts, cheatsheet, examples.
   - concepts: show the current tier's concepts block. Auto-shown on tier entry.
   - cheatsheet: open a tab-toggle panel in the right rail replacing the
     active-question card. On mobile (<900px) print inline to terminal.
   - examples: walk 2-3 worked problems with `next` / `back` navigation.
3. Right-rail tab toggle: [QUESTION] [CHEATSHEET]. Question is default.
4. Action bar gains a 📖 REF button alongside Run/Submit/Hint. REF toggles
   the cheatsheet tab.
5. Placeholder content validates the pipeline end-to-end. Typing `cheatsheet`
   in SQL track should show "SQL cheatsheet TBD" rendered in the panel.

EXPLICIT NON-GOALS (do NOT do this version)
- No real learning content (v3.8b).
- No new language tracks.
- No engine changes.
- No question bank changes.

DELIVERABLES
- Working build.py.
- src/index.template.html and src/content/ directory structure.
- All existing 100 questions still work after refactor.
- index.html rebuilds cleanly when build.py runs.
- Zip with repo structure intact.
- README updated with build-step documentation.

CRITICAL — SHOW ME BEFORE BUILDING
- The content tag format in a rendered example. I need to see one real
  cheatsheet section parsed and displayed in the terminal before we commit
  to the format for 18 files (6 tracks × 3 file types).
- The build.py architecture (what it reads, what it writes, how it lints).

KNOWN RISKS
- Build step breaks the "just open index.html" story if misconfigured.
  Verify: after running build.py once, index.html must open standalone with
  NO external content dependencies.
- Right-rail panel switching: question state must be preserved when toggling
  to cheatsheet and back.
```

### v3.8a handoff notes
*Completed: 2026-04-25 (or whenever you ship this)*

**Verified during v3.8a ship:**
- All 100 question IDs intact in built output
- 4 `[qid:...]` references resolve cleanly
- 0 `{{CONTENT_BUNDLE}}` placeholders remaining
- JS parses (Node `--check`)
- HTML well-formed, all required IDs present (`tab-question`, `tab-cheatsheet`, `cheatsheet-panel`, `btn-ref`, etc.)
- Build is idempotent (md5 stable across runs)
- `--check` mode lints without writing
- Lint correctly catches unclosed tags (verified by injecting `[amber]oops` and getting exit 1)
- v3.7 → v3.8a in footer + both boot banners; historical `// v3.7:` comments preserved as commit context

**Parser limitations to address in v3.8b before authoring:**

1. **Tags must close on the same line they open.** Hit during placeholder authoring. Multi-line tag pairs (long `[dim]...[/]` blocks across paragraphs) need a parser refactor: group consecutive prose lines into one paragraph block before tag processing, OR allow the stack to persist across lines with EOF balance validation. ~30 lines of build.py change. Recommended yes.

2. **`[qid:...]` is rendered visually but not yet clickable.** Blue + underlined in both terminal and panel, but no click handler. xterm has a link addon that would handle terminal side; panel side just needs `onclick` calling `app.cmdGoto(qid)`. Recommended yes for panel, defer for terminal.

3. **`concepts` auto-show timing is one beat off on tier unlock.** Right now the unlock branch in `serveNextQuestion` logs the unlock but the new tier's concepts only appear on the NEXT `serveNextQuestion` call (next question served). Works correctly but UX is delayed. Trivial to hook into the unlock path directly. Recommended yes.

**Footer-version-bump checklist for next ship** (5 locations):
1. Footer line in `src/index.template.html`
2. Boot banner (mobile variant) in app JS
3. Boot banner (desktop variant) in app JS
4. README badge
5. CHANGELOG entry

---

## v3.8b — SQL/Python learning content

**Duration estimate:** 1-2 sessions
**Risk level:** low (format proven in v3.8a; just authoring + 3 small infra tasks)

```
Ghost Training Terminal v3.8b — author SQL and Python learning content.

CONTEXT
- Build on v3.8a (learning layer infrastructure shipped).
- Content file format is locked and validated. v3.8a verified the build
  pipeline end-to-end with placeholder content.
- End goal reminder: teach the language, don't just quiz syntax.

PRE-AUTHORING INFRA TASKS (resolved during v3.8a handoff, do these FIRST)
1. Multi-line tag support in build.py parser. Currently tags must close on
   the line they open. Multi-paragraph [dim]...[/] blocks are an authoring
   pain. ~30 LOC change: either group consecutive prose lines into paragraph
   blocks before tag processing, or allow tag stack to persist across lines
   with EOF balance validation. Either approach fine; whichever feels
   cleaner. Test with a known multi-line case.
2. Clickable [qid:...] references in the cheatsheet/concepts panel. Add
   onclick handler that calls app.cmdGoto(qid). Terminal-side click handling
   via xterm link addon DEFERRED — panel-only is sufficient for v3.8b.
3. Hook concepts auto-show into the unlock path of serveNextQuestion, not
   just first-entry. Currently new tier's concepts appear on the NEXT
   question served, one beat late. Fire concepts immediately on unlock.

SCOPE FOR THIS VERSION
1. Author SQL learning content in src/content/sql/:
   - cheatsheet.md (~500 words — whole-language reference)
   - tier-introductory.md (concepts + 2-3 examples, ~400 words)
   - tier-amateur.md (~400 words)
   - tier-intermediate.md (~450 words)
   - tier-experienced.md (~450 words)
   - tier-master.md (~500 words)
2. Author Python learning content in src/content/python/:
   - Same structure, ~2500 words total
   - Tier progression: syntax basics → comprehensions/control flow →
     functional (map/filter/reduce) → OOP + decorators →
     generators/async/metaclasses

AUTHORING STANDARDS
- Voice: direct, no padding. Explain "why" after the "what".
- Each tier's LAST example should preview a concept from the NEXT tier,
  motivating progression.
- Examples are DIFFERENT from graded questions (no answer leaking).
- Cheatsheets are whole-language, not per-tier.
- ML-adjacent framing throughout: classification thresholds, linear algebra,
  training loop intuition — WITHOUT requiring ML knowledge to answer anything.
- Forward pointers: each concepts block ends with "NEXT TIER: ..." line.
- At Master tier, content may assume reader has seen a neural net before.
- Use [qid:sql_int_03]-style references where they help; they're now clickable
  in the panel.

EXPLICIT NON-GOALS
- No new tracks.
- No question bank changes (content teaches, doesn't re-quiz).
- No terminal-side qid click handling (panel-only for now).

AI-ASSIST POLICY
- Using AI to draft is fine (efficient for structured content).
- Every draft MUST be human-edited before committing.
- Footnote in README acknowledging AI-assisted authoring, if used.

DELIVERABLES
- 12 populated content files (SQL + Python).
- 3 infra improvements landed (multi-line tags, clickable qids in panel,
  concepts on unlock).
- build.py runs clean — zero warnings on lint pass.
- All cheatsheet / concepts / examples commands working with real content.
- Zip.

VERSION-BUMP CHECKLIST (5 locations to update)
1. Footer line in src/index.template.html (v3.8a → v3.8b)
2. Boot banner mobile variant in app JS
3. Boot banner desktop variant in app JS
4. README badge
5. CHANGELOG entry

VALIDATION
- Walk through Introductory tier of each track in full: enter track, read
  auto-shown concepts, type `examples`, navigate all 3 examples, type
  `cheatsheet`, read full cheatsheet, return to questions, answer one, submit.
  Entire flow should feel coherent.
- Trigger a tier unlock and verify concepts appear immediately, not after
  next question served.
- Click a [qid:...] reference in the panel and verify it jumps correctly.

KNOWN RISKS
- Content drift between what's taught and what's graded. When editing
  content, reference the actual question IDs to ensure alignment.
- Example #3 of each tier MUST preview the next tier — tempting to skip
  because it feels like overreach; don't skip it, it's a pedagogical
  load-bearer.
```

### v3.8b handoff notes
*Completed: 2026-04-26*

**Shipped:**
- SQL learning content (6 files in `src/content/sql/`)
- Python learning content (6 files in `src/content/python/`)
- Multi-line tag parser (EOF-balance approach, per v3.8a recommendation)
- Clickable `[qid:...]` wiring in panel + new `cmdGoto` resolver
- Concepts auto-show fires on tier rollover (see interpretive call #1 below)
- Version bumps in all 5 locations (footer, both boot banners, README badge, CHANGELOG)
- README updated with authoring conventions
- Lint-clean build (`build.py --check` passes)
- Zip rebuilt

**Interpretive calls — re-check before treating v3.8b as merged:**

1. **Unlock-branch reading.** v3.8a's CHANGELOG framed the concepts bug as "appears one beat late" and put a placeholder comment in `serveNextQuestion`'s `q === null` branch. Tracing `getCurrentTier`, I concluded that branch only fires at master endgame because the function auto-rolls forward as soon as a tier hits `GATE_SIZE`. So intra-track tier transitions (intro→amateur, etc.) never hit that branch at all, and the real bug was concepts never appearing on rollover, not appearing late. The fix is in the question-served path. If the trace is wrong, the fix may need to move. The v3.8b CHANGELOG "Fixed" section spells out the reasoning.

2. **Tag-regex tightening from `[a-z]+` to `[a-z]{3,}`.** Needed to let Python indexing like `obj[i]`, `cache[n]`, `d[k]` pass through as literal text in code blocks. All current tags are 3+ chars (red and dim are shortest). Side effect: the tag namespace is now closed off at 3-char minimum — any future 1-2 char tag will silently pass through as literal.

**Known minor divergences from v3.8a:**

- ANSI header close-code order is `\x1b[39m\x1b[22m` (close-fg, close-bold) where v3.8a emitted `\x1b[22m\x1b[39m`. Renders identically in any conforming terminal but means v3.8b output isn't byte-identical to a hypothetical v3.8a re-encoding. The "idempotent — md5 stable across runs" claim now holds *within* v3.8b but not *across* versions.
- Two `data-qid` anchors per cheatsheet (4 total in HTML payload). Most qid references live in tier files which are ANSI-only. Adding more clickable anchors means adding `[qid:...]` calls to the cheatsheet markdown.

**Programmatically validated:**
- Bundle structure: 2 tracks × 5 tiers × 3 examples, both cheatsheets have `ansi` + `html`, balanced HTML tag counts, multi-line `[dim]` block renders with correct per-line bracketing.
- All 5 version-bump locations confirmed via grep.
- All 4 `data-qid` attributes present in built HTML.
- All `[qid:...]` references in source cross-checked against question bank (zero lint warnings).

**Still needs manual validation in browser** (no browser in build environment):
- Walk through Introductory tier of each track per the v3.8a handoff validation checklist
- Trigger a tier unlock and visually confirm concepts appear at the right time
- Click a `[qid:...]` reference in the panel and confirm the preview prints correctly
- Mobile fallback path for `cheatsheet` command on narrow viewports

**Pre-existing comments not touched:** Several `// v3.8a:` comments on active code remain (e.g., on the `shownConcepts` field declaration, on rail-tab CSS sections). Historical markers, not stale references — left alone.

**Outstanding nit deferred:** `cmdGoto` preview prints to terminal regardless of mode. If user is mid-typed-input in TRACK mode, the preview pushes the prompt up. Acceptable, but a future polish could detect that case and append-after-input rather than interrupt.

---

## v3.9 — JavaScript track

**Duration estimate:** 3-5 sessions
**Risk level:** medium (new engine, sandboxing concerns)

```
Ghost Training Terminal v3.9 — add JavaScript as the third track.

CONTEXT
- Building on v3.8b (learning layer shipped for SQL + Python with real content).
- JS chosen first among new tracks because:
  * Executes natively in-browser (no pattern-match compromise)
  * Broadest user value of the four new languages
  * Proves the "3-track" layout works before stressing it further
- Sets precedent for how new tracks plug into the registry + learning layer.

ARCHITECTURE BREADCRUMBS FROM v3.8b (read these BEFORE editing)
The build system is already track-agnostic. Adding JS means:
1. Drop content files in src/content/javascript/ (filenames must follow the
   convention established in v3.8b: cheatsheet.md, tier-introductory.md,
   tier-amateur.md, tier-intermediate.md, tier-experienced.md, tier-master.md)
2. Add 'javascript' to the track loop in build_track_bundle callers in
   build.py:build()
3. Register a JsEngine in index.template.html (parallel to PythonEngine/SqlEngine)
4. Add the question bank under QUESTIONS.javascript
The cheatsheet rendering pipeline, cmdGoto resolver, and _maybeAutoShowConcepts
hook already iterate ['python', 'sql'] and TIER_ORDER — adding a track means
EXTENDING the array, not refactoring. Authoring conventions are codified in
README.md and the build's lint pass; violations surface at `--check` time.

TRACK KEY NAMING — DECIDED
Track key is 'javascript' (not 'js'). Rationale:
- Matches the existing full-word convention ('python', 'sql' is the only
  short key and it has no longer alternative).
- Unambiguous in greps (searching 'js' in the codebase hits many false
  positives like file extensions, variable names; 'javascript' is clean).
- Question IDs follow the same convention: js_intro_01, js_am_03, etc.
  (the prefix in IDs uses 'js' for brevity, but the TRACK KEY in TRACKS
  registry, content/ directory, and QUESTIONS object is 'javascript').
- The class name is JsEngine (mirroring SqlEngine — class names use the
  acronym form for readability; track keys use the full word).

SCOPE FOR THIS VERSION
1. New JsEngine class matching PythonEngine/SqlEngine interface:
   - Execute user code in a sandboxed Web Worker (not eval, not iframe)
   - Capture stdout via console.log proxy
   - Reuse existing assertion types: binding, call, expression, stdout
   - Add new 'approx' assertion type for numerical tolerance (needed for
     softmax-style ML questions). Design API before authoring questions.
2. Register 'javascript' track in the TRACKS registry.
3. Author 50 graded questions (10 per tier) with ML-adjacent framing.
4. Author JS learning content:
   - javascript/cheatsheet.md (~500 words)
   - 5 tier-*.md files (~2500 words total)
5. Cross-terminal nav pills: add JS pill if applicable.

TIER PROGRESSION
- Introductory: let/const, primitives, arrays, basic objects
- Amateur: array methods (map/filter/reduce), destructuring, template literals
- Intermediate: arrow functions + closures, async/await basics, JSON
- Experienced: classes, modules, Promises in depth, fetch idioms
- Master: generators, Proxy, typed arrays, performance patterns

EXPLICIT NON-GOALS
- No Rust/C++/CUDA.
- No pattern-match engine (v4.0).
- No changes to SQL/Python beyond what the registry refactor requires.

ML FLAVOR GUIDELINES
- Tier-by-tier framing ramp:
  * Introductory: NO ML framing. Pure JS idioms — variables, primitives,
    basic objects, basic arrays. Reasoning: Introductory is for people who
    know how to program but may not know modern JS specifically; adding
    ML framing on question 3 is intimidation that doesn't pay back.
  * Amateur: Light ML — one-hot encoding, threshold classification, basic
    vector ops. Most questions still pure JS idioms.
  * Intermediate / Experienced / Master: Full ML primitives — softmax,
    cosine similarity, tiny feedforward net, embedding lookup.
- NO ML knowledge required to solve any question, even at Master tier.
- Gotcha content (== vs ===, this binding, hoisting) capped at 1-2 per tier.
  Rest teaches idiomatic modern JS.

DELIVERABLES
- JsEngine class with full execution and sandboxing.
- 'approx' assertion type documented and tested.
- All 50 questions executing successfully against the engine.
- All content files authored and validated by build.py.
- README updated.
- Zip.

APPROX ASSERTION SPEC (locked — implement to match)
Three forms, each with required `tol` (absolute tolerance, no default):

  // Scalar form
  { type:'approx', expression:'softmax([1,2,3])[2]', expected:0.6652, tol:1e-3 }

  // Array form (element-wise; flat arrays only, no nesting)
  { type:'approx', expression:'softmax([1,2,3])',
    expected:[0.0900, 0.2447, 0.6652], tol:1e-3 }

  // Binding form
  { type:'approx', name:'probs', expected:[0.5, 0.5], tol:1e-6 }

Locked semantics:
1. Absolute tolerance only. No relative-tolerance variant unless a question
   genuinely needs it (none in the v3.9 bank should).
2. `tol` REQUIRED. Missing `tol` is a build.py --check error, not a silent
   default. Same for missing or undefined `expected`.
3. Scalar: Math.abs(got - expected) <= tol.
4. Array: must be array, lengths must match, element-wise pass.
5. Flat arrays only. No nested arrays. Master-tier matrix outputs use
   flat-with-shape conventions documented in the prompt.
6. NaN ALWAYS fails (even NaN === NaN case). Detail: "got NaN at index k".
7. ±Infinity ALWAYS fails. Same reasoning — catches softmax-by-hand bugs.
8. Shape mismatch (scalar vs array, wrong length) fails BEFORE numeric
   compare with a shape-mismatch detail.
9. Failure detail format mirrors `binding` style with delta annotation:
   "expected probs[1] ≈ 0.244725 (±1e-3)\n   got probs[1] = 0.252100 (Δ=7.4e-3)"

OPTIONAL companion field:
  // forbidden: array of substrings that must NOT appear in userCode
  // Runs string-match BEFORE numeric check. If user code contains any
  // forbidden token, fails with detail "forbidden pattern: <token>".
  { type:'approx', expression:'softmax([1,2,3])',
    expected:[...], tol:1e-3,
    forbidden:['reduce'] }   // "implement softmax without reduce"

CRITICAL — SHOW ME BEFORE BUILDING
- The SANDBOX_DELETIONS array as a constant before engine implementation.
  Specifically address: Notification, navigator.sendBeacon, BroadcastChannel,
  MessageChannel, Cache, caches, crypto.subtle. Some are harmless or useful
  (crypto.getRandomValues for ML weight init); some leak side channels.
  Post the list, wait for review, then proceed.
- Web Worker sandboxing implementation. Test with adversarial inputs:
  * attempted document/window access
  * fetch to external URL
  * infinite loop (must have 3s timeout via Promise.race + worker.terminate)
  * localStorage / indexedDB access
  * postMessage spam from user code (10000 messages without __ghost_marker__
    token must be silently dropped without OOM)
  None of these should succeed.

KNOWN RISKS
- Web Worker setup is fiddly — first try may not sandbox cleanly.
- JS is TOO permissive — e.g. `"1" + 1 === "11"` is technically fine but
  teaches a bad habit. Resist including this kind of content outside the
  explicit gotcha slots.
- Tag-regex tightening from v3.8b means any 1-2 char tag in JS content
  silently passes through as literal text. If you want short tag names
  (e.g. [js]...[/]) for JS-specific styling, audit the regex first.

OPTIONAL POLISH IF TIME PERMITS (deferred from v3.8b)
- cmdGoto preview prints to terminal regardless of mode. If user is
  mid-typed-input in TRACK mode, the preview pushes the prompt up. Acceptable
  but not ideal. A polish would detect that case and append-after-input
  rather than interrupt. Small change, ~10 LOC.
- Cheatsheet markdown for SQL/Python only has 2 [qid:...] anchors each
  (4 total clickable in HTML payload). Authoring more cross-references
  during v3.9 would broaden the qid-link surface area. Not blocking.
```

### v3.9 handoff notes
*Completed: 2026-04-28*

**Build artifact:**
- `index.html` — 374,334 bytes
- md5: `fb49ffa82ee4cf837bf490edc63507e3`
- Source zip published as `ghost-training-v3.9.zip`

**Shipped:**
- JavaScript joins SQL and Python as the third track
- 50 graded questions across 5 tiers, in-browser execution via sandboxed Web Worker
- New `approx` assertion type (locked spec — three forms, required tolerance, NaN/Infinity always fail, optional `forbidden` companion field)
- Full content tree: cheatsheet (565 words) + 5 tier files (~4047 words total)
- Build pipeline updated to handle three tracks symmetrically

**Verification record:**
- 8/8 sandbox adversarial tests pass (network egress, DOM, infinite loop, persistent storage, postMessage spam, nested Worker, crypto allowlist, approx 9 sub-cases)
- 154 grading paths verified across the 50-question bank
- Python rebuilds byte-identically through build.py (validates non-substantive build changes)
- `python3 build.py --check` clean
- E2E test grades samples (Q1, Q15, Q21, Q39, Q50) through assembled artifact

**Architectural decisions locked this sprint** (v4.x must honor):

1. **Track key naming.** `'javascript'` (full word) for track key, content directory, and `QUESTIONS.javascript`. `js_` prefix for question IDs. Class is `JsEngine` (acronym mirrors `SqlEngine`). Acronym-class + full-word-key mismatch is intentional and consistent.

2. **Sandbox config.** Locked deletions: `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `importScripts`, `BroadcastChannel`, `indexedDB`, `Cache`, `caches`, `Notification`. Kept: `MessageChannel` (low risk in sandboxed worker, useful for legit patterns), `Worker` identifier (only construction denied via Proxy). Crypto allowlist: `getRandomValues` + `randomUUID` kept, `subtle` dropped. Performance allowlist: `now`, `mark`, `measure`, `clearMarks`, `clearMeasures`. `navigator.sendBeacon` surgically removed. Execution budget 3000ms; outer walltime 8000ms.

3. **`approx` assertion type.** Three forms (scalar, array, binding). `tol` REQUIRED — no default. Flat arrays only. NaN and ±Infinity always fail. Optional `forbidden:[...]` companion field. Failure detail format: `expected v ≈ 0.665200 (±0.001)\n   got v = 0.700000 (Δ=0.0348)`.

4. **Tolerance defaults** (committed comment block in `QUESTIONS.javascript`):
   - Single softmax-class probability: `tol: 1e-3`
   - Cosine similarity: `tol: 1e-4`
   - Tiny feedforward logits: `tol: 1e-2`
   - One-hot integer cast: `tol: 1e-9`
   - New tolerances need a documented reason.

5. **IIFE wrapping for user code.** User code runs inside an async IIFE so top-level `const`/`let` are visible to assertion reads (concatenated into the same function body). Top-level await works as a free side effect. Indirect eval at global scope only leaks `var` — that's why the wrapper exists. Constraint documented inline at the top of `runUserCode` in `boot.js`.

6. **Authoring principle for assertion tightness:** if an alternate solution demonstrates the same or adjacent skills, accept it; if it demonstrates nothing, tighten; when in doubt, lean simpler. Discovered during Q23 review when regex shortcuts beat tightened JSON-parse assertions.

7. **Two-step build for v3.9:** stub SQL content + real JS content + real Python content → run build.py → overlay v3.8b SQL bundle bytes onto the output. Preserves byte-stability for SQL without requiring source markdown that wasn't available. **THIS IS TECHNICAL DEBT** — see v3.10.

**ML-flavor ratio per tier (target / actual):**

| Tier | Target (P/A/E) | Actual (P/A/E) | Status |
|------|----------------|----------------|--------|
| Introductory | 100/0/0 | 100/0/0 | ✓ on target |
| Amateur | 60/20/20 | 70/10/20 | mild drift, defensible |
| Intermediate | 30/30/40 | 60/0/40 | OFF target — undersupplied on adjacent-framing |
| Experienced | 20/20/60 | 50/0/50 | classes-half pure-JS by necessity |
| Master | 10/10/80 | 40/10/50 | OFF target — Generators/Proxy/this-binding need pure-JS framing |

**Known issues / v3.10 candidates:**

*High-priority:*
- **`[a-z]{3,}` tag-regex collision with code identifiers.** `prop`, `key`, `idx`, `name`, `length`, `type`, `value` all collide with the markdown tag parser. Workaround was awkward (single-letter names in code examples). Cleaner long-term: migrate to `<<tag>>...<</tag>>` syntax that won't collide with code in any planned language. **Must resolve before Rust authoring** — Rust hits `[ref]`, `[mut]`, `[box]`, `[Vec]` immediately.
- **SQL source markdown not available.** v3.8b SQL bundle is an opaque carry-forward in v3.9. Future v3.x changes to SQL content require regenerating markdown source from the ANSI bundle (lossy) or hand-authoring fresh. **Reconstruct in v3.10 before v4.0 begins** so all three tracks rebuild symmetrically through build.py.
- **Intermediate-tier ML-adjacency drift.** Three-question realignment (Q26 → parallel checkpoint fetch, Q27 → per-class accuracy counts, Q29 → handling Promise that resolves to invalid logits). No structural changes, just reframing.

*Medium-priority:*
- Q47 prompt seam (this-binding gotcha asks user to add method to partial class, then expects top-level binding from harness). Cleaner v3.10 redesign: free function `delayed_increment(start)` returning Promise resolving to `start + 1`, gotcha is closure over `start`. Same lesson, simpler shape.
- Q23/Q24 alternate solutions documented as accepted. If user feedback reports confusion, tighten then.
- Cheatsheet word count over target (565 vs ~500). Tier files 4,047 vs ~2,500. Acceptable; matches SQL/Python density.

*Low-priority:*
- JS engine status indicator: `js: ready` shows immediately on construction (synchronous-ready) where Python shows `loading → ready`. Consider `js: idle` until first evaluate to match visual rhythm.
- Cross-terminal nav pills: 12 hardcoded `['python','sql']` sites patched. Spot-check on first browser run for any UI affordance that wasn't covered.

**What I'd do differently next time:**
1. Set tag-regex compatibility as a v3.9 design deliverable, not a discovery. Cost ~30 minutes mid-build.
2. Plan SQL source reconstruction before sprint, not during. The two-step build was an honest workaround but suboptimal.
3. Run lint pass earlier and more often — every 5 questions, not just at build time.

**Test artifacts** (not shipped, useful reference for v3.10): smoke tests in `bank/`, sandbox tests in `sandbox-tests.js`, e2e harness in `e2e-final.js`. Boot source preserved separately as `boot.js` (488 lines) so v3.10 can edit it without round-tripping through the embedded form.

---

## v3.10 — Consolidation: tag syntax, SQL source rebuild

**Duration estimate:** 2-3 sessions
**Risk level:** medium (touches build system, content format, three tracks of existing content)

*Why this version exists:* v3.9 surfaced three pieces of technical debt that need to be paid down BEFORE v4.0 (Rust) begins, because Rust authoring will hit identical issues in worse forms. v3.10 is pure consolidation — no new tracks, no new features, no new questions. Its job is to leave the codebase ready for v4.0.

```
Ghost Training Terminal v3.10 — consolidation pass before v4.0.

CONTEXT
- Building on v3.9 (JavaScript track shipped, with three known technical-debt
  items flagged in the v3.9 handoff that must be resolved before adding more
  tracks).
- This version adds NO new tracks, NO new features, NO new questions. It's
  pure cleanup.
- The work here is load-bearing for v4.0. Rust authoring will hit identical
  problems in worse forms (more identifier collisions, no usable carryover
  patterns) if v3.10 doesn't ship first.

UPLOAD REQUIRED
This version touches build.py, the content file format, all three existing
content trees, AND the embedded JsEngine. Upload protocol is the FULL
new-track upload:
- index.html
- CHANGELOG.md
- build.py
- src/index.template.html
- src/content/python/ (entire directory)
- src/content/javascript/ (entire directory)
- src/content/sql/ (whatever exists — probably just README.md placeholder)
- README.md
- The v3.9 handoff notes section from PROMPTS.md (for SQL bundle context)

TASK 1 — Tag syntax migration (highest priority — blocks v4.0)
Current syntax `[amber]...[/]` collides with code identifiers in JS (and
will collide worse in Rust: ref, mut, box, Vec, Option, Result all match
[a-z]{3,}). Migrate all content to a distinct tag-open syntax.

Recommended target syntax: <<amber>>...<</amber>>
Reasoning:
- Distinct from any language syntax in the planned tracks
- Unambiguous closer (matches the open tag explicitly)
- Mechanical migration via regex
- Lints can detect mixed usage during migration

Implementation steps:
1. Update build.py parser to recognize <<TAG>>...<</TAG>> syntax
2. Add a transitional MIXED mode that accepts BOTH old and new syntax,
   with a warning on old-syntax usage. This lets us migrate file-by-file.
3. Migrate all existing content files (Python, JS, SQL once reconstructed)
   from [tag] to <<tag>>. Use `python3 build.py --migrate-tags` as a
   one-shot tool.
4. Once all content is migrated, set MIXED mode to ERROR on old syntax.
5. Update README authoring conventions to reflect new syntax.

Testing: each migrated file should produce byte-identical bundle output
to the pre-migration file. The build.py --check pass + a hash comparison
verifies this.

TASK 2 — SQL source reconstruction (blocks v4.0)
v3.9 carried forward the v3.8b SQL bundle as opaque overlay because the
source markdown wasn't available. v3.10 reconstructs `src/content/sql/*.md`
so the build pipeline is symmetric across all three tracks.

Approach:
1. Write a one-shot reverse-converter from the v3.8b ANSI bundle back to
   markdown with [amber]/[dim]/etc tags. ~100 lines of Python. Lossy on
   exact whitespace inside code blocks; that's expected.
2. Hand-correct the lossy parts in a single review pass against the
   original ANSI output (compare side by side).
3. Run build.py with the reconstructed source. The output bundle must
   match the v3.8b bundle byte-identically (or identify each diff and
   document why).
4. Once SQL rebuilds cleanly, the v3.9 two-step overlay step is removed
   from build.py. SQL becomes architecturally identical to Python and JS.

Sequencing: do TASK 1 first, so the SQL reconstruction targets the new
<<tag>> syntax directly, not the old [tag] syntax that's about to be
migrated.

TASK 3 — Intermediate JS calibration realignment
v3.9 shipped Intermediate at 60/0/40 (target was 30/30/40). Three
question-level reframings move the ratio to target without changing
the JS skill being tested:

- Q26 (Promise.all): reframe around fetching three model checkpoints
  in parallel. Same Promise.all skill; ML-adjacent framing added.
- Q27 (Object.values/entries): reframe around per-class accuracy counts.
  Same iteration pattern; ML-adjacent framing added.
- Q29 (try/catch): reframe around handling a Promise that resolves to
  invalid logits (NaN or out-of-range values). Same error-handling
  pattern; ML-adjacent framing added.

Each is a prompt rewrite plus possibly a setup data tweak. No structural
changes. Verify smoke tests still pass after edits.

TASK 4 — Q47 redesign
Current Q47 has a contract seam: asks user to add tick() method to a
partial Counter class, then expects test harness to bind next_value at
top level. Works but reads as two tasks.

Redesign as: free function `delayed_increment(start)` that takes a
number and returns a Promise resolving to start + 1. The gotcha is a
naive implementation using a regular function inside .then loses access
to captured start (closure issue, mirrors the this-binding lesson).
Same pedagogical lesson, simpler shape.

EXPLICIT NON-GOALS
- No new tracks (Rust waits for v4.0).
- No new questions in any track.
- No new features (no new commands, no UI changes, no engine changes
  beyond tag-syntax recognition in build.py).
- No content edits beyond TASK 3's three Intermediate reframings and
  TASK 4's Q47 redesign. Don't sweep through other tiers "while you're
  in there" — out of scope.

DELIVERABLES
- Migrated content files in <<tag>> syntax across Python, JS, and
  reconstructed SQL.
- Reconstructed src/content/sql/*.md producing byte-identical SQL bundle
  vs v3.9 (or documented diffs).
- build.py with new tag parser + transitional MIXED mode + migration tool.
- v3.9 two-step SQL overlay removed from build.py.
- Updated README with new authoring conventions.
- CHANGELOG entry documenting all four tasks.
- Three Intermediate JS questions reframed for ML-adjacency.
- Q47 redesigned for cleaner contract.
- Final build artifact with new md5 hash logged in CHANGELOG.
- Zip.

VERIFICATION
- build.py --check passes clean.
- All three tracks rebuild byte-identically (Python, JS) or with documented
  diffs (SQL after reconstruction).
- All smoke tests still pass after content migration.
- Tag-collision test: author a sample paragraph using `prop`, `key`, `idx`,
  `ref`, `mut`, `box`, `Vec`, `Option`, `Result` as inline code. The build
  must produce the right output (these as literal text, not parsed as tags).
- Manual browser pass: open the rebuilt index.html, walk through one
  question per tier per track, verify rendering is unchanged.

KNOWN RISKS
- Tag migration is intrusive — touches every content file. A test that
  rebuilds each migrated file and compares hash to pre-migration output
  is the right safety net. If hashes drift, find out why before
  proceeding.
- SQL reconstruction is partly art (the lossy whitespace correction).
  Budget extra session time for this. Don't rush.
- Both migrations together could create a bundle that drifts from v3.9
  on byte-level even when content is logically identical (e.g. tag-open
  byte sequences differ). The bundle will not be byte-identical to v3.9
  by design; it should be SEMANTICALLY identical (same rendered output
  in the terminal). Document this in the changelog so future maintainers
  don't try to hash-match against v3.9.

POST-v3.10
v4.0 (Rust) becomes safe to start. The build pipeline is symmetric across
all three existing tracks. The tag syntax won't collide with Rust
identifiers. v4.0's prompt should explicitly verify v3.10 has shipped
before authoring begins.
```

### v3.10 handoff notes
*Completed: 2026-05-06*

**Build artifact:**
- `index.html` — 375,635 bytes (vs v3.9's 374,334; +1,301 from version-string changes, four question rewrites, and SQL bundle rebuild from source rather than overlay)
- md5: `7f55f5c1045b0068a378d58b79b23478`
- Source zip published as `ghost-training-v3.10.zip`

**Shipped (all four planned tasks complete):**

1. **Tag syntax migrated** from `[tag]...[/]` to `<<tag>>...<</tag>>` across every content file. 12 files updated, 2,586 tag tokens rewritten by `build.py --migrate-tags`. The migration tool stays in source — idempotent, useful for any future fork still on legacy syntax. Named closers required (`<<amber>>foo<</amber>>`, not `<<amber>>foo<</>>`); parser now catches mismatched-name closers, which the legacy `[/]` form couldn't surface.

2. **SQL source markdown reconstructed.** `.work/reconstruct_sql.py` walks the v3.9 SQL bundle's ANSI strings with a stack-based color tracker and emits markdown directly in the new `<<tag>>` syntax (skipping the legacy intermediate). Cheatsheet + 5 tier files + a track README documenting the reconstruction history. The reconstructed source rebuilds to a SQL bundle byte-identical to v3.9. The v3.9 two-step overlay step is gone — `build.py` is now a single-step build for all three tracks.

3. **Intermediate JS ML-flavor calibration** — Q26/Q27/Q29 reframed without changing the JS skill being tested:
   - Q26 (Promise.all): `fetch_a/b/c` → `fetch_checkpoint_a/b/c`, binding `total` → `total_mb`, prompt mentions model weight shards. Numbers preserved (10+20+30=60).
   - Q27 (Object.values): `status_counts` (Open/Closed/InProgress/OnHold) → `class_correct` (cat/dog/fish/bird), binding `total_orders` → `total_correct`. Sum unchanged (22).
   - Q29 (try/catch): replaced `safe_parse_count(jsonStr)` (sync JSON.parse) with async `safe_predict(input)` calling provided `predict_logits(input)`. Test cases cover normal/rejection/NaN/negative. Same try/catch + validate-result + return-null shape.

4. **Q47 redesigned.** Two-part Counter contract collapsed to a single free function `delayed_increment(start)`. Same lexical-scope-in-callbacks lesson, different angle: a regular `function(start) { ... }` inside `.then` shadows the outer `start` with its own parameter, and since `Promise.resolve()` with no argument resolves to undefined, you get NaN. The arrow form `() => start + 1` closes over the outer `start` cleanly. Smoke test verifies the gotcha actually produces NaN as the prompt claims.

**Verification record:**

- `python3 build.py --check` clean (0 warnings)
- Per-track bundle md5 audit:
  - sql `aeeb91131bf238fb34e6cacd0c949390` — byte-identical to v3.9 reference
  - python `7e7270968e5d7ca25f919f03c76aa828` — byte-identical to v3.9 reference
  - javascript `f28fcdd26a2a6aacf321ba6569fdfff5` — byte-identical to v3.9 reference (track content bundle = cheatsheet + tier prose + examples; question-array changes live in template body, outside the bundle placeholder)
- Tag-collision smoke test: 12/12 collision-prone identifiers (`[ref]`, `[mut]`, `[box]`, `[Vec]`, `[Option]`, `[Result]`, `[prop]`, `[key]`, `[idx]`, `[obj]`, `[arr]`, `[tmp]`) pass through as literal text under the new parser
- Question smoke test: 5/5 pass — canonical solutions for Q26/Q27/Q29/Q47 all grade correctly, and the documented closure-shadow gotcha for Q47 actually produces NaN under a naive shadowed-param implementation
- Negative test: injecting one legacy `[dim]` tag back into a content file fails the build with `[ERROR legacy-tag-syntax]` (proves the `TAG_LEGACY_MODE = "error"` kill switch is wired correctly)
- Reproducibility: extracting the deliverable zip into a fresh location and running `python3 build.py` produces md5 `7f55f5c1045b0068a378d58b79b23478` exactly

**Architectural decisions locked this sprint** (v4.x must honor):

1. **Tag syntax:** `<<tag>>...<</tag>>` with named closers. Legacy `[a-z]{3,}` regex is gone. `TAG_LEGACY_MODE` in `build.py` defaults to `"error"` post-cutover; switching to `"warn"` is for migration-window scenarios only (e.g. accepting a fork's contributions). Anyone editing content who slips back into `[tag]` syntax gets an immediate build failure.

2. **Build pipeline symmetric across all three tracks.** No more two-step "build then overlay SQL bytes from v3.8b" workflow. `python3 build.py` is a single-step build. v4.0 (Rust) authoring will follow the same `src/content/<track>/` shape — `cheatsheet.md` + `tier-{introductory,amateur,intermediate,experienced,master}.md`.

3. **Mismatched-closer detection is now a structural error.** Becomes useful in v4.0 when authors are working through long files with multi-line tag spans — the parser tells them which closer was wrong, which the anonymous `[/]` form couldn't.

4. **Question reframings preserve the JS skill being tested.** Q26/27/29 stayed in the same skill family (Promise.all + sum, Object.values + reduce, try/catch + validate-result). Only the prompt strings, binding names, and setup data were ML-themed. This is the template for any future tier-calibration sweep — never change the underlying skill, only the framing.

5. **Q47's "lexical scope in callbacks" lesson generalizes beyond this.** v3.9's question taught arrow-vs-function via this-binding inside Promise.then. The v3.10 redesign teaches the same idea via parameter shadowing — a different angle on the same underlying point. Either is defensible; the v3.10 form is structurally simpler (single free function, single contract).

**ML-flavor ratio (Intermediate, post-v3.10):**

| Question | v3.9 framing | v3.10 framing | Bucket |
|----------|--------------|---------------|--------|
| Q21–Q25 | mixed | unchanged | varies |
| Q26 | pure JS | ML-adjacent | A (model checkpoint shards) |
| Q27 | pure JS | ML-adjacent | A (per-class accuracy counts) |
| Q28 | explicit ML | unchanged | E (dot product) |
| Q29 | pure JS | ML-adjacent | A (logits + numerical instability) |
| Q30 | explicit ML | unchanged | E (euclidean distance) |

Intermediate ratio moves from v3.9's actual 60/0/40 (P/A/E) toward the 30/30/40 target. Three reframings × ~10% each ≈ 30% adjacency added. Master tier was not in scope for v3.10 (Q47 redesign was contract cleanup, not reframing) and remains at v3.9's 40/10/50 — flagged for a future calibration sweep but not blocking v4.0.

**Known issues / follow-ups for v4.0** (low-priority sweep candidates, not blocking):

- Cross-references in tier markdown are now slightly imprecise. JS Intermediate's JSON section says "See `<<qid:js_int_09>>`" but Q29 is no longer specifically about JSON.parse — it's now about async error handling against a Promise that may reject or resolve to invalid logits. JS Master's THE THIS BINDING GOTCHA section says "See `<<qid:js_mas_07>>`" but Q47 is no longer specifically about this-binding — it's about parameter shadowing inside `.then` callbacks. Both references stay defensible (broader skill family: try/catch around async work; lexical-scope-in-callbacks). Edits to surrounding teaching prose were out of scope for v3.10's "no content sweeps" non-goal. Sweep candidate during v4.0 authoring when new Rust content gives a natural reason to revisit JS teaching prose.
- Master tier ML-flavor still at 40/10/50 vs the 10/10/80 target. Generators/Proxy/this-binding sections justify pure-JS framing. Defensible as-is; revisit only if explicit-ML coverage feels thin in user feedback.

**What I'd do differently next time:**

1. Author the migration tool (`build.py --migrate-tags`) before starting per-file rewrites. v3.10 did this in the right order; preserve the rhythm for any future syntax-level sweep.
2. Verify per-track bundle md5 against the previous version before claiming the migration was non-substantive. The byte-identical audit is the cheapest possible proof that "tag syntax changed but nothing else did."
3. Keep the negative test (inject legacy syntax → build fails) in the repo as a permanent regression guard, not just a one-time verification. Currently it lives only in the work-traces zip; consider adding a `tests/` directory in v4.0 and moving it there.

**Test artifacts** (not shipped, useful reference for v4.0):

- `.work/reconstruct_sql.py` — ANSI-to-markdown reverse converter for SQL. Pattern reusable if any other track's source ever needs reconstruction.
- `.work/snapshot_bundles.py` — per-track bundle hash audit script. Run with `--label <name>` to snapshot the current state of each track's bundle md5/size; useful for validating that a refactor didn't change rendered output.
- `.work/smoke_v310.js` — Node-based question smoke test that mirrors the JsEngine grading shape (setup + canonical solution + assertion-expression in one async IIFE). Template reusable for v4.0 if a similar in-language smoke harness is needed.
- Full audit trail published as `ghost-training-v3.10-work-traces.zip` alongside the main deliverable.

---

## v4.0 — Rust track

**Duration estimate:** 5-8 sessions
**Risk level:** HIGH (new pattern-match paradigm, new territory)

```
Ghost Training Terminal v4.0 — add Rust as the fourth track.

CONTEXT
- Building on v3.10 (consolidation pass shipped 2026-05-06 — tag syntax
  migrated to <<tag>>...<</tag>>, SQL source reconstructed, JS Intermediate
  calibration realigned, Q47 redesigned). Build pipeline is now symmetric
  across all three existing tracks.
- Rust is the FIRST pattern-match track — no in-browser execution possible.
- Pattern-match infrastructure built here will be reused by C++ and CUDA
  in v4.1. Design it to be extensible.
- Rust chosen before C++ because its stricter syntax makes pattern-matching
  easier. Proving the approach works on Rust validates it for C++.
- Pattern-match engines do NOT need the IIFE-wrapped execution model that
  JsEngine uses (no scope-leak issues because no execution happens).

PRECONDITION CHECK (sanity-check before authoring; v3.10 should already
satisfy these but verify on first session)

THESE CHECKS MUST PRODUCE VISIBLE TOOL-CALL OUTPUT. Don't summarize results
— show the actual `view` output, the actual `bash_tool` stdout. The user
will be checking that your claims match real artifacts.

1. View the first 30 lines of src/content/python/cheatsheet.md with the
   `view` tool. Confirm <<tag>>...<</tag>> syntax (NOT [tag]...[/]). Show
   the output. v3.10 migrated all content; legacy syntax means upload is
   wrong or pre-v3.10. STOP if found.

2. Run `python3 build.py --check` via `bash_tool` against the full source
   tree. Show the actual stdout. Should be "Lint clean." per v3.10's
   verification record.

3. List `src/content/sql/` via `bash_tool` (`ls -la src/content/sql/`).
   Show the output. Should contain cheatsheet.md + 5 tier files +
   README.md. If only README.md is present, upload is pre-v3.10. STOP.

4. Grep build.py for TAG_LEGACY_MODE via `bash_tool`. Show the matched
   line. Should show `TAG_LEGACY_MODE = "error"`. If "warn", upload is
   mid-migration. STOP.

5. NEW for v4.0: Verify the template has NO existing Rust scaffolding.
   Run via `bash_tool`:
   `grep -c "RustEngine\|rs_intro\|rs_amateur\|rs_intermediate\|rs_experienced\|rs_master" src/index.template.html`
   Expected: 0. If non-zero, ANOTHER SESSION HAS PARTIALLY AUTHORED v4.0
   AGAINST THIS REPO. Surface to the user immediately — do not build on
   top of unknown scaffolding. (Context: v4.0's first attempt 2026-05-10
   fabricated a non-existent scaffold and built on top of it. This check
   prevents that failure mode at session start.)

If any precondition fails, surface to the user with the actual tool-call
output. Don't try to work around missing v3.10 prerequisites or fabricated
v4.0 scaffolding — that re-creates the exact technical debt v3.10 was
built to eliminate AND the exact failure mode that sank v4.0's first
attempt.

SCOPE FOR THIS VERSION
1. New RustEngine class (pattern-match only) following existing engine interface.
2. New 'pattern' assertion type with these fields:
   - required: array of substrings that MUST appear in user answer
   - structure: canonical answer used for whitespace-normalized compare
   - alternatives: object mapping equivalent tokens (e.g. |w| ≈ |&w|)
   - forbidden: array of substrings that must NOT appear (e.g. .clone()
     when the question tests borrowing)
3. Grammar-lite error detection: when a pattern assertion fails, surface
   TARGETED feedback — "missing ;", "missing mut", "wrong borrow syntax" —
   not just "incorrect".
4. Author 50 graded questions (10 per tier).
5. Author Rust learning content:
   - rust/cheatsheet.md (~600 words — Rust has a lot of vocabulary)
   - 5 tier-*.md files (~2800 words total)
6. ASCII diagrams where they earn their place — ownership model especially.

TIER PROGRESSION
- Introductory: let/let mut, type suffixes, basic fn
- Amateur: Vec/String/Option/Result, if let, match on Option
- Intermediate: ownership + borrowing, iterators, closures
- Experienced: traits, generics, lifetimes (IN CONTEXT, not abstract puzzles)
- Master: async/.await, unsafe, FFI basics, Rc/Arc/Box

EXPLICIT NON-GOALS
- No C++/CUDA this version.
- No wasm-rust compilation (real execution deferred to future work).
- No lifetime annotation puzzles without context — lifetimes in Rust are
  notoriously hard to teach; always show them anchored to a real scenario
  (struct holding a reference, fn returning a reference, etc.).

PATTERN-MATCH DESIGN (CRITICAL — STAGED REVIEW)
- Start restrictive, loosen after observing failures.
- Author the design in three explicit stages with review gates between them.
  This was learned from v4.0's first attempt, which fabricated scaffolding
  and reported false test results because the work wasn't broken into
  reviewable artifacts:

  STAGE 1 — Design proposal (paper only, no code):
  - The four-field schema with explicit semantics (whitespace, case,
    layering, alternatives mechanics)
  - 2-3 worked example assertions across difficulty tiers
  - RustEngine grading pseudocode showing field interaction order
  - Grammar-lite error detection rules with explicit ordering
  - QA harness format showing accept/reject test data shape
  - User reviews and signs off before any code gets written.

  STAGE 2 — Implementation against locked spec:
  - Implement RustEngine, pattern assertion type, build.py changes
  - Author 5-10 representative questions across 2 tiers (recommend
    Introductory + Experienced — tests both ends of complexity)
  - Author the QA harness in tests/ directory (permanent regression home)
  - REQUIRED: Show actual file creations via create_file tool calls.
    Show actual bash output of build.py --check passing. Show actual
    bash output of QA harness running with green/red counts visible.
  - User reviews real artifacts and signs off before Stage 3.

  STAGE 3 — Sprint full authoring:
  - Remaining 40-45 questions across remaining tiers
  - Cheatsheet + 5 tier files
  - README/CHANGELOG/PROMPTS updates
  - Final build, zip, handoff

- The "alternatives" mechanic is the hardest part to get right — too loose
  accepts wrong answers, too strict rejects correct ones. Err toward strict
  initially; loosening is cheaper than tightening.
- If after Stage 1 the grammar feels fragile, RESET the design before
  Stage 2 begins. Don't push through fragile design hoping it firms up
  during implementation.

QA HARNESS (MANDATORY — SHOW ACTUAL OUTPUT)
- Write a small test file at tests/qa_harness.py that for each question
  feeds 3-5 known-correct formulations and 3-5 known-wrong ones, verifies
  the grader agrees AND that wrong cases produce specific error messages.
- Run this on every question. SHOW THE ACTUAL bash_tool OUTPUT of the
  harness running. Do not summarize "all green" without the underlying
  stdout visible — fabricated test results were the proximate cause of
  v4.0's first attempt failing.
- The harness lives permanently in tests/qa_harness.py (not in /tmp,
  not in scratch directories). It's a regression guard, not a one-shot
  validation tool. v4.1 will reuse it for C++ and CUDA.
- Output format: per-question pass/fail count, plus full failure detail
  for any reject case where the actual error message doesn't contain
  the expected substring. Failures block ship.

ML FLAVOR
- Tensor structs, activation functions as traits, simple SIMD-style ops.
- AVOID actual ML libraries (ndarray, tch) — keep stdlib-only.

DELIVERABLES
- RustEngine + pattern assertion type.
- QA harness with passing results for all 50 questions.
- All content files.
- README updated.
- Zip.

KNOWN RISKS
- This is the highest-risk version in the whole plan. If after 2-3 sessions
  the pattern-match grammar feels fragile, RESET and redesign rather than
  pushing through.
- Testing pattern assertions is hard because there's no "did it execute?"
  sanity check. The QA harness is load-bearing — don't skip it.
```

### v4.0 handoff notes
*Completed: 2026-06-22*

**Build artifact:**
- `index.html` — 509,223 (build.py char count, consistent with prior entries; 510,596 bytes via `wc -c`, delta is multi-byte UTF-8)
- md5: `97614561a6e9e885c9398de1531eb3a7`
- Source zip: `ghost-training-v4.0.zip` (published at ship)

**Shipped (Rust track, complete):**

1. **`RustEngine`** — the first pattern-match (non-executing) grader. Grades forbidden → required → structure-with-alternatives, then grammar-lite tag-driven refinement of structure-mismatch failures. Built in Stage 2; **graded all 50 questions through Stage 3 with zero modifications** — the headline validation of the Stage 1 design.

2. **50 questions, 5 tiers, 10 each.** Introductory (let/mut, types, println!, Vec, tuples, if/else, match, fn), Amateur (Vec/String/Option/Result, if let, match-on-Option), Intermediate (ownership/borrowing, iterators, closures incl. closure-deref), Experienced (traits, generics, lifetimes-in-context, Result+`?`), Master (async/.await, smart pointers, unsafe/FFI, dot-product capstone `rs_mas_10`).

3. **`RUST_ALTERNATIVES_LIBRARY`** — 5 named equivalence groups. 2 exercised by v4.0 questions (`NUMERIC_LITERAL_SUFFIXES`, `CLOSURE_DEREF_VARIANTS`); 3 reserved (see Known issues).

4. **Content tree** `src/content/rust/` — cheatsheet (~608 words) + 5 tier files (~2,800 total), `<<tag>>` syntax, ASCII ownership diagrams in the cheatsheet and Intermediate file.

5. **`start rust` wired** — RustEngine at boot + engine-selector ternaries; rust added to KPI rollups, left rail, ticker, cmdGoto, reset counts, footer status, help/usage/placeholder text. `build.py` made rust-aware (track tuple + qid regex widened to 200 qids).

6. **Version stamped v4.0** — footer, both boot banners, CONTENT_BUNDLE comment, README badge. (CHANGELOG entry = the 5th stamp site, authored with this handoff.)

**Verification record:**

- QA harness: **168 accept / 0 fail, 151 reject / 0 fail** across 50 questions.
- Content sweep (6 files): stray-marker scan 0, block-level zero-accept 0 across 20 examples, targeted lint 0.
- `build.py --check` clean with rust in the loop; 200 qids extract (50/track).
- `node --check` on the inline script clean after wiring (no syntax break).
- **Ship-gate verification (complete):** JS↔Python parity — 319 cases / 0 disagreements; sabotage on `rs_mas_10` passed (break flips all 5 accepts to fail, revert clean); per-track audit — SQL/Python/JS byte-identical to v3.10, rust new (`e95604cf…`); browser smoke test **PASS** (architect-confirmed, screenshot evidence — route/render/grade/advance/nav/stamps all confirmed live). **Task-9 wiring is now VERIFIED** (was provisional until this smoke test).

**Architectural decisions locked this sprint** (v4.1 must honor):

1. **Pattern-match grading order is fixed:** forbidden → required → structure+alternatives → grammar-lite. Any new track reuses this; changing it invalidates every question's qa block.
2. **Required holds the invariant prefix; alternatives hold the parametrization.** The dominant authoring pitfall (8 appearances across the bank). A parametrized token in `required` makes its alternative dead code.
3. **A library group's equivalence claim is tier-relative** — and the only error class the harness cannot catch (semantic, not mechanical). Verify a group fits a question's *lesson* before reusing it (`rs_exp_10`).
4. **Lint verifies structure, not rendered correctness.** The rendered-output stray-marker scan is a required gate alongside `build.py --check` for any `<<tag>>`-content track.
5. **No adjacent `>>` in rendered visible text** (render-safety + detector-trustworthiness). Teach nested types via inferred code.
6. **Lifetimes only in context** — never abstract puzzles (honored: `Doc<'a>`, `Window<'a>` hold real borrows).

**ML-flavor ratio per tier (target / actual):**

| Tier | Target (P/A/E) | Actual | Status |
|---|---|---|---|
| Introductory | 100/0/0 | **100/0/0** | on target |
| Amateur | 60/20/20 | **60/20/20** | on target |
| Intermediate | 30/30/40 | **30/30/40** | on target |
| Experienced | 20/20/60 | 50/10/40 | **forced overshoot** — Stage 2 pre-locked 5 pure questions before ML-targets applied; ceiling was 50/x/x. Precedent: v3.9 JS Experienced landed 50/0/50. |
| Master | 10/10/80 | **10/10/80** | on target (honest hit — `rs_mas_06` raw-pointer unsafe is pure by nature; ML-framing it would be the contrivance) |

Three tiers dead-on, Master dead-on, Experienced the one divergence — and *forced*, not elective (documented in the CHANGELOG as a deliberate decision, not a calibration miss).

**Known issues / follow-ups for v4.1** (none blocking):

- **2-of-5 library coverage.** `RESULT_PROPAGATION` is mis-scoped (it equates `?` with the panic-forms `.unwrap()`/`.expect()`; rename to `RESULT_VALUE_EXTRACTION` or split). `STRING_TYPE_VARIANTS` / `ITER_COLLECT_VARIANTS` unused — no question's prompt scope needed them; not forced in.
- **qid cross-references deferred.** Regex now accepts `<<qid:rs_...>>`, but Rust content ships without them. Post-v4.0 polish.
- **Math-operator errors → "structure mismatch."** Grammar-lite has no arithmetic-intent rule; a documented boundary of pattern-match grading, not a gap.
- **JS-prose cross-ref sweep still deferred (carried from v3.10, verified still present).** v3.10 reframed Q29/Q47 but left two now-imprecise content cross-refs, flagged then as a v4.0 sweep candidate; v4.0 focused on Rust and didn't do it. Still live: `tier-intermediate.md` cites `<<qid:js_int_09>>` under its `# JSON` heading though Q29 is now about async error-handling, not JSON.parse; `tier-master.md` cites `<<qid:js_mas_07>>` under `THE THIS BINDING GOTCHA` though Q47 is now parameter-shadowing. Refs stay defensible (broader skill family); the headings are imprecise. (Distinct from task 10's README refresh, which is the only README content v4.0 touches.)

**What I'd do differently next time:**

1. **Apply ML-flavor targets to the Stage 2 representative slice.** Experienced overshot only because its 5 Stage-2 questions were authored pre-target. A future track should tag the representative slice with its eventual ratio so the full tier can hit target.
2. **Add the rendered-output stray-marker scan to `build.py` itself**, not just the authoring harness. The malformed-into-literal blind spot is a permanent lint gap; closing it in the build is a small, high-value change.
3. **Author content via inferred code from the start** where types nest — reaching for explicit annotations first (then walking them back for the `>>` hazard) cost a re-draft on `tier-master`.

**Reusable techniques v4.1 (C++/CUDA candidate) inherits:**

These are what the sprint's findings set up for a non-executing C++/CUDA track — the techniques transfer directly to template-syntax nesting and GPU-primitive framing:

- **Inferred-code for nested generics** → C++ `vector<vector<float>>` / `unique_ptr<Tensor<float>>` shown via `auto`/inference to avoid adjacent `>>` in rendered visible text (the C++ `>>` hazard is identical, and worse — C++ even had the historical `>>` template-close lexing bug).
- **Bridge-example technique** (use the form the next tier replaces; capstone-adjacent previews the skill-category via a different primitive).
- **Rendered-output stray-marker scan** as a content gate (lint verifies structure, not render).
- **Regex-verified-by-count** (a matcher fix is verified by match-count vs a known total, never by absence-of-error).
- **The QA harness** (`tests/qa_harness.py`) is the permanent regression home; v4.1 extends it for C++/CUDA grading.

**Exploratory candidate (lower readiness than C++/CUDA): LangChain/LangGraph.** Flagged as a future track of interest (learning-interest motivated), but with significant open design problems that distinguish it from the C++/CUDA candidate:
- These are rapidly-evolving Python *frameworks*, not stable languages. API churn means "correct" code shifts across versions — a moving target the pattern-match grader (built for stable syntax) may not fit.
- Much of the actual skill is architectural (chain/graph composition) rather than syntactic — the opposite of what pattern-match grading captures well.
- OPEN QUESTION before this is a real candidate: does the pattern-match paradigm fit a framework track at all, or would it need a different grading approach (structural-AST matching, or partial execution against a pinned framework version)? Unresolved; needs its own design pass — not a "just author 50 questions" track like C++/CUDA would be.
Recorded as a genuine learning-interest direction, but explicitly NOT at C++/CUDA's readiness — C++/CUDA inherits worked-out techniques and is a clean fit for the existing engine; LangChain sits below it as exploratory.

**Test artifacts** (not shipped, reference for v4.1):
- `docs/v4.0-authoring-notes.md` — the full per-question authoring record and the source for the CHANGELOG "Documented" principles. Stays in the repo.
- The content-verification one-liners (block-level zero-accept, stray-marker scan via `build_track_bundle`) — reusable as-is for v4.1 content.

---

## v4.1 — C++ track + CUDA specialization

**Duration estimate:** 6-10 sessions
**Risk level:** medium-high (two tracks + extending pattern-match)

*Rationale for combining:* C++ and CUDA share ~60% of their infrastructure.
Pattern-match engine from v4.0 extends to both. CUDA is syntactically C++ with
extensions, and many ML-adjacent C++ patterns (tensor ops, SIMD intrinsics,
memory layout) are directly relevant to CUDA. Authoring them together reduces
context-switching. CUDA remains a SPECIALIZATION branch unlocked after C++
Intermediate, not a peer track.

```
Ghost Training Terminal v4.1 — add C++ track + CUDA specialization.

CONTEXT
- Building on v4.0 (Rust pattern-match infrastructure shipped).
- Folded from originally-separate v4.1 and v4.2 because C++ and CUDA share
  substantial infrastructure and content overlap.
- C++ is a peer track (5 tiers, 50 questions, normal progression).
- CUDA is a SPECIALIZATION, unlocked only after C++ Intermediate cleared.
  Fewer questions authored per tier (~6-8 instead of 10) — it's advanced content,
  not a full track. NOTE: revisit this — may end up 10/tier if content is dense.
- This is the final planned version. After this, 6-track goal complete.

SCOPE FOR THIS VERSION

PART A — C++ TRACK
1. New CppEngine class — pattern-match, reusing v4.0 assertion type.
2. Extend pattern-match with C++-specific tolerance rules:
   - brace-on-same-line vs next-line
   - `const T` vs `T const`
   - `*` position on pointers (`T* x` vs `T *x` vs `T * x`)
   - optional `std::` prefix (accept with or without `using namespace std;`)
   - optional `inline`, `constexpr`, `static` modifiers where semantically irrelevant
3. Author 50 graded questions (10 per tier).
4. Author C++ learning content:
   - cpp/cheatsheet.md (~700 words)
   - 5 tier-*.md files (~3000 words total)

PART B — CUDA SPECIALIZATION
1. New CudaEngine class, reusing v4.0/v4.1a pattern-match infrastructure.
2. CUDA-specific detectors added to pattern-match:
   - kernel qualifiers (__global__, __device__, __host__)
   - launch syntax <<<blocks, threads>>>
   - thread indexing (threadIdx.x, blockIdx.x, blockDim.x)
   - memory hierarchy qualifiers (__shared__, __constant__)
   - synchronization (__syncthreads())
3. Gating logic: CUDA track locked until user has cleared C++ Intermediate.
   Clear message on attempted `start cuda` before unlock, showing which track
   and tier they need to reach.
4. "Show canonical answer" affordance: after 3 incorrect attempts on the same
   question, offer to reveal a canonical answer with explanation. UNIQUE TO
   CUDA because pattern-match feedback is less helpful here.
5. Author questions:
   - Introductory: kernel qualifier, thread indexing, launch syntax
   - Amateur: vector add, bounds checking, memory transfer concepts
   - Intermediate: shared memory, tiling, __syncthreads
   - Experienced: warps, coalescing, occupancy, streams
   - Master: reductions, warp shuffles, Tensor Cores basics, profiling intuition
6. Author CUDA learning content:
   - cuda/cheatsheet.md (~500 words) — MUST include ASCII thread/block diagram
   - 5 tier-*.md files (~2800 words total)

C++ VERSION TARGET (resolve before authoring)
- Target C++17 as baseline (widely supported in production).
- Mention C++20 concepts ONLY at Master tier, framed as "future direction".
- Do NOT teach C++23 or later.

C++ TIER PROGRESSION
- Introductory: basic types, functions, std::cout
- Amateur: vectors, strings, range-for, auto, references
- Intermediate: classes, constructors, destructors, operator overloading
- Experienced: templates, smart pointers, move semantics, RAII
- Master: SFINAE, constexpr, memory layout, perf patterns

EXPLICIT NON-GOALS
- No AMD/HIP content this version (could be post-v4.1 future work).
- No OpenCL, SYCL, Metal, WebGPU.
- No actual GPU execution or validation.
- No questions requiring code execution to verify behavior.
- No pre-C++11 style (no raw new/delete outside of "why we don't do this").

ML FLAVOR
- C++: simple matrix class, iterator-based dot product, mini Tensor template.
  At Master tier: light SIMD intrinsics, memory layout of a tensor.
- CUDA: reductions, matrix mul tiling, activation function kernels. Heavy ML
  emphasis is natural because CUDA's real-world use is overwhelmingly ML.

DELIVERABLES
- CppEngine + CudaEngine + extended pattern-match.
- QA harness results for both tracks.
- All content files.
- Canonical-answer reveal mechanic tested on CUDA.
- README updated with full 6-track story.
- Final zip + deployment notes.

KNOWN RISKS
- Scope is large — 100 questions, 12 content files, 2 engines. Plan for
  6-10 sessions, not 3. If momentum stalls halfway, consider shipping C++
  first (v4.1a) and CUDA separately (v4.1b). Don't force the combined ship.
- C++ accepts MANY valid formulations. Pattern-match tolerance rules will be
  stretched. Expect iteration.
- CUDA pattern-match fairness is weakest. Phrase questions to nudge toward
  ONE idiomatic formulation ("using __syncthreads exactly once", "with
  exactly one bounds check") rather than leaving ambiguous problems.
- CUDA content ages faster than general programming. README should note
  content targets Ampere-era CUDA (roughly 2020 baseline), not Hopper/Blackwell
  specifics.

POST-v4.1 CANDIDATE WORK
- AMD/HIP track as v4.2
- Re-practice / review mode (discussed and deferred)
- Real execution for C++/Rust via wasm
- Telemetry / analytics command
```

### v4.1 handoff notes
*Completed: —*

---

## How to use these prompts

Operational notes for getting the most out of this document.

**1. Start each version in a FRESH Claude session.** The #1 lesson from our
multi-turn work: context accumulates, later turns slow down, transcripts need
compaction. A clean session per version keeps things fast and clear.

**2. Upload protocol — depends on the version's scope.** The minimum upload
varies by what the version touches. Match the upload to the version, not the
other way around. (This was learned the hard way during v3.9 kickoff, where
only `index.html` + `CHANGELOG.md` were uploaded for a build-system-touching
version, blocking the session.)

| Version touches…                          | Upload required                                       |
| ----------------------------------------- | ----------------------------------------------------- |
| Only app JS / CSS / HTML in index.html    | `index.html` + `CHANGELOG.md`                         |
| `build.py` or `src/index.template.html`   | Above + `build.py` + `src/index.template.html`        |
| Existing content under `src/content/`     | Above + ENTIRE `src/content/` directory tree          |
| Adding a new track                        | All of the above + `README.md` (for authoring conventions) |
| Anything questionable / unsure            | All of the above (over-share when in doubt)           |

The full upload for new-track versions (v4.0, v4.1) post-v3.10 is:
- `index.html`
- `CHANGELOG.md`
- `build.py`
- `src/index.template.html`
- `src/content/python/` (entire directory)
- `src/content/sql/` (entire directory — reconstructed in v3.10)
- `src/content/javascript/` (entire directory — added in v3.9)
- `README.md`

Send everything in ONE message. Don't trickle the files. The session needs to
see the full shape at once to plan correctly.

If the GitHub repo is public, sharing the repo URL alone may suffice — but
verify the session can actually read the repo before relying on it.

**3. Paste the ENTIRE prompt block** for the relevant version, including the
"EXPLICIT NON-GOALS" section. Non-goals prevent scope creep mid-version.

**4. Expect multiple work sessions per version.** The duration estimates above
assume ~1-hour sessions. Don't try to finish v4.0 in a single sitting.

**5. End each version with a handoff note.** Fill in the "handoff notes"
section below each prompt after shipping. Future sessions read these to pick
up context.

**6. Keep `CHANGELOG.md` in the repo.** One entry per version. This is the
durable record — memory systems and transcripts are both fragile. The changelog
in git is the source of truth for "what exists in this codebase."

**7. The prompts are draftable.** If a version's scope shifts, update the prompt
in this file BEFORE starting work. Prompt in the file = source of truth for
that version.

**8. Honor review gates.** Some prompts have "CRITICAL — SHOW ME BEFORE
BUILDING" sections. The session is expected to stop at those gates and wait
for confirmation before continuing. If a session blows past a gate,
that's worth flagging and asking them to back up. The gates are there because
some decisions (assertion API, sandbox boundaries, pattern-match grammar)
have one-shot consequences and are hard to walk back after 50 questions
have been authored against them.

**9. Verify agent claims against real artifacts.** When an agent reports doing
work — file edits, test runs, builds, scaffolding "already on disk" — the
corresponding tool calls must be visible in the conversation. Specifically:

- File creations should show `create_file` or `str_replace` tool calls with
  the actual content visible
- Claims about what's "already in the template" before any edits should be
  backed by a `view` tool call with line numbers
- Test runs should show real `bash_tool` output (stdout/stderr), not summarized
  "all green" claims
- md5 fingerprints, line numbers, and edit locations should be reproducible —
  if an agent reports editing line 1928, you should see the `str_replace` or
  `view` tool call confirming that edit

Reports of work without supporting tool-call evidence should be treated as
fabricated until verified by inspecting the actual files. **Files do not
"reset between turns" or "vanish" in a single Claude.ai chat session** — that
framing has been used as cover for confabulated work in at least one prior
session (v4.0 first attempt, 2026-05-10). If a session reports filesystem
instability, ask them to demonstrate it via `ls -la` and `bash_tool` output;
the artifact will either be there or not, and either way you have ground truth.

When in doubt, upload your local repo state and have the session diff their
claims against your actual files. The cost of a verification turn is small;
the cost of building Stage 3 work on top of fabricated Stage 2 work is total
loss of that work.

---

## Meta-notes on plan evolution

Capture decisions that affected multiple versions here.

- **v3.8 split decision** (date: [fill when committed])
  Originally single-version. Split into v3.8a (infra) and v3.8b (content) because
  authoring 12 content files + building the infrastructure in one session was
  too ambitious and the format decisions needed to be validated before committing
  to 12 files of content using them.

- **CUDA fold decision** (date: [fill when committed])
  Originally v4.2 (standalone CUDA track). Folded into v4.1 alongside C++
  because: (1) pattern-match engine shared, (2) ~60% content overlap at
  Experienced/Master tier, (3) CUDA is syntactically C++, (4) two round-trips
  through the same codebase is wasteful. Escape hatch: if v4.1 scope feels too
  big at execution time, ship as v4.1a (C++) and v4.1b (CUDA).

- **AI-assisted authoring policy** (date: [fill when committed])
  Permitted and encouraged for learning content (structured, fact-checkable,
  not creative). Required human editing before commit. README acknowledges.
  NOT permitted for the question bank itself — question content must be
  deliberately authored because grading fairness depends on precise phrasing.

- **JavaScript track key naming** (2026-04-28)
  Track key is 'javascript' (full word), not 'js' (abbreviation). Matches
  existing full-word convention ('python', 'sql' is the only short key
  and has no longer alternative). Question IDs retain the 'js_' prefix
  for brevity (e.g. js_intro_01) but the TRACK KEY, content directory,
  and QUESTIONS object key all use 'javascript'. Class name is JsEngine
  (mirroring SqlEngine — class names use acronym form, track keys use
  full word). This convention applies to all future tracks: full word for
  the track key, acronym for the class if it reads better.

- **v3.10 consolidation insertion** (2026-04-28)
  v3.10 was not in the original roadmap. Inserted after v3.9 ship
  surfaced three pieces of technical debt that block clean v4.0 (Rust)
  authoring: (1) tag-regex collision with code identifiers (Rust hits
  [ref], [mut], [box], [Vec] immediately); (2) SQL source markdown not
  available, requiring an opaque overlay step in build.py; (3) JS
  Intermediate ML-flavor calibration miss. v3.10 is pure consolidation
  — no new tracks, no new features, no new questions. v4.0 explicitly
  depends on v3.10 having shipped (precondition check in v4.0 prompt).
  This pattern (consolidation version between feature versions when
  technical debt accumulates) may recur — leave room for v4.0.5,
  v4.1.5, etc. if needed.

- **v3.10 ship validation** (2026-05-06)
  v3.10 shipped cleanly: all four planned tasks complete, every claim
  backed by a passing test, byte-identical bundle audit proved the tag
  migration was non-substantive across all three tracks. The
  consolidation-version pattern is validated. Two takeaways for future
  sweeps: (1) author the migration tool BEFORE doing per-file rewrites
  — `build.py --migrate-tags` did the work, then humans never had to
  type the new syntax by hand; (2) per-track bundle md5 audits are the
  cheapest possible proof that "syntax changed but rendered output
  didn't." Both should be standard practice for any future syntax-level
  refactor.

- **v4.0 first attempt — fabrication incident** (2026-05-10)
  v4.0's first session reported building a RustEngine class, an
  alternatives library, 10 pre-staged Rust questions, and a passing QA
  harness against them. The agent's handoff was detailed, structured,
  and convincing — specific line numbers (1928, 2010, 2043), specific
  md5 fingerprints, specific edits with before/after. NONE OF IT EXISTED.
  Verification: re-uploading the actual v3.10 src.zip showed the template
  at 4,401 lines with zero RustEngine/LIBRARY/rs_intro references. Agent
  fabricated ~5,135-line template state and reported it as pre-existing
  scaffold. When pressed about the discrepancy, the agent attributed
  the missing files to "filesystem resets between turns" — a framing
  that does not match how Claude.ai chat sandboxes actually behave.

  Process improvements committed to PROMPTS.md as a result:
  (1) Operational note #9 — verify agent claims against tool-call
      evidence; "filesystem reset" claims are not load-bearing
  (2) v4.0 PRECONDITION CHECK now requires visible tool-call output
      including a grep for existing Rust scaffolding (catches partial
      authoring from prior sessions)
  (3) v4.0 PATTERN-MATCH DESIGN section restructured into explicit
      Stage 1 / Stage 2 / Stage 3 with tool-call evidence required
      at each stage gate
  (4) v4.0 QA HARNESS section now mandates visible bash_tool output
      of harness runs, not summarized "all green" claims

  No engineering progress was lost — v3.10 remained the clean checkpoint.
  But the loss of confidence in the v4.0 chat session forced a restart
  and several days of delay. The lesson generalizes: detailed,
  structured, confident agent reports without supporting tool-call
  evidence should be treated as fabricated until verified. This
  applies to all future versions, not just v4.0.

---

*File maintained manually alongside code. Last plan revision: v4.0 first attempt 2026-05-10 surfaced verification-discipline gaps; PROMPTS.md updated with stricter gates before v4.0 retry.*
