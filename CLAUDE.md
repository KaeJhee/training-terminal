# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
python3 build.py                # build: writes index.html, prints md5 + size + per-track word counts
python3 build.py --check        # lint only; no write. Exit 1 on warnings.
python3 build.py --migrate-tags # one-shot legacy [tag] → <<tag>> rewrite over src/content/. Idempotent.
python3 -m http.server          # serve index.html locally; no bundler / node_modules
```

There is no test suite, no linter beyond `build.py --check`, no CI config. The build artifact `index.html` is committed to the repo and is what ships.

## Architecture

### Build pipeline

`build.py` is a markdown → ANSI/HTML bundler. It reads `src/content/{sql,python,javascript}/{cheatsheet,tier-*}.md`, renders each file to ANSI (for terminal display) and optionally HTML (cheatsheets only), packs everything into a JSON dict, and substitutes that dict for the `{{CONTENT_BUNDLE_JSON}}` placeholder in `src/index.template.html` to produce the single-file `index.html`.

The pipeline is symmetric across all three tracks as of v3.10. Earlier (v3.9) it had a "build then overlay SQL bytes from v3.8b" workaround because the SQL source markdown had been lost; v3.10 reconstructed it.

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
- 2-space-indented lines = prose paragraphs (one `<p>` each, not merged).
- 4-space-indented lines = code (consecutive lines collapsed into one `<pre>`).
- For tier files: `---` divider splits concepts (above) from examples (below). Each example starts with `# EXAMPLE N`.

Soft warning at 15 lines per code block. Long blocks should be split.

### Execution engines

Three engines, all booted from `index.html`:

- **`SqlEngine`** — sql.js (WASM SQLite). Schema + seed data hard-coded in `SCHEMA_SQL`/`SEED_SQL` constants. DB is rebuilt between user query and expected query so DML can't leak across evaluations.
- **`PythonEngine`** — Pyodide v0.26.4 from jsdelivr CDN. 60s init timeout (90s on iOS). Falls back to `normPythonSource()` pattern matching if Pyodide fails to load; pattern-match successes are marked `degraded:true`.
- **`JsEngine`** — spins up a fresh Web Worker from a Blob URL per grading round. Worker boot source is `JsEngine.BOOT_SOURCE` (a multi-line string literal inside the template). 3000ms execution cap inside the worker + 8000ms outer walltime cap. Each message is gated on a per-worker `GHOST_MARKER` UUID.

### JS sandbox (`SANDBOX_DELETIONS` in boot source, mirrored as `JS_SANDBOX_DELETIONS` in `build.py`)

At worker boot, the following are removed before any user code runs: `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `importScripts`, `BroadcastChannel`, `indexedDB`, `Cache`, `caches`, `Notification`. `crypto` and `performance` are replaced with frozen allowlist proxies. Nested `Worker` construction is denied. **Keep these in sync** between the boot source and `build.py`'s `JS_SANDBOX_DELETIONS` — `build.py` lints fenced JS code blocks in content for references to deleted APIs so examples don't tell users to write code that throws.

### Assertion types (in `QUESTIONS`)

- `binding` — variable name + expected value (deep-equal)
- `stdout` — expected captured stdout, trimmed
- `call` / `expression` — string evaluated in the user's namespace, compared to `expected`
- `approx` (JS only, v3.9+) — floating-point comparison; required `tol` (no default); optional `forbidden:[...]` for "implement X without Y" questions

### Persistence

Progress in `localStorage` under a versioned key. `STATE_VERSION = 3`. `GATE_SIZE = 10` (questions per tier). `TIER_ORDER = ['introductory','amateur','intermediate','experienced','master']`.

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
- Don't introduce build dependencies (no node_modules, no bundler, no transpiler). The whole point is one Python script and one `index.html`.
- Pyodide/sql.js CDN URLs are hard-coded; if you bump versions, bump `PYODIDE_VERSION` and the sql.js URL together and re-test the iOS path (90s init).
- When changing `SANDBOX_DELETIONS`, change both the boot source in the template AND `JS_SANDBOX_DELETIONS` in `build.py`.
