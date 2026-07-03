#!/usr/bin/env python3
"""
patch_synchronizer_cb404.py — v5.2.16 circuit-breaker 404 fix

Problem:
    In core/db/ubec_data_synchronizer.py, the outer `except` of the
    operations-sync method calls self.rate_limiter.record_failure() for EVERY
    exception. A 404 from GET /accounts/{id}/operations means the account has
    no operation history — an expected "no data" response, not a failure.
    Counting those 404s tripped the circuit breaker mid-sync (threshold=10),
    which then rejected all remaining accounts. Result: full syncs stalled at
    ~181 of ~622 UBEC holders.

Fix (surgical, one block):
    Inspect the exception for an HTTP 404. On 404, log at debug and return 0
    WITHOUT recording a breaker failure. All other exceptions behave exactly as
    before (record_failure + error log). Preserves the existing "don't raise /
    return 0" contract. Genuine failures (timeouts, 5xx, 429) still trip the
    breaker as designed (Principle #9 intact).

Safety:
    * Idempotent — detects an already-patched file and exits cleanly.
    * Verifies the ORIGINAL block is present exactly once before touching it.
    * Writes a timestamped .bak backup.
    * Compiles the result with py_compile before saving; aborts on syntax error.
    * Refuses to run if it cannot find exactly one match (fails loud, changes nothing).

Usage:
    python3 patch_synchronizer_cb404.py /srv/ubec/protocol/core/db/ubec_data_synchronizer.py
    # add --dry-run to preview without writing

License (code): GNU AGPL v3.0
This project uses the services of Claude and Anthropic PBC to inform our
decisions and recommendations. This project was made possible with the
assistance of Claude and Anthropic PBC.
"""
import sys
import os
import re
import shutil
import tempfile
import py_compile
from datetime import datetime

# The exact original block we replace. Matched with flexible leading indentation
# so it works regardless of how deeply the method is nested.
OLD_BODY = [
    "except Exception as e:",
    "    self.rate_limiter.record_failure()",
    '    self.logger.error(f"Failed to sync operations for {account_id[:8]}...: {e}")',
    "    # Don't raise - operations sync failure shouldn't block account sync",
    "    return 0",
]

# Sentinel proving the file is already patched.
ALREADY_PATCHED_MARK = "v5.2.16: A 404 from /accounts/{id}/operations"

NEW_BODY_TEMPLATE = '''{i}except Exception as e:
{i}    # v5.2.16: A 404 from /accounts/{{id}}/operations means the account
{i}    # simply has no operation history - an expected "no data" response,
{i}    # NOT a service failure. Counting it against the circuit breaker caused
{i}    # the breaker to trip mid-sync on accounts with no operations, blocking
{i}    # all remaining accounts. Only genuine failures (timeouts, 5xx, 429)
{i}    # should count toward the breaker.
{i}    status = getattr(getattr(e, "response", None), "status_code", None)
{i}    if status is None:
{i}        status = getattr(e, "status", None)
{i}    if status == 404:
{i}        self.logger.debug(
{i}            f"    No operations for {{account_id[:8]}}... (404 - expected)"
{i}        )
{i}    else:
{i}        self.rate_limiter.record_failure()
{i}        self.logger.error(
{i}            f"Failed to sync operations for {{account_id[:8]}}...: {{e}}"
{i}        )
{i}    # Don't raise - operations sync failure shouldn't block account sync
{i}    return 0'''


def build_old_pattern():
    """Regex that matches the OLD block at any indentation, capturing the indent."""
    # First line captures leading whitespace as group 'i'; subsequent lines must
    # share that indent + the relative indentation shown in OLD_BODY.
    first = r"(?P<i>[ \t]+)" + re.escape(OLD_BODY[0])
    rest = []
    for line in OLD_BODY[1:]:
        # each subsequent original line is indent + its own leading spaces
        stripped = line
        rest.append(r"(?P=i)" + re.escape(stripped))
    return re.compile("\n".join([first] + rest))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry_run = "--dry-run" in sys.argv
    if len(args) != 1:
        print("usage: patch_synchronizer_cb404.py <path-to-ubec_data_synchronizer.py> [--dry-run]")
        return 2
    path = args[0]
    if not os.path.isfile(path):
        print(f"ERROR: file not found: {path}")
        return 2

    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    if ALREADY_PATCHED_MARK in src:
        print("Already patched (v5.2.16 marker present). No changes made.")
        return 0

    pattern = build_old_pattern()
    matches = list(pattern.finditer(src))
    if len(matches) == 0:
        print("ERROR: original block not found. File may differ from expected.")
        print("       No changes made. Paste the current block so the patch can be adjusted.")
        return 3
    if len(matches) > 1:
        print(f"ERROR: found {len(matches)} matching blocks; expected exactly 1.")
        print("       Aborting to avoid a wrong edit. No changes made.")
        return 3

    m = matches[0]
    indent = m.group("i")
    new_block = NEW_BODY_TEMPLATE.format(i=indent)
    patched = src[: m.start()] + new_block + src[m.end():]

    if dry_run:
        print("--- DRY RUN: would replace this block ---")
        print(m.group(0))
        print("--- with ---")
        print(new_block)
        return 0

    # Verify the patched source compiles before writing over the original.
    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8")
    try:
        tmp.write(patched)
        tmp.flush()
        tmp.close()
        py_compile.compile(tmp.name, doraise=True)
    except py_compile.PyCompileError as e:
        print("ERROR: patched file failed to compile; original left untouched.")
        print(e)
        os.unlink(tmp.name)
        return 4
    os.unlink(tmp.name)

    backup = f"{path}.bak.{datetime.now():%Y%m%d_%H%M%S}"
    shutil.copy2(path, backup)
    with open(path, "w", encoding="utf-8") as f:
        f.write(patched)

    print("PATCH APPLIED (v5.2.16 circuit-breaker 404 fix)")
    print(f"  file:   {path}")
    print(f"  backup: {backup}")
    print(f"  indent: {len(indent)} chars")
    print("  Verify: python3 -c \"import ast; ast.parse(open('%s').read()); print('parses OK')\"" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
