#!/usr/bin/env python3
"""tests/qa_harness.py - v4.0 Stage 2 QA harness for the Rust pattern-match grader.

Reads Rust question definitions from src/index.template.html, runs each
question's qa.accept and qa.reject test cases through a Python port of
RustEngine's grading logic, and reports per-question and aggregate results.

The Python grader here MUST stay in sync with the JS RustEngine class in
src/index.template.html. Any change to one is a change to both.

Exit code: 0 if every accept passes and every reject produces a failure
detail containing the expected substring. 1 otherwise.

Usage: python3 tests/qa_harness.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


# ============================================================
# Python port of RustEngine grading logic.
# Mirror of the JS implementation in src/index.template.html.
# ============================================================

WORD_RE = re.compile(r"[A-Za-z0-9_']")


def normalize(s):
    """Pass 1: identify string/char literal ranges. Pass 2: emit char-by-char,
    preserving literal interiors and collapsing/dropping whitespace outside
    literals per the locked design. Lifetime apostrophes ('a, 'static) are
    part of the surrounding token, not a literal delimiter.
    """
    if s is None:
        return ''
    s = str(s)
    n = len(s)
    literals = []
    i = 0
    while i < n:
        c = s[i]
        if c == '"':
            j = i + 1
            while j < n and s[j] != '"':
                if s[j] == '\\' and j + 1 < n:
                    j += 2
                else:
                    j += 1
            if j < n:
                j += 1
            literals.append((i, j))
            i = j
            continue
        if c == 'r' and i + 1 < n and s[i + 1] == '"':
            j = i + 2
            while j < n and s[j] != '"':
                j += 1
            if j < n:
                j += 1
            literals.append((i, j))
            i = j
            continue
        if c == "'":
            if i + 3 < n and s[i + 1] == '\\' and s[i + 3] == "'":
                literals.append((i, i + 4))
                i += 4
                continue
            if i + 2 < n and s[i + 1] != "'" and s[i + 1] != '\\' and s[i + 2] == "'":
                literals.append((i, i + 3))
                i += 3
                continue
            i += 1
            continue
        i += 1

    out = []
    li = 0
    i = 0
    while i < n:
        if li < len(literals) and i == literals[li][0]:
            out.append(s[literals[li][0]:literals[li][1]])
            i = literals[li][1]
            li += 1
            continue
        c = s[i]
        if c.isspace():
            j = i + 1
            while j < n and s[j].isspace():
                j += 1
            prev = out[-1][-1] if out else ''
            nxt = s[j] if j < n else ''
            if WORD_RE.match(prev) and WORD_RE.match(nxt):
                out.append(' ')
            i = j
            continue
        out.append(c)
        i += 1
    result = ''.join(out)
    result = re.sub(r",(\s*[\)\]\}])", r"\1", result)
    return result.strip()


def build_reverse_alt_map(alts_map):
    entries = []
    for canon, alts in (alts_map or {}).items():
        if not isinstance(alts, list):
            continue
        canon_norm = normalize(canon)
        for alt in alts:
            entries.append((normalize(alt), canon_norm))
    entries.sort(key=lambda x: len(x[0]), reverse=True)
    return entries


def apply_alternatives(s, reverse_map):
    if not reverse_map:
        return s
    n = len(s)
    out = []
    i = 0
    while i < n:
        matched = None
        for alt, canon in reverse_map:
            if not alt:
                continue
            if i + len(alt) > n:
                continue
            if s[i:i + len(alt)] != alt:
                continue
            prev = s[i - 1] if i > 0 else ''
            nxt = s[i + len(alt)] if i + len(alt) < n else ''
            if WORD_RE.match(alt[0]) and prev and WORD_RE.match(prev):
                continue
            if WORD_RE.match(alt[-1]) and nxt and WORD_RE.match(nxt):
                continue
            matched = (alt, canon)
            break
        if matched:
            out.append(matched[1])
            i += len(matched[0])
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


def truncate(s, n=80):
    s = str(s) if s is not None else ''
    return s[:n - 1] + '…' if len(s) > n else s


def grade_pattern(user_code, question):
    a = question.get('assertion', {})
    if a.get('type') != 'pattern':
        return {'ok': False, 'detail': 'RustEngine requires a pattern assertion.'}
    user_norm = normalize(user_code)
    tags = question.get('tags', []) or []

    for f in (a.get('forbidden') or []):
        f_norm = normalize(f)
        if f_norm and f_norm in user_norm:
            reason = (' — ' + question['forbid_reason']) if question.get('forbid_reason') else ''
            return {'ok': False, 'detail': 'uses `' + f + '`' + reason}

    for r in (a.get('required') or []):
        r_norm = normalize(r)
        if r_norm and r_norm not in user_norm:
            return {'ok': False, 'detail': 'missing `' + r + '`'}

    canon_norm = normalize(a.get('structure') or '')
    reverse_map = build_reverse_alt_map(a.get('alternatives') or {})
    user_sub = apply_alternatives(user_norm, reverse_map)
    if user_sub == canon_norm:
        return {'ok': True}

    return {'ok': False, 'detail': grammar_lite(user_sub, canon_norm, user_code, a, tags)}


def grammar_lite(user_norm, canon_norm, user_raw, assertion, tags):
    has = lambda t: t in tags
    if has('mutability') and re.search(r'\bmut\b', canon_norm) and not re.search(r'\bmut\b', user_norm):
        return 'binding needs `mut`'
    if canon_norm.endswith(';') and not user_norm.endswith(';'):
        return 'missing `;` at end of statement'
    if (has('borrowing') or has('closures') or has('iterators')) \
            and '|&' in canon_norm and '|&' not in user_norm:
        return 'wrong borrow syntax — try `|&w|` or `*w`'
    if has('traits') and re.search(r'\bimpl\b[^{]*\bfor\b', canon_norm) \
            and re.search(r'\bimpl\b', user_norm) \
            and not re.search(r'\bimpl\b[^{]*\bfor\b', user_norm):
        return 'missing `for <Type>` in impl block'
    u = truncate(str(user_raw or ''), 80)
    e = truncate(str(assertion.get('structure') or ''), 80)
    return 'structure mismatch\n   your:     ' + u + '\n   expected: ' + e


# ============================================================
# Extraction: pull RUST_ALTERNATIVES_LIBRARY and the rust questions
# block out of src/index.template.html.
# ============================================================

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / 'src' / 'index.template.html'

ALT_LIB_BEGIN = 'STAGE2_RUST_ALTERNATIVES_LIBRARY_BEGIN'
ALT_LIB_END = 'STAGE2_RUST_ALTERNATIVES_LIBRARY_END'
RUST_QS_BEGIN = 'STAGE2_RUST_QUESTIONS_BEGIN'
RUST_QS_END = 'STAGE2_RUST_QUESTIONS_END'


def find_balanced_braces(text, start_idx):
    """Given index of an opening { in text, return index just past the matching }.
    Skips over string literals so a } inside a string doesn't fool the counter."""
    depth = 0
    i = start_idx
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"':
            i += 1
            while i < n and text[i] != '"':
                if text[i] == '\\' and i + 1 < n:
                    i += 2
                else:
                    i += 1
            i += 1
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def extract_alt_library(template):
    s = template.find(ALT_LIB_BEGIN)
    e = template.find(ALT_LIB_END, s + len(ALT_LIB_BEGIN) if s >= 0 else 0)
    if s < 0 or e < 0:
        raise RuntimeError('RUST_ALTERNATIVES_LIBRARY markers not found in template')
    block = template[s:e]
    m = re.search(r'const\s+RUST_ALTERNATIVES_LIBRARY\s*=\s*\{', block)
    if not m:
        raise RuntimeError('RUST_ALTERNATIVES_LIBRARY declaration not found inside markers')
    brace_abs = s + m.end() - 1
    brace_end = find_balanced_braces(template, brace_abs)
    if brace_end < 0:
        raise RuntimeError('Unbalanced braces in RUST_ALTERNATIVES_LIBRARY block')
    raw = template[brace_abs:brace_end]
    raw = re.sub(r',(\s*[\]\}])', r'\1', raw)
    return json.loads(raw)


def extract_rust_questions(template, alt_library):
    s = template.find(RUST_QS_BEGIN)
    e = template.find(RUST_QS_END, s + len(RUST_QS_BEGIN) if s >= 0 else 0)
    if s < 0 or e < 0:
        raise RuntimeError('rust questions markers not found in template')
    block = template[s:e]
    m = re.search(r'rust\s*:\s*\{', block)
    if not m:
        raise RuntimeError('rust: { not found between question markers')
    brace_abs = s + m.end() - 1
    brace_end = find_balanced_braces(template, brace_abs)
    if brace_end < 0:
        raise RuntimeError('Unbalanced braces in rust questions block')
    raw = template[brace_abs:brace_end]

    # Quote bare-identifier tier keys so the block becomes JSON-compatible.
    raw = re.sub(r'\b(introductory|amateur|intermediate|experienced|master)\s*:',
                 r'"\1":', raw)

    # Substitute RUST_ALTERNATIVES_LIBRARY.NAME references with the JSON of that group.
    def alt_repl(m_):
        name = m_.group(1)
        if name not in alt_library:
            raise RuntimeError('Unknown alternatives library group referenced: ' + name)
        return json.dumps(alt_library[name])
    raw = re.sub(r'RUST_ALTERNATIVES_LIBRARY\.([A-Z_]+)', alt_repl, raw)

    # Strip trailing commas.
    raw = re.sub(r',(\s*[\]\}])', r'\1', raw)

    return json.loads(raw)


# ============================================================
# Harness runner.
# ============================================================

def run_harness():
    template = TEMPLATE_PATH.read_text(encoding='utf-8')
    alt_library = extract_alt_library(template)
    rust_tiers = extract_rust_questions(template, alt_library)

    tier_order = ('introductory', 'amateur', 'intermediate', 'experienced', 'master')
    questions = []
    for tier_name in tier_order:
        for q in (rust_tiers.get(tier_name) or []):
            questions.append((tier_name, q))

    accept_pass = 0
    accept_fail = 0
    reject_pass = 0
    reject_fail = 0
    failures = []
    per_q = []

    for tier_name, q in questions:
        qid = q.get('id', '?')
        qa = q.get('qa', {}) or {}
        accept = qa.get('accept', []) or []
        reject = qa.get('reject', []) or []
        a_pass = a_fail = r_pass = r_fail = 0

        for s in accept:
            r = grade_pattern(s, q)
            if r.get('ok'):
                a_pass += 1
                accept_pass += 1
            else:
                a_fail += 1
                accept_fail += 1
                failures.append({
                    'qid': qid, 'kind': 'accept', 'input': s,
                    'actual': 'ok=False, detail=' + str(r.get('detail', '')),
                })

        for rj in reject:
            inp = rj.get('input', '')
            expect_msg = rj.get('expect_msg', '')
            r = grade_pattern(inp, q)
            if r.get('ok'):
                r_fail += 1
                reject_fail += 1
                failures.append({
                    'qid': qid, 'kind': 'reject', 'input': inp,
                    'actual': 'ok=True (graded as correct, but expected reject)',
                    'expected_msg': expect_msg,
                })
            elif expect_msg and expect_msg not in (r.get('detail') or ''):
                r_fail += 1
                reject_fail += 1
                failures.append({
                    'qid': qid, 'kind': 'reject', 'input': inp,
                    'actual': 'detail=' + str(r.get('detail', '')),
                    'expected_msg': expect_msg,
                })
            else:
                r_pass += 1
                reject_pass += 1

        per_q.append((tier_name, qid, a_pass, a_fail, r_pass, r_fail))

    print('v4.0 Stage 2 QA harness - Rust pattern-match grader')
    print('source: ' + str(TEMPLATE_PATH))
    print('questions: %d  (%d tiers populated)' % (
        len(questions),
        sum(1 for t in tier_order if rust_tiers.get(t)),
    ))
    print('')
    print('  %-14s  %-12s   accept       reject' % ('tier', 'qid'))
    print('  %-14s  %-12s  pass fail    pass fail' % ('----', '---'))
    for tier_name, qid, a_p, a_f, r_p, r_f in per_q:
        print('  %-14s  %-12s  %4d %4d    %4d %4d' % (tier_name, qid, a_p, a_f, r_p, r_f))
    print('')
    print('TOTAL: accept %d pass / %d fail   reject %d pass / %d fail' % (
        accept_pass, accept_fail, reject_pass, reject_fail,
    ))

    if failures:
        print('')
        print('FAILURES (%d):' % len(failures))
        for f in failures:
            print('  [%s] %s' % (f['qid'], f['kind']))
            print('     input:    %r' % f['input'])
            print('     actual:   %s' % f['actual'])
            if 'expected_msg' in f:
                print('     expected: %r (substring of detail)' % f['expected_msg'])
        return 1

    print('')
    print('ALL GREEN.')
    return 0


if __name__ == '__main__':
    sys.exit(run_harness())
