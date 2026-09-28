# How this was built

Ghost Training Terminal was written with AI coding agents and checked by
programs, not by trusting the draft.

## What the agents did

The teaching notes, the 200 questions, and the page itself were drafted in
stages. `PROMPTS.md` is the work plan those stages used. `docs/` keeps the
stage handoff notes. The product decisions (what a correct answer is, what
the sandbox is allowed to do, what the terminal should feel like) were
reviewed by a person before they shipped.

## How the output was checked

- **The build is reproducible.** `python3 build.py` writes `index.html` and
  `content-bundle.js`. CI runs the build again and fails if the committed
  files differ.
- **Answer keys run in the real engines.** SQL expected queries run in
  sql.js. Python reference answers run in Pyodide, including the hidden
  second inputs and the `None`/`null` case that gates Master. JavaScript
  reference answers live in `tests/js_solutions.json` and run in the worker.
  Rust's 319 accept/reject cases run through the same grader the page uses
  (`tests/qa_harness.py` and a browser parity check).
- **A bad progress file cannot brick the page.** Import is rejected before
  it is saved, and a corrupt `localStorage` value is replaced with a blank
  profile on the next load.

## A verification lesson

An early v4.0 attempt reported a finished Rust engine, ten questions, and a
passing harness. None of that was on disk. The rule that came out of it is
in `CLAUDE.md`: a claim about a file, a test, or a build counts only when
the tool output shows the artifact. The Rust track that shipped later was
built in stages, with the harness kept in lockstep with the page grader.

That is the useful part of building this with agents. The draft is cheap.
The check is the product.
