# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state

- **v4.0.5 shipped.** Review fixes: Python runs in a worker (Ctrl+C abort, `None` grades as null so Master unlocks), progress import is validated, engine status reflects real load state, Rust grader accepts type ascriptions and comments, static assets are vendored, CI grades the answer keys. See `CHANGELOG.md` for the artifact md5.
- **v4.0 Rust track is in the product**, graded by pattern match (no in-browser Rust runtime). `PROMPTS.md` is the historical stage plan, not the current status.
- **v4.1 next.** C++ + CUDA, both reusing v4.0's pattern-match infrastructure.

## Commands

```bash
python3 build.py                # build: writes index.html, prints md5 + size + per-track word counts
python3 build.py --check        # lint only; no write. Exit 1 on warnings.
python3 build.py --migrate-tags # one-shot legacy [tag] → <<tag>> rewrite over src/content/. Idempotent.
python3 -m http.server          # serve the built site locally; no bundler / node_modules
python3 tests/qa_harness.py     # Rust pattern-match grader, 319 embedded cases
python3 tests/rust_variants.py  # type ascriptions and comments
python3 tests/secret_scan.py
```

GitHub Actions (`.github/workflows/ci.yml`) rebuilds `index.html` and `content-bundle.js` and diffs them, then runs the Rust harness and a headless-Chrome pass over the SQL, Python, and JavaScript answer keys. The built `index.html` and `content-bundle.js` are committed and are what ships.

## Architecture

### Build pipeline

`build.py` is a markdown → ANSI/HTML bundler. It reads `src/content/{sql,python,javascript,rust}/{cheatsheet,tier-*}.md`, renders each file to ANSI (for terminal display) and optionally HTML (cheatsheets only), and writes the JSON dict to `content-bundle.js` (`window.CONTENT_BUNDLE = …`). The `{{CONTENT_BUNDLE_JSON}}` token in `src/index.template.html` is replaced with the word `external` so the shell does not inline the teaching material.

The pipeline is symmetric across all four tracks. v3.10 reconstructed the SQL markdown that v3.9 had lost.

### The two halves of the content model

- **Content bundle** (`src/content/`) — teaching material: cheatsheets, per-tier concepts, per-tier examples. Goes through `build.py`'s markdown renderer.
- **Question bank** (`QUESTIONS` const in `src/index.template.html`) — graded items with `id`, `prompt`, `assertion`, optional `setup`/`hint`/`fallback_expected`. Lives in template body, NOT in content bundle. `build.py` parses `id:'...'` strings out of the template to validate `<<qid:foo>>` references in content.

If a task says "reframe Q26" or "add a question," the change is in `src/index.template.html`, not under `src/content/`. If it says "edit cheatsheet" or "add an example," the change is under `src/content/`.

### Tag syntax (v3.10+)

Inline color tags use `<<tag>>...<</tag>>` with **named closers**. Valid tags: `bold amber teal green blue purple red dim`. Question references: `<<qid:py_intro_03>>` becomes a clickable link.

Legacy `[tag]...[/]` syntax is rejected by the build (`TAG_LEGACY_MODE = "error"` in `build.py`). The migration tool stays around for forks. The rationale: legacy `[a-z]{3,}` open-tag regex collided with code identifiers (`[prop]`, `[mut]`, `[Vec]`), and v4.0 Rust authoring would hit this immediately.

Named-closer mismatch (`<<amber>>foo<</dim>>`) is a structural error. Tags can span lines and paragraph breaks; the renderer closes/re-opens ANSI codes at each line boundary so terminals that reset SGR on `\n` render consistently.

### Markdown format

- `# HEADER` lines become bold-amber section headers.
- Consecutive 2-space-indented prose lines merge into one paragraph. A blank line starts the next paragraph.
- 4-space-indented lines = code (consecutive lines collapsed into one `<pre>`).
- For tier files: `---` divider splits concepts (above) from examples (below). Each example starts with `# EXAMPLE N`.

Soft warning at 15 lines per code block. Long blocks should be split.

### Execution engines

Four engines, booted from `index.html`:

- **`SqlEngine`** — vendored sql.js 1.14.2 (WASM SQLite). Schema + seed data hard-coded in `SCHEMA_SQL`/`SEED_SQL` constants. DB is rebuilt between user query and expected query so DML can't leak across evaluations. Prewarmed after first paint.
- **`PythonEngine`** — Pyodide 0.29.5 from jsDelivr, loaded only when the Python track starts, inside `pyodide-worker.js`. A 5s eval wall terminates the worker. Ctrl+C aborts and respawns. `None` is mapped to `null` before comparison. Falls back to `normPythonSource()` pattern matching if Pyodide fails to load; pattern-match successes are marked `degraded:true` and skip hidden checks.
- **`JsEngine`** — spins up a fresh Web Worker from a Blob URL per grading round. Worker boot source is `JsEngine.BOOT_SOURCE` (a multi-line string literal inside the template). 3000ms execution cap inside the worker + 8000ms outer walltime cap. Each message is gated on a per-worker `GHOST_MARKER` UUID. Ctrl+C terminates the in-flight worker.
- **`RustEngine`** — pattern match against a canonical form. No Rust compiler. Optional `: Type` ascriptions and comments are accepted; the 319 QA cases still pass.

### JS sandbox (`SANDBOX_DELETIONS` in boot source, mirrored as `JS_SANDBOX_DELETIONS` in `build.py`)

At worker boot, the following are removed on `globalThis` and on each prototype up the chain, before any user code runs: `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `importScripts`, `BroadcastChannel`, `indexedDB`, `Cache`, `caches`, `Notification`. `crypto` and `performance` are replaced with frozen allowlist proxies. Nested `Worker` construction is denied. A meta Content-Security-Policy limits `connect-src` to this origin and jsDelivr. **Keep the deletion list in sync** between the boot source and `build.py`'s `JS_SANDBOX_DELETIONS` — `build.py` lints fenced JS code blocks in content for references to deleted APIs so examples don't tell users to write code that throws. The page CSP includes `'unsafe-eval'` because the JavaScript grader runs learner code with `eval`.

### Assertion types (in `QUESTIONS`)

- `binding` — variable name + expected value (deep-equal)
- `stdout` — expected captured stdout, trimmed
- `call` / `expression` — string evaluated in the user's namespace, compared to `expected`
- `approx` (JS only, v3.9+) — floating-point comparison; required `tol` (no default); optional `forbidden:[...]` for "implement X without Y" questions

### Persistence

Progress in `localStorage` under a versioned key. `STATE_VERSION = 4`. `GATE_SIZE = 10` (questions per tier). `TIER_ORDER = ['introductory','amateur','intermediate','experienced','master']`. `load()` and `importJson()` reject a shape that is missing `completed` (object keyed by track) or `activity` (array) and fall back to defaults instead of saving it. Migration keeps python, sql, javascript, and rust. Session attempt counts live in `state.stats` and survive reload; the session clock does not.

## Conventions

### Authoring

- Voice is direct, no padding. Explain "why" after "what."
- Each tier's last example previews the next tier.
- Examples never duplicate the graded questions — submitting an exact-match example answer should NOT pass.
- Cheatsheets are whole-language references, not per-tier.
- ML-adjacent framing welcome (e.g., "training loop intuition") but no question may *require* ML knowledge.

### Versioning

Loose SemVer, with patch-style letters (`v3.8a`, `v3.8b`) only when a milestone splits across releases that must ship together. **A version bump touches five places**:

1. Footer line in `src/index.template.html`
2. Mobile boot banner (`TerminalApp.boot()` in template)
3. Desktop boot banner (same area)
4. README badge
5. New `CHANGELOG.md` entry

### CHANGELOG and PROMPTS

- `CHANGELOG.md` is the source of truth for "what exists in this codebase." One entry per version, with build-artifact md5 + per-track bundle md5 audit. Read it before assuming what a feature does — it captures rationales that aren't in the code.
- `PROMPTS.md` is the multi-version work plan with per-version kickoff prompts and handoff notes. Treat it as project context, not as instructions for the current session.

### Things to avoid

- Don't author or accept legacy `[tag]` syntax — `build.py` will block the build.
- Don't add the SQL `cheatsheet.html` to the repo; HTML is regenerated from the markdown source by every build.
- Don't introduce build dependencies (no node_modules, no bundler, no transpiler). The site is built by one Python script. CI may install Playwright; that is not a build dependency.
- Pyodide stays on jsDelivr (`PYODIDE_VERSION`, `PYODIDE_JS_SRI`). sql.js is vendored. If you bump Pyodide, recompute the sha384 SRI and re-run `tests/answer_keys.mjs`.
- When changing `SANDBOX_DELETIONS`, change both the boot source in the template AND `JS_SANDBOX_DELETIONS` in `build.py`.

### Verification discipline

When making claims about work done — file edits, test runs, builds — the corresponding tool calls must produce real artifacts visible to the user. Don't summarize "all green" without showing the underlying output. Don't claim scaffolding exists without viewing it first. Files do not vanish between turns in a single session.

This convention exists because v4.0's first attempt fabricated a full `RustEngine` + 10 questions + passing harness, none of which existed on disk. The lesson: detailed, confident reports without supporting tool-call evidence should be treated as fabricated until verified.

### v4.0 is shipped

The Rust track, the pattern-match grader, and the QA harness are in the tree. `PROMPTS.md` records how that work was staged. New track work (v4.1 C++ / CUDA) should reuse that grader rather than re-opening the design stages.
