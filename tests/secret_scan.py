#!/usr/bin/env python3
"""Fail if the repo looks like it contains a credential.

Skips vendor binaries, the scanner's own pattern strings, and the fictional
555 phone numbers in the SQL seed. Exit 0 when clean.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', 'node_modules', 'vendor', '.work', '.claude', '__pycache__'}
SKIP_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.woff', '.woff2', '.wasm', '.zip'}

# Patterns are built at runtime so this file does not contain a literal token.
RULES = [
    ('aws_access_key', r'AKIA' + r'[0-9A-Z]{16}'),
    ('private_key', r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
    ('github_pat', r'ghp_' + r'[A-Za-z0-9]{20,}'),
    ('github_fine', r'github_pat_' + r'[A-Za-z0-9_]{20,}'),
    ('slack', r'xox[baprs]-' + r'[A-Za-z0-9-]{10,}'),
    ('aws_secret_assign', r'(?i)aws_secret_access_key\s*=\s*[\'\"][A-Za-z0-9/+=]{20,}'),
    ('generic_secret_assign', r'(?i)(?:api[_-]?key|secret[_-]?key|password)\s*[:=]\s*[\'\"][A-Za-z0-9/+_=-]{24,}[\'\"]'),
]


def iter_files():
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        if path.name == 'secret_scan.py':
            continue
        yield path


def main():
    compiled = [(name, re.compile(pat)) for name, pat in RULES]
    hits = []
    for path in iter_files():
        try:
            text = path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for name, cre in compiled:
                if cre.search(line):
                    hits.append(f'{path.relative_to(ROOT)}:{lineno}: {name}')
    if hits:
        print('secret scan failed:')
        print('\n'.join(hits))
        return 1
    print('secret scan clean')
    return 0


if __name__ == '__main__':
    sys.exit(main())
