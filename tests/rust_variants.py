#!/usr/bin/env python3
"""Extra Rust grader cases that the embedded 319-case bank does not cover.

The 319 cases stay in the question `qa` blocks and are run by qa_harness.py.
This file checks the v4.0.5 additions: optional type ascriptions and comments.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_harness import (  # noqa: E402
    TEMPLATE_PATH,
    extract_alt_library,
    extract_rust_questions,
    grade_pattern,
)


def questions_by_id():
    template = TEMPLATE_PATH.read_text(encoding='utf-8')
    tiers = extract_rust_questions(template, extract_alt_library(template))
    out = {}
    for tier_qs in tiers.values():
        for q in tier_qs:
            out[q['id']] = q
    return out


CASES = [
    ('rs_intro_01', 'let shop_open: bool = true;', True, None),
    ('rs_intro_01', 'let shop_open = true; // open', True, None),
    ('rs_intro_01', 'let shop_open = true; /* open */', True, None),
    ('rs_intro_01', 'let shop_open = true // open', False, 'missing `;`'),
    ('rs_intro_01', 'let shop_open: bool = true', False, 'missing `;`'),
    ('rs_intro_02', 'let mut counter: i32 = 0;', True, None),
    ('rs_ama_02', 'let greeting = String::from("Hello");', False, 'structure mismatch'),
    ('rs_ama_02', 'let greeting: String = String::from("Hello");', True, None),
]


def main():
    by_id = questions_by_id()
    failed = 0
    for qid, src, expect_ok, expect_msg in CASES:
        q = by_id[qid]
        result = grade_pattern(src, q)
        ok = bool(result.get('ok'))
        detail = result.get('detail') or ''
        bad = ok != expect_ok or (expect_msg and expect_msg not in detail)
        status = 'FAIL' if bad else 'ok'
        if bad:
            failed += 1
        print(f'  {status}  {qid}  {src!r}  -> ok={ok} detail={detail!r}')
    print()
    if failed:
        print(f'{failed} variant case(s) failed')
        return 1
    print(f'ALL GREEN ({len(CASES)} variant cases)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
