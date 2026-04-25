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
| [v3.8a](#v38a--learning-layer-infrastructure) | Build system + command UI + content file format | Pending |
| [v3.8b](#v38b--sqlpython-learning-content) | Author SQL and Python learning content | Pending |
| [v3.9](#v39--javascript-track) | New track: JS (native execution) | Pending |
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
*Completed: —*
*Notes recorded here once shipped.*

---

## v3.8b — SQL/Python learning content

**Duration estimate:** 1-2 sessions
**Risk level:** low (format proven in v3.8a; just authoring)

```
Ghost Training Terminal v3.8b — author SQL and Python learning content.

CONTEXT
- Build on v3.8a (learning layer infrastructure shipped).
- Content file format is locked and validated. This version is pure authoring.
- End goal reminder: teach the language, don't just quiz syntax.

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

EXPLICIT NON-GOALS
- No new tracks.
- No infrastructure changes.
- No question bank changes (content teaches, doesn't re-quiz).

AI-ASSIST POLICY
- Using AI to draft is fine (efficient for structured content).
- Every draft MUST be human-edited before committing.
- Footnote in README acknowledging AI-assisted authoring, if used.

DELIVERABLES
- 12 populated content files (SQL + Python).
- build.py runs clean — zero warnings on lint pass.
- All cheatsheet / concepts / examples commands working with real content.
- Zip.

VALIDATION
- Walk through Introductory tier of each track in full: enter track, read
  auto-shown concepts, type `examples`, navigate all 3 examples, type
  `cheatsheet`, read full cheatsheet, return to questions, answer one, submit.
  Entire flow should feel coherent.

KNOWN RISKS
- Content drift between what's taught and what's graded. When editing
  content, reference the actual question IDs to ensure alignment.
- Example #3 of each tier MUST preview the next tier — tempting to skip
  because it feels like overreach; don't skip it, it's a pedagogical load-bearer.
```

### v3.8b handoff notes
*Completed: —*

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
- Examples use ML primitives: softmax, argmax, one-hot encoding,
  cosine similarity, tiny feedforward net.
- NO ML knowledge required to solve any question.
- Gotcha content (== vs ===, this binding, hoisting) capped at 1-2 per tier.
  Rest teaches idiomatic modern JS.

DELIVERABLES
- JsEngine class with full execution and sandboxing.
- 'approx' assertion type documented and tested.
- All 50 questions executing successfully against the engine.
- All content files authored and validated by build.py.
- README updated.
- Zip.

CRITICAL — SHOW ME BEFORE BUILDING
- The 'approx' assertion API. Comparing numbers is easy, arrays are harder,
  NaN handling is a gotcha. Lock signature before 50 questions depend on it.
- Web Worker sandboxing implementation. Test with adversarial inputs:
  * attempted document/window access
  * fetch to external URL
  * infinite loop (must have timeout)
  * localStorage access
  None of these should succeed.

KNOWN RISKS
- Web Worker setup is fiddly — first try may not sandbox cleanly.
- JS is TOO permissive — e.g. `"1" + 1 === "11"` is technically fine but
  teaches a bad habit. Resist including this kind of content outside the
  explicit gotcha slots.
```

### v3.9 handoff notes
*Completed: —*

---

## v4.0 — Rust track

**Duration estimate:** 5-8 sessions
**Risk level:** HIGH (new pattern-match paradigm, new territory)

```
Ghost Training Terminal v4.0 — add Rust as the fourth track.

CONTEXT
- Building on v3.9 (JavaScript track shipped).
- Rust is the FIRST pattern-match track — no in-browser execution possible.
- Pattern-match infrastructure built here will be reused by C++ and CUDA
  in v4.1. Design it to be extensible.
- Rust chosen before C++ because its stricter syntax makes pattern-matching
  easier. Proving the approach works on Rust validates it for C++.

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

PATTERN-MATCH DESIGN (CRITICAL)
- Start restrictive, loosen after observing failures.
- Before authoring all 50 questions, show me 2-3 example assertions in the
  new format. Want to critique the format before it's locked in.
- The "alternatives" mechanic is the hardest part to get right — too loose
  accepts wrong answers, too strict rejects correct ones. Err toward strict
  initially; loosening is cheaper than tightening.

QA HARNESS (MANDATORY)
- Write a small test file that for each question feeds 3-5 known-correct
  formulations and 3-5 known-wrong ones, verifies the grader agrees.
- Run this on every question before shipping.
- This harness will be reused in v4.1 for C++ and CUDA.

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
*Completed: —*

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

**2. Before pasting, attach the current `index.html`** so the new session has
the concrete starting point. Alternatively share the GitHub repo URL.

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

---

*File maintained manually alongside code. Last plan revision: v3.7 → v3.8a split + CUDA fold.*
