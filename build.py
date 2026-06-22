#!/usr/bin/env python3
"""
build.py — Ghost Training Terminal content bundler.

Reads markdown content files from src/content/<track>/ and concatenates them
into index.html via src/index.template.html.

Usage:
    python build.py            # build (write index.html, print summary)
    python build.py --check    # lint only (no write); exit 1 on warnings

Content file format (whole-language reference in src/content/cheatsheet-format.md):

    # Header line                       <- bold amber section header

      Two-space-indent line of prose.   <- regular paragraph
      Inline color tags: [amber]SELECT[/], [dim]aside[/], [bold]emphasis[/].
      Question references: [qid:sql_intro_03] become clickable links in panel.

          Four-space-indent line of code.   <- code block (auto-grouped)
          [amber]SELECT[/] name [amber]FROM[/] customers;

      Tags can [dim]span across
      multiple lines (v3.8b)
      with paragraph breaks in between.[/]

For tier-<rank>.md files: a horizontal rule (---) divides the concepts section
from the examples section. Examples are subdivided by top-level `# EXAMPLE N`
headings into a list of separately-renderable strings.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Iterable

# --------------------------------------------------------------------------------------
# Tag tables. Keep these in sync with index.template.html CSS (.cs-amber, .cs-teal, ...).
# --------------------------------------------------------------------------------------

ANSI_OPEN = {
    "bold":   "\x1b[1m",
    "amber":  "\x1b[33m",
    "teal":   "\x1b[36m",
    "green":  "\x1b[32m",
    "blue":   "\x1b[34m",
    "purple": "\x1b[35m",
    "red":    "\x1b[31m",
    "dim":    "\x1b[90m",
}
ANSI_CLOSE = {
    "bold":   "\x1b[22m",
    "amber":  "\x1b[39m",
    "teal":   "\x1b[39m",
    "green":  "\x1b[39m",
    "blue":   "\x1b[39m",
    "purple": "\x1b[39m",
    "red":    "\x1b[39m",
    "dim":    "\x1b[39m",
}
HTML_CLASS = {
    "bold":   "cs-bold",
    "amber":  "cs-amber",
    "teal":   "cs-teal",
    "green":  "cs-green",
    "blue":   "cs-blue",
    "purple": "cs-purple",
    "red":    "cs-red",
    "dim":    "cs-dim",
}

VALID_TAGS = set(ANSI_OPEN.keys())
TIER_NUMS = {"introductory": 1, "amateur": 2, "intermediate": 3, "experienced": 4, "master": 5}

# v3.9 — JS sandbox deletions. Used for the globalThis-deletion lint that
# scans fenced code blocks in JS content for references to APIs the JsEngine
# Worker has stripped (so a question example doesn't accidentally tell the
# user to write `globalThis.fetch(...)`, which throws). Mirrors the
# SANDBOX_DELETIONS constant defined in JsEngine in index.template.html.
JS_SANDBOX_DELETIONS = frozenset({
    "fetch", "XMLHttpRequest", "WebSocket", "EventSource", "importScripts",
    "BroadcastChannel", "indexedDB", "Cache", "caches", "Notification",
})

# Sentinels used in the index.template.html
PLACEHOLDER = "{{CONTENT_BUNDLE_JSON}}"

# Hard limit on code-block lines — soft-warned by --check.
CODE_BLOCK_SOFT_LIMIT = 15

# v4.0 Stage 2 — closed tag set for Rust questions. New tags require adding
# here first; the lint below rejects any tag outside this set.
RUST_QUESTION_TAGS = frozenset({
    "mutability",     # let mut, &mut, mutable references
    "borrowing",      # & references, borrow checker concepts
    "lifetimes",      # 'a annotations, lifetime elision
    "traits",         # trait definitions, impl blocks, trait bounds
    "closures",       # |x| ... syntax, FnOnce/Fn/FnMut
    "iterators",      # iter(), map, filter, collect chains
    "error-handling", # Result, Option, ?, unwrap, panic
    "generics",       # <T>, where clauses
    "macros",         # println!, vec!, custom macro_rules!
    "unsafe",         # unsafe blocks, raw pointers
    "async",          # async fn, .await, futures (Master tier)
})

# Marker sentinels around the Stage 2 Rust questions block in the template.
RUST_QS_BEGIN = "STAGE2_RUST_QUESTIONS_BEGIN"
RUST_QS_END = "STAGE2_RUST_QUESTIONS_END"

# --------------------------------------------------------------------------------------
# Tag syntax (v3.10).
#
# v3.10 migrates the inline-tag syntax from the v3.<=3.9 form `[amber]...[/]` to
# `<<amber>>...<</amber>>`. Reasoning: the legacy `[a-z]{3,}` open-tag regex
# collides with code identifiers across the languages this terminal targets —
# JS already had to dodge `[prop]`, `[key]`, `[idx]`; Rust would hit it
# immediately with `[ref]`, `[mut]`, `[box]`, `[Vec]`, `[Option]`, `[Result]`.
# The `<<...>>` form has no such overlap with any of the planned tracks and
# uses an explicit named closer for unambiguous matching.
#
# During the v3.10 sprint the parser accepts BOTH syntaxes (MIXED mode), and
# a per-file lint warns whenever legacy `[tag]` syntax appears so authors can
# migrate file-by-file. The `--migrate-tags` tool walks every content file
# and rewrites it from legacy syntax to new syntax in place, using the
# parser's tag stack so that legacy `[/]` close tokens get rewritten to the
# correct named `<</tag>>` closer. After all content files are migrated, set
# TAG_LEGACY_MODE = "error" below (or pass --strict-tags) to make the lint
# fatal — at which point legacy syntax can no longer ship.
# --------------------------------------------------------------------------------------

# v3.10 — accepted modes for legacy `[tag]` syntax during the migration window.
#   "warn"  — lint warns on legacy use, build still succeeds (during migration)
#   "error" — lint fails on any legacy use (post-cutover, default for v3.10+)
#   "off"   — pretend legacy syntax doesn't exist (don't use; here for testing)
#
# Bumped to "error" as of v3.10 ship: every content file across all three
# tracks has been migrated to <<tag>> syntax, verified by per-track bundle
# md5 matching v3.9. Anyone editing content files now gets an immediate
# build failure if they slip back into [tag] syntax.
TAG_LEGACY_MODE = "error"

# Token regexes for inline parsing — both syntaxes.
# Legacy open-tag requires 3+ lowercase chars (carries forward the v3.8a rule
# that prevented `obj[i]` from being misread as a tag); kept for back-compat
# during the migration window.
RE_OPEN_TAG_LEGACY = re.compile(r"\[([a-z]{3,})\]")
RE_CLOSE_TAG_LEGACY = re.compile(r"\[/\]")
RE_QID_LEGACY = re.compile(r"\[qid:([a-z0-9_]+)\]")

# v3.10 syntax. Open: `<<TAG>>`. Close: `<</TAG>>` with the matching name —
# unambiguous closer that doesn't depend on stack inspection. The 1+ chars
# rule for the tag name is fine because the leading `<<` is itself distinctive
# (no JS/Rust/Python identifier syntax produces a `<<` digram).
RE_OPEN_TAG_V310 = re.compile(r"<<([a-z]+)>>")
RE_CLOSE_TAG_V310 = re.compile(r"<</([a-z]+)>>")
RE_QID_V310 = re.compile(r"<<qid:([a-z0-9_]+)>>")


# --------------------------------------------------------------------------------------
# Inline parser. Walks a stream of source characters maintaining a tag stack so that
# tags can span across line boundaries (v3.8b infra fix #1).
#
# Rendering model:
#   - ANSI: at every line break we emit the close codes for any currently-open tags
#     and re-emit the open codes at the start of the next line. This keeps terminals
#     that reset SGR on newline (some xterm modes) rendering consistently.
#   - HTML: spans stay open across line breaks. We close them only when [/] is seen
#     or when a structural boundary (header, code-block, EOF) forces a flush.
# --------------------------------------------------------------------------------------


class TagStack:
    """Stack of currently-open inline tags. Mutated by the inline parser."""

    def __init__(self) -> None:
        self._stack: list[str] = []

    def push(self, tag: str) -> None:
        self._stack.append(tag)

    def pop(self) -> str | None:
        if not self._stack:
            return None
        return self._stack.pop()

    @property
    def depth(self) -> int:
        return len(self._stack)

    def open_codes_ansi(self) -> str:
        return "".join(ANSI_OPEN[t] for t in self._stack)

    def close_codes_ansi(self) -> str:
        # Close in reverse order, mirroring xterm push/pop.
        return "".join(ANSI_CLOSE[t] for t in reversed(self._stack))

    def open_spans_html(self) -> str:
        return "".join(f'<span class="{HTML_CLASS[t]}">' for t in self._stack)

    def close_spans_html(self) -> str:
        return "</span>" * len(self._stack)


class LineRender:
    """Result of rendering one source line."""

    def __init__(self, ansi: str, html: str) -> None:
        self.ansi = ansi
        self.html = html


def _esc_html(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def render_inline(line: str, stack: TagStack, *, errors: list[str], file_label: str,
                  line_num: int) -> LineRender:
    """Render a single source line's inline tags. Mutates stack across calls so
    multi-line tags work. Returns ANSI and HTML for this line.

    Recognises BOTH the v3.10 `<<tag>>...<</tag>>` syntax and the legacy
    `[tag]...[/]` syntax during the migration window. Legacy usage is
    surfaced through warn_legacy_tag_usage() which scans the raw markdown
    for legacy tokens and emits warnings/errors per TAG_LEGACY_MODE — the
    parser here just renders both forms identically and records nothing.

    Note: ANSI here is the line's *interior* — caller wraps with line-edge close+reopen.
    """
    ansi_parts: list[str] = []
    html_parts: list[str] = []
    i = 0
    n = len(line)

    def _next_token_pos(start: int) -> int:
        """Return index of the next character that could start a token: either
        '[' or '<'. Returns n if no more tokens."""
        nb = line.find("[", start)
        nl = line.find("<", start)
        if nb == -1: nb = n
        if nl == -1: nl = n
        return min(nb, nl)

    while i < n:
        if line[i] not in ("[", "<"):
            # Plain text run until next potential token start.
            j = _next_token_pos(i + 1)
            chunk = line[i:j]
            ansi_parts.append(chunk)
            html_parts.append(_esc_html(chunk))
            i = j
            continue

        # Try v3.10 syntax first: `<</tag>>`, `<<qid:...>>`, `<<tag>>`.
        if line[i] == "<":
            m_close_v = RE_CLOSE_TAG_V310.match(line, i)
            if m_close_v:
                tag = m_close_v.group(1)
                popped = stack.pop()
                if popped is None:
                    errors.append(
                        f"{file_label}:{line_num}: stray <</{tag}>> with no matching <<{tag}>>"
                    )
                elif popped != tag:
                    errors.append(
                        f"{file_label}:{line_num}: <</{tag}>> closes {popped!r} on stack — "
                        f"named-closer mismatch (did you mean <</{popped}>>?)"
                    )
                    ansi_parts.append(ANSI_CLOSE[popped])
                    html_parts.append("</span>")
                else:
                    ansi_parts.append(ANSI_CLOSE[popped])
                    html_parts.append("</span>")
                i = m_close_v.end()
                continue

            m_qid_v = RE_QID_V310.match(line, i)
            if m_qid_v:
                qid = m_qid_v.group(1)
                ansi_parts.append("\x1b[34m\x1b[4m" + qid + "\x1b[24m\x1b[39m")
                html_parts.append(
                    f'<a class="cs-qid" data-qid="{_esc_html(qid)}">{_esc_html(qid)}</a>'
                )
                i = m_qid_v.end()
                continue

            m_open_v = RE_OPEN_TAG_V310.match(line, i)
            if m_open_v:
                tag = m_open_v.group(1)
                if tag not in VALID_TAGS:
                    errors.append(
                        f"{file_label}:{line_num}: unknown tag <<{tag}>> "
                        f"(valid: {', '.join(sorted(VALID_TAGS))})"
                    )
                    ansi_parts.append(m_open_v.group(0))
                    html_parts.append(_esc_html(m_open_v.group(0)))
                    i = m_open_v.end()
                    continue
                stack.push(tag)
                ansi_parts.append(ANSI_OPEN[tag])
                html_parts.append(f'<span class="{HTML_CLASS[tag]}">')
                i = m_open_v.end()
                continue

            # A '<' that isn't part of any v3.10 token — pass through.
            ansi_parts.append("<")
            html_parts.append(_esc_html("<"))
            i += 1
            continue

        # line[i] == "[" — try legacy syntax: [/], [qid:...], [tag].
        m_close = RE_CLOSE_TAG_LEGACY.match(line, i)
        if m_close:
            popped = stack.pop()
            if popped is None:
                errors.append(
                    f"{file_label}:{line_num}: stray [/] with no matching [tag]"
                )
            else:
                ansi_parts.append(ANSI_CLOSE[popped])
                html_parts.append("</span>")
            i = m_close.end()
            continue

        m_qid = RE_QID_LEGACY.match(line, i)
        if m_qid:
            qid = m_qid.group(1)
            ansi_parts.append("\x1b[34m\x1b[4m" + qid + "\x1b[24m\x1b[39m")
            html_parts.append(
                f'<a class="cs-qid" data-qid="{_esc_html(qid)}">{_esc_html(qid)}</a>'
            )
            i = m_qid.end()
            continue

        m_open = RE_OPEN_TAG_LEGACY.match(line, i)
        if m_open:
            tag = m_open.group(1)
            if tag not in VALID_TAGS:
                errors.append(
                    f"{file_label}:{line_num}: unknown tag [{tag}] "
                    f"(valid: {', '.join(sorted(VALID_TAGS))})"
                )
                ansi_parts.append(m_open.group(0))
                html_parts.append(_esc_html(m_open.group(0)))
                i = m_open.end()
                continue
            stack.push(tag)
            ansi_parts.append(ANSI_OPEN[tag])
            html_parts.append(f'<span class="{HTML_CLASS[tag]}">')
            i = m_open.end()
            continue

        # A '[' that isn't part of any pattern — pass through.
        ansi_parts.append("[")
        html_parts.append("[")
        i += 1

    return LineRender(ansi="".join(ansi_parts), html="".join(html_parts))


# --------------------------------------------------------------------------------------
# Block-level parser. Walks the source line-by-line, classifying each line into
# header / prose / code / blank, and emits structured ANSI + HTML.
# --------------------------------------------------------------------------------------


HEADER_PREFIX = "# "
DIVIDER_RE = re.compile(r"^---+\s*$")


def _classify(line: str) -> tuple[str, str]:
    """Return (kind, payload). kind is 'header'|'prose'|'code'|'blank'.
    payload is the line stripped of structural indent (header-text, prose-text,
    or full-text-with-leading-spaces-preserved for code).
    """
    if line.strip() == "":
        return ("blank", "")
    if line.startswith(HEADER_PREFIX):
        return ("header", line[len(HEADER_PREFIX):].rstrip())
    # Count leading spaces.
    stripped_left = line.lstrip(" ")
    indent = len(line) - len(stripped_left)
    if indent >= 4:
        # Code: keep indent beyond the first 4 spaces (normalize 4-space prefix to 0).
        return ("code", line[4:].rstrip())
    # Anything else is prose — strip up to 2 leading spaces, otherwise pass through.
    if indent >= 2:
        return ("prose", line[2:].rstrip())
    return ("prose", line.rstrip())


def render_markdown(md_text: str, *, want_html: bool, file_label: str,
                    errors: list[str]) -> tuple[str, str]:
    """Render full markdown source. Returns (ansi, html) — html is empty if not wanted.

    Block grammar:
        section := header? (prose-line | code-block | blank)*
        code-block := one or more consecutive 4-space-indented lines.

    The parser does not merge contiguous prose lines into one paragraph. Each
    non-blank prose line maps to its own <p class="cs-prose"> in HTML and its own
    '  ...\\r\\n' line in ANSI. Code lines collapse into one
    <pre class="cs-code"><code>...</code></pre> block per consecutive run.

    Inline tags can span multiple source lines (v3.8b infra fix #1). On every
    \\r\\n boundary the ANSI emits the close-codes for any still-open tags and
    re-emits the open-codes at the start of the next line, so terminal SGR
    state is always sane after a newline. HTML spans simply stay open across
    lines until [/] is reached.
    """
    raw = md_text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    lines = raw.split("\n")

    ansi_chunks: list[str] = []
    html_chunks: list[str] = []
    stack = TagStack()

    section_open = False

    def open_section() -> None:
        nonlocal section_open
        if want_html and not section_open:
            html_chunks.append('<div class="cs-section">')
            section_open = True

    def close_section() -> None:
        nonlocal section_open
        if want_html and section_open:
            html_chunks.append('</div>')
            section_open = False

    code_html_lines: list[str] = []

    def flush_code() -> None:
        nonlocal code_html_lines
        if not code_html_lines:
            return
        if want_html:
            html_chunks.append('<pre class="cs-code"><code>'
                               + "\n".join(code_html_lines)
                               + '</code></pre>')
        code_html_lines = []

    def emit_ansi_line(indent: str, body_ansi: str) -> None:
        """Emit one ANSI line: re-open any across-line tags at start, close them at end.
        body_ansi already contains the tag deltas this line introduces."""
        ansi_chunks.append(stack.open_codes_ansi() if False else "")
        # NOTE: stack here reflects state AFTER this line is processed. We want
        # the state at line START. Caller must capture that before invoking us.
        ansi_chunks.append(indent + body_ansi + "\r\n")

    for idx, raw_line in enumerate(lines, start=1):
        kind, payload = _classify(raw_line)

        if kind == "header":
            flush_code()
            close_section()
            if stack.depth:
                errors.append(
                    f"{file_label}:{idx}: header line `{payload}` while "
                    f"{stack.depth} inline tag(s) still open — did you forget [/]?"
                )
                while stack.depth:
                    stack.pop()
            ansi_chunks.append(
                ANSI_OPEN["bold"] + ANSI_OPEN["amber"] + payload
                + ANSI_CLOSE["amber"] + ANSI_CLOSE["bold"] + "\r\n"
            )
            if want_html:
                open_section()
                html_chunks.append(f'<h4 class="cs-h">{_esc_html(payload)}</h4>')
            continue

        if kind == "blank":
            flush_code()
            ansi_chunks.append("\r\n")
            continue

        if kind == "code":
            if want_html and not section_open:
                open_section()
            # Capture stack state at line start so we can re-open on this line.
            line_start_open = stack.open_codes_ansi()
            line_render = render_inline(
                payload, stack, errors=errors,
                file_label=file_label, line_num=idx,
            )
            line_end_close = stack.close_codes_ansi()
            ansi_chunks.append(
                "    " + line_start_open + line_render.ansi + line_end_close + "\r\n"
            )
            if want_html:
                code_html_lines.append(line_render.html)
            continue

        # kind == "prose"
        flush_code()
        if want_html and not section_open:
            open_section()
        line_start_open = stack.open_codes_ansi()
        line_render = render_inline(
            payload, stack, errors=errors,
            file_label=file_label, line_num=idx,
        )
        line_end_close = stack.close_codes_ansi()
        ansi_chunks.append(
            "  " + line_start_open + line_render.ansi + line_end_close + "\r\n"
        )
        if want_html:
            html_chunks.append('<p class="cs-prose">' + line_render.html + '</p>')

    flush_code()
    close_section()

    if stack.depth:
        errors.append(
            f"{file_label}: EOF reached with {stack.depth} unclosed inline tag(s). "
            f"Add [/] to balance."
        )
        # Don't try to recover — leave the ANSI as emitted; caller's downstream
        # validation will surface this.

    return "".join(ansi_chunks), "".join(html_chunks)



# --------------------------------------------------------------------------------------
# Tier file split: concepts vs examples.
# --------------------------------------------------------------------------------------


def split_tier_file(md_text: str, *, file_label: str, errors: list[str]
                    ) -> tuple[str, list[str]]:
    """Split tier-X.md into (concepts_md, [example1_md, example2_md, ...]).

    Divider: a line matching ^---+\\s*$.
    Examples are subdivided by `# EXAMPLE` headings within the post-divider section.
    """
    raw = md_text.replace("\r\n", "\n").rstrip("\n")
    lines = raw.split("\n")
    # Find the first divider.
    div_idx = None
    for idx, line in enumerate(lines):
        if DIVIDER_RE.match(line):
            div_idx = idx
            break
    if div_idx is None:
        # No divider → treat the whole file as concepts, no examples. Author may want
        # to add examples later; not an error.
        return ("\n".join(lines).rstrip() + "\n", [])

    concepts_md = "\n".join(lines[:div_idx]).rstrip() + "\n"
    rest = lines[div_idx + 1:]

    # Now split `rest` on `# EXAMPLE` headings (case-insensitive title prefix).
    examples: list[list[str]] = []
    current: list[str] | None = None
    for line in rest:
        if line.startswith("# ") and line[2:].strip().upper().startswith("EXAMPLE"):
            if current is not None:
                examples.append(current)
            current = [line]
        else:
            if current is None:
                # Stray content before the first EXAMPLE heading — skip with warning.
                if line.strip():
                    errors.append(
                        f"{file_label}: stray text after divider before first "
                        f"`# EXAMPLE` heading: `{line[:60]}…`"
                    )
                continue
            current.append(line)
    if current is not None:
        examples.append(current)

    if not examples:
        errors.append(
            f"{file_label}: divider present but no `# EXAMPLE N` headings found "
            f"in the examples section."
        )

    examples_md = ["\n".join(ex).rstrip() + "\n" for ex in examples]
    return concepts_md, examples_md


# --------------------------------------------------------------------------------------
# Bundle assembly.
# --------------------------------------------------------------------------------------


def warn_long_code_blocks(md_text: str, *, file_label: str,
                          errors: list[str]) -> None:
    """Soft-warn on consecutive code blocks longer than CODE_BLOCK_SOFT_LIMIT lines."""
    lines = md_text.replace("\r\n", "\n").split("\n")
    run = 0
    run_start = 0
    for idx, line in enumerate(lines, start=1):
        if line.startswith("    "):
            if run == 0:
                run_start = idx
            run += 1
        else:
            if run > CODE_BLOCK_SOFT_LIMIT:
                errors.append(
                    f"{file_label}:{run_start}: code block has {run} lines "
                    f"(soft limit: {CODE_BLOCK_SOFT_LIMIT}). Consider splitting."
                )
            run = 0
    if run > CODE_BLOCK_SOFT_LIMIT:
        errors.append(
            f"{file_label}:{run_start}: code block has {run} lines "
            f"(soft limit: {CODE_BLOCK_SOFT_LIMIT}). Consider splitting."
        )


def warn_unknown_qids(md_text: str, *, file_label: str, valid_qids: set[str],
                      errors: list[str]) -> None:
    """Warn if a qid reference (legacy `[qid:foo]` or v3.10 `<<qid:foo>>`)
    points to an id not in the question bank."""
    for regex, fmt in ((RE_QID_LEGACY, "[qid:{}]"), (RE_QID_V310, "<<qid:{}>>")):
        for m in regex.finditer(md_text):
            qid = m.group(1)
            if qid not in valid_qids:
                line_num = md_text.count("\n", 0, m.start()) + 1
                errors.append(
                    f"{file_label}:{line_num}: {fmt.format(qid)} references an unknown question. "
                    f"Check QUESTIONS in index.template.html."
                )


def warn_legacy_tag_usage(md_text: str, *, file_label: str,
                          errors: list[str]) -> None:
    """v3.10 — Per TAG_LEGACY_MODE, warn or error when legacy `[tag]...[/]`
    syntax appears in a content file. The migration tool (`--migrate-tags`)
    rewrites legacy syntax to the new `<<tag>>...<</tag>>` form. After all
    files are migrated, set TAG_LEGACY_MODE = 'error' to prevent regressions.

    Detection is conservative: we look for `[tag]` with a known color/bold
    tag name only — anything else (e.g. `[a-z]{1,2}` or non-color names) is
    treated as literal text and ignored, matching how the parser handles
    them. `[/]` is detected directly. `[qid:...]` is detected directly.
    """
    if TAG_LEGACY_MODE == "off":
        return

    findings: list[str] = []

    # Known-tag opens.
    for m in RE_OPEN_TAG_LEGACY.finditer(md_text):
        tag = m.group(1)
        if tag in VALID_TAGS:
            line_num = md_text.count("\n", 0, m.start()) + 1
            findings.append(f"{file_label}:{line_num}: legacy `[{tag}]` syntax")
            break  # one finding per file is enough — keep the report short
    else:
        # Closes only count as legacy if the file *also* has legacy opens; a
        # bare `[/]` on its own would be a parse error caught elsewhere. Skip.
        pass

    # Legacy qid syntax.
    for m in RE_QID_LEGACY.finditer(md_text):
        line_num = md_text.count("\n", 0, m.start()) + 1
        findings.append(f"{file_label}:{line_num}: legacy `[qid:...]` syntax")
        break

    if not findings:
        return

    msg_prefix = "ERROR" if TAG_LEGACY_MODE == "error" else "WARN "
    for f in findings:
        suffix = (" — fix or run `python3 build.py --migrate-tags`"
                  if TAG_LEGACY_MODE == "error"
                  else " — migrate to <<tag>>...<</tag>> via `python3 build.py --migrate-tags`")
        errors.append(f"{f}{suffix}  [{msg_prefix} legacy-tag-syntax]")


def warn_deleted_globals_in_js_content(md_text: str, *, file_label: str,
                                       errors: list[str]) -> None:
    """v3.9 — Scan JS content's FENCED CODE BLOCKS only (4-space-indent paragraphs)
    for references to APIs the JsEngine sandbox has deleted. A code-block
    example showing `globalThis.fetch(...)` would mislead the user, since
    that throws inside the worker. Prose mentions of these names are fine
    and pass through.
    """
    lines = md_text.replace("\r\n", "\n").split("\n")
    for idx, line in enumerate(lines, start=1):
        if not line.startswith("    "):
            continue  # prose — ignore (per v3.9 review's guidance)
        for api in JS_SANDBOX_DELETIONS:
            # Match `globalThis.<api>` or bare `<api>(` style usage.
            patterns = [
                f"globalThis.{api}",
                f"self.{api}",
                f"window.{api}",
            ]
            for pat in patterns:
                if pat in line:
                    errors.append(
                        f"{file_label}:{idx}: code block references "
                        f"sandbox-deleted API '{pat}'. The JsEngine worker "
                        f"removes {api} at boot — examples using it will throw."
                    )


def warn_rust_question_tags(template_text: str, *, errors: list[str]) -> None:
    """v4.0 Stage 2 — verify every tag on a Rust question is in the closed
    RUST_QUESTION_TAGS set. The Rust questions live between STAGE2 sentinels
    in src/index.template.html; absence of the block is not an error (Stage 2
    may be reverted), but any tag outside the closed set is fatal.

    Tags appear as JSON arrays of double-quoted strings: `"tags":["mutability"]`.
    We scan inside the marked block and extract every quoted string from every
    "tags":[...] occurrence.
    """
    s = template_text.find(RUST_QS_BEGIN)
    e = template_text.find(RUST_QS_END, s + len(RUST_QS_BEGIN) if s >= 0 else 0)
    if s < 0 or e < 0:
        return  # Block not present — Stage 2 not landed; no Rust questions to check.
    block = template_text[s:e]
    # Find every `"tags":[ ... ]` array body. Tag values are simple identifiers
    # (no nested brackets), so `[^\]]*` is safe inside the array.
    for m in re.finditer(r'"tags"\s*:\s*\[([^\]]*)\]', block):
        body = m.group(1)
        for tag_m in re.finditer(r'"([^"]+)"', body):
            tag = tag_m.group(1)
            if tag not in RUST_QUESTION_TAGS:
                line_num = (template_text.count("\n", 0, s + m.start()) + 1)
                errors.append(
                    f"src/index.template.html:{line_num}: unknown Rust question tag "
                    f"'{tag}'. Closed set: {', '.join(sorted(RUST_QUESTION_TAGS))}. "
                    f"Add to RUST_QUESTION_TAGS in build.py first if introducing a new tag."
                )


def build_track_bundle(track: str, content_dir: Path, *, valid_qids: set[str],
                       errors: list[str]) -> dict:
    """Build the {cheatsheet, tiers, examples} dict for one track."""
    track_dir = content_dir / track
    if not track_dir.is_dir():
        raise FileNotFoundError(f"missing content dir: {track_dir}")

    # Cheatsheet: ANSI + HTML.
    cs_path = track_dir / "cheatsheet.md"
    if not cs_path.is_file():
        raise FileNotFoundError(f"missing {cs_path}")
    cs_text = cs_path.read_text(encoding="utf-8")
    warn_long_code_blocks(cs_text, file_label=str(cs_path), errors=errors)
    warn_unknown_qids(cs_text, file_label=str(cs_path),
                      valid_qids=valid_qids, errors=errors)
    warn_legacy_tag_usage(cs_text, file_label=str(cs_path), errors=errors)
    if track == "javascript":
        warn_deleted_globals_in_js_content(cs_text, file_label=str(cs_path),
                                           errors=errors)
    cs_ansi, cs_html = render_markdown(
        cs_text, want_html=True, file_label=str(cs_path), errors=errors,
    )

    # Tiers: ANSI only for concepts; ANSI per example.
    tiers: dict[str, str] = {}
    examples: dict[str, list[str]] = {}
    for tier_name, tier_num in TIER_NUMS.items():
        tier_path = track_dir / f"tier-{tier_name}.md"
        if not tier_path.is_file():
            raise FileNotFoundError(f"missing {tier_path}")
        tier_text = tier_path.read_text(encoding="utf-8")
        warn_long_code_blocks(tier_text, file_label=str(tier_path), errors=errors)
        warn_unknown_qids(tier_text, file_label=str(tier_path),
                          valid_qids=valid_qids, errors=errors)
        warn_legacy_tag_usage(tier_text, file_label=str(tier_path), errors=errors)
        if track == "javascript":
            warn_deleted_globals_in_js_content(tier_text, file_label=str(tier_path),
                                               errors=errors)
        concepts_md, example_mds = split_tier_file(
            tier_text, file_label=str(tier_path), errors=errors,
        )
        concepts_ansi, _ = render_markdown(
            concepts_md, want_html=False,
            file_label=f"{tier_path}#concepts", errors=errors,
        )
        tiers[str(tier_num)] = concepts_ansi
        ex_ansis: list[str] = []
        for ei, ex_md in enumerate(example_mds, start=1):
            ex_ansi, _ = render_markdown(
                ex_md, want_html=False,
                file_label=f"{tier_path}#example-{ei}", errors=errors,
            )
            ex_ansis.append(ex_ansi)
        examples[str(tier_num)] = ex_ansis

    return {
        "cheatsheet": {"ansi": cs_ansi, "html": cs_html},
        "tiers": tiers,
        "examples": examples,
    }


def extract_valid_qids(template_text: str) -> set[str]:
    """Pull the set of valid question ids out of the template's QUESTIONS const.

    Matches both the legacy bare-key single-quote form used by SQL/Python/JS
    (`id:'sql_intro_01'`) AND the Rust questions' quoted-key double-quote form
    (`"id":"rs_intro_01"`). The optional quotes around the `id` key plus either
    quote style on the value cover both; without this the 50 Rust qids would be
    invisible to `warn_unknown_qids`, so any `<<qid:rs_...>>` reference in Rust
    content would be flagged as unknown."""
    return set(re.findall(r"""["']?id["']?\s*:\s*["']([a-z0-9_]+)["']""", template_text))


# --------------------------------------------------------------------------------------
# Migration tool: rewrite content files from legacy `[tag]...[/]` syntax to
# v3.10 `<<tag>>...<</tag>>` syntax. Preserves every non-tag byte exactly so
# the rendered bundle is unchanged.
# --------------------------------------------------------------------------------------


def _migrate_one_file(text: str, *, file_label: str,
                      errors: list[str]) -> tuple[str, int]:
    """Rewrite a single markdown file's tag tokens. Returns (new_text, n_changes).

    Walks the source maintaining a tag stack so that legacy `[/]` close tokens
    can be rewritten to the correctly-named `<</tag>>` closer for the
    most-recent open. v3.10-syntax tokens already in the file pass through
    unchanged. Plain `[` / `<` characters that aren't part of any token are
    preserved literally.
    """
    out: list[str] = []
    stack: list[str] = []
    i = 0
    n = len(text)
    n_changes = 0
    line_no = 1

    while i < n:
        c = text[i]
        if c == "\n":
            out.append(c)
            i += 1
            line_no += 1
            continue
        if c not in ("[", "<"):
            # Fast path: emit text until the next interesting character or EOL.
            j = i + 1
            while j < n and text[j] not in ("[", "<", "\n"):
                j += 1
            out.append(text[i:j])
            i = j
            continue

        # v3.10 already-migrated tokens — pass through, but track stack for
        # downstream legacy-close handling consistency.
        if c == "<":
            m = RE_CLOSE_TAG_V310.match(text, i)
            if m:
                tag = m.group(1)
                if stack and stack[-1] == tag:
                    stack.pop()
                # else: structural error; the build's lint will surface it.
                out.append(m.group(0))
                i = m.end()
                continue
            m = RE_QID_V310.match(text, i)
            if m:
                out.append(m.group(0))
                i = m.end()
                continue
            m = RE_OPEN_TAG_V310.match(text, i)
            if m:
                tag = m.group(1)
                if tag in VALID_TAGS:
                    stack.append(tag)
                out.append(m.group(0))
                i = m.end()
                continue
            out.append("<")
            i += 1
            continue

        # c == "[" — try legacy tokens.
        m = RE_CLOSE_TAG_LEGACY.match(text, i)
        if m:
            if not stack:
                errors.append(
                    f"{file_label}:{line_no}: stray [/] with no matching open tag"
                )
                out.append(m.group(0))  # leave it for the build lint to catch
                i = m.end()
                continue
            tag = stack.pop()
            out.append(f"<</{tag}>>")
            n_changes += 1
            i = m.end()
            continue

        m = RE_QID_LEGACY.match(text, i)
        if m:
            out.append(f"<<qid:{m.group(1)}>>")
            n_changes += 1
            i = m.end()
            continue

        m = RE_OPEN_TAG_LEGACY.match(text, i)
        if m:
            tag = m.group(1)
            if tag in VALID_TAGS:
                stack.append(tag)
                out.append(f"<<{tag}>>")
                n_changes += 1
                i = m.end()
                continue
            # Unknown tag name (e.g. `[abc]` where abc isn't a color) — pass
            # through; the build lint will warn separately.
            out.append(m.group(0))
            i = m.end()
            continue

        # A '[' that isn't part of any pattern — pass through.
        out.append("[")
        i += 1

    if stack:
        errors.append(
            f"{file_label}: EOF reached during migration with {len(stack)} "
            f"unclosed tag(s) on stack: {stack!r}. The legacy source is malformed; "
            f"close tags before re-running --migrate-tags."
        )

    return "".join(out), n_changes


def migrate_tags(repo_root: Path) -> int:
    """Walk every content markdown file under src/content/<track>/ and rewrite
    legacy tag syntax to v3.10 syntax in place. Returns 0 on success, 1 if any
    file produced a structural error during migration.
    """
    content_dir = repo_root / "src" / "content"
    if not content_dir.is_dir():
        print(f"FATAL: missing {content_dir}", file=sys.stderr)
        return 2

    targets: list[Path] = []
    for track_dir in sorted(content_dir.iterdir()):
        if not track_dir.is_dir():
            continue
        cs = track_dir / "cheatsheet.md"
        if cs.is_file():
            targets.append(cs)
        for tier_name in TIER_NUMS:
            tp = track_dir / f"tier-{tier_name}.md"
            if tp.is_file():
                targets.append(tp)

    if not targets:
        print("No content files found under src/content/<track>/.")
        return 0

    errors: list[str] = []
    total_changes = 0
    n_files_changed = 0
    for path in targets:
        original = path.read_text(encoding="utf-8")
        new_text, changes = _migrate_one_file(
            original, file_label=str(path), errors=errors,
        )
        if changes > 0:
            path.write_text(new_text, encoding="utf-8")
            n_files_changed += 1
            total_changes += changes
            print(f"  migrated {path}  ({changes} tag tokens rewritten)")
        else:
            print(f"  unchanged {path}")

    if errors:
        print("\nMigration errors:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    print(f"\nMigration complete: {n_files_changed} file(s) updated, "
          f"{total_changes} tag tokens rewritten total.")
    print("Run `python3 build.py --check` to verify; per-track bundle md5s "
          "should match the pre-migration values.")
    return 0


def build(repo_root: Path, *, check_only: bool) -> int:
    template_path = repo_root / "src" / "index.template.html"
    content_dir = repo_root / "src" / "content"
    out_path = repo_root / "index.html"

    template_text = template_path.read_text(encoding="utf-8")
    if PLACEHOLDER not in template_text:
        print(f"FATAL: placeholder `{PLACEHOLDER}` not found in {template_path}",
              file=sys.stderr)
        return 2
    valid_qids = extract_valid_qids(template_text)
    if not valid_qids:
        print(f"WARN: no question ids extracted from template — qid validation disabled.",
              file=sys.stderr)

    errors: list[str] = []
    warn_rust_question_tags(template_text, errors=errors)
    bundle = {
        track: build_track_bundle(
            track, content_dir, valid_qids=valid_qids, errors=errors,
        )
        for track in ("sql", "python", "javascript", "rust")
    }

    if errors:
        print("Lint warnings:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)

    if check_only:
        if errors:
            print(f"\n{len(errors)} warning(s). Fix and re-run.", file=sys.stderr)
            return 1
        print("Lint clean.")
        return 0

    if errors:
        # In build mode we still write, but exit 1 so CI catches it.
        pass

    # Serialize bundle. ensure_ascii so the embedded JSON only uses ASCII (matches
    # the v3.8a style which used \uNNNN escapes for ANSI).
    bundle_json = json.dumps(bundle, ensure_ascii=True, separators=(",", ":"))
    output = template_text.replace(PLACEHOLDER, bundle_json)
    out_path.write_text(output, encoding="utf-8")

    md5 = hashlib.md5(output.encode("utf-8")).hexdigest()
    sql_words = sum(len(re.sub(r"\x1b\[[0-9;]*m", "", v).split())
                    for v in [bundle["sql"]["cheatsheet"]["ansi"],
                              *bundle["sql"]["tiers"].values(),
                              *(s for arr in bundle["sql"]["examples"].values() for s in arr)])
    py_words = sum(len(re.sub(r"\x1b\[[0-9;]*m", "", v).split())
                   for v in [bundle["python"]["cheatsheet"]["ansi"],
                             *bundle["python"]["tiers"].values(),
                             *(s for arr in bundle["python"]["examples"].values() for s in arr)])
    js_words = sum(len(re.sub(r"\x1b\[[0-9;]*m", "", v).split())
                   for v in [bundle["javascript"]["cheatsheet"]["ansi"],
                             *bundle["javascript"]["tiers"].values(),
                             *(s for arr in bundle["javascript"]["examples"].values() for s in arr)])
    rust_words = sum(len(re.sub(r"\x1b\[[0-9;]*m", "", v).split())
                     for v in [bundle["rust"]["cheatsheet"]["ansi"],
                               *bundle["rust"]["tiers"].values(),
                               *(s for arr in bundle["rust"]["examples"].values() for s in arr)])
    print(f"Built {out_path}")
    print(f"  md5:        {md5}")
    print(f"  size:       {len(output):,} bytes")
    print(f"  sql words:  ~{sql_words}")
    print(f"  py words:   ~{py_words}")
    print(f"  js words:   ~{js_words}")
    print(f"  rust words: ~{rust_words}")
    print(f"  warnings:   {len(errors)}")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Build Ghost Training Terminal index.html from src/."
    )
    p.add_argument("--check", action="store_true", help="lint only; do not write index.html")
    p.add_argument("--migrate-tags", action="store_true",
                   help="rewrite legacy [tag]...[/] syntax to v3.10 <<tag>>...<</tag>> "
                        "syntax in every content file under src/content/. Does not "
                        "build index.html.")
    args = p.parse_args(argv)
    repo_root = Path(__file__).resolve().parent
    if args.migrate_tags:
        return migrate_tags(repo_root)
    return build(repo_root, check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
