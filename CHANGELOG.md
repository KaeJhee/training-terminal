# Changelog

All notable changes to Ghost Training Terminal are documented here.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

Upcoming versions are planned in [PROMPTS.md](./PROMPTS.md):

- **v3.8a** — Learning layer infrastructure (build.py, content file format, new commands)
- **v3.8b** — SQL and Python learning content
- **v3.9** — JavaScript track (native execution + learning content)
- **v4.0** — Rust track (pattern-match + learning content)
- **v4.1** — C++ track + CUDA specialization (pattern-match + learning content)

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
