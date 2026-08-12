#!/usr/bin/env python3
"""Writing guards.

AGENTS.md, under Writing: "Plain dash, never an em dash." The rule had been
stated since the repository's first commits and never enforced, so 766 em dashes
accumulated across ~114 files, almost all arriving when the atlas corpus and the
prod module were integrated. This guard landed in the same PR that made the tree
clean - a guard introduced already-red is a guard people learn to bypass.

The rule is about **prose**. In Markdown, an em dash inside a fenced code block
or an inline code span is being *quoted*, not used as punctuation: documenting
the hazard requires showing the character. Without that distinction the
repository cannot document its own writing rule, and this project's own article
would be unpublishable. Outside Markdown the whole file is prose-checked, since
an em dash in a comment or a docstring is ordinary writing.

Scope is files Git tracks plus non-ignored untracked files, matching
check_links.sh. Tracked-only scope means a brand-new document is invisible until
it is staged, so the author gets the failure from CI instead of the terminal.

Exit 1 on any violation.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

EM_DASH = "—"

# Frozen artifacts. Each is excluded because the em dash in it is not prose we
# maintain, and rewriting it would change a shipped thing:
#
#   prod/app/          the v0.1.0 standalone MVP. The character is a table VALUE
#                      meaning "not applicable", rendered to an operator.
#                      Replacing it edits the product, not the punctuation.
#   prod/docs/v0.1.0/  the archived handoff package documenting a released ZIP.
#                      Its text is supposed to match what shipped.
#
# atlas/public/search-index.json is deliberately NOT excluded. It is generated,
# and it went clean by itself once the corpus did, so an em dash reappearing
# there means the committed index has drifted from the content.
EXCLUDED_PREFIXES = ("prod/app/", "prod/docs/v0.1.0/")

MARKDOWN_SUFFIXES = (".md", ".mdx", ".markdown")
BINARY_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".pdf")

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")


def mask_markdown_code(text: str) -> str:
    """Blank out fenced blocks and inline code spans, preserving line numbers."""
    out = []
    in_fence = False
    for line in text.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        out.append(INLINE_CODE.sub("", line))
    return "\n".join(out)


def scanned_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard", "-z"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [f for f in out.split("\0") if f]


def main() -> int:
    os.chdir(Path(__file__).resolve().parents[2])
    self_path = "tools/policy/check_writing.py"
    status = 0

    print("== no em dashes in prose (AGENTS.md: plain dash, never an em dash) ==")
    violations: list[str] = []
    for name in scanned_files():
        if name.startswith(EXCLUDED_PREFIXES) or name == self_path:
            continue
        path = Path(name)
        if path.suffix.lower() in BINARY_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if EM_DASH not in text:
            continue
        checked = mask_markdown_code(text) if path.suffix in MARKDOWN_SUFFIXES else text
        for i, line in enumerate(checked.split("\n"), 1):
            if EM_DASH in line:
                violations.append(f"{name}:{i}: {line.strip()[:100]}")

    if violations:
        for v in violations:
            print(v)
        print()
        print("Use a plain dash. Two things worth knowing before you fix it:")
        print("  - A line-LEADING em dash needs reflowing, not replacing:")
        print("    '- ' at the start of a Markdown line is a list item.")
        print("  - Inside a code fence or `inline code` the character is quoted,")
        print("    not used as punctuation, and is allowed.")
        print(f"::error::em dash in prose; {'AGENTS.md requires a plain dash'}")
        status = 1
    else:
        print("ok")

    # The exclusions are load-bearing, so they have to keep pointing at
    # something. An exclusion for a path that has moved is a rule nobody can see
    # is dead.
    print("== every excluded path still exists ==")
    missing = [p for p in EXCLUDED_PREFIXES if not Path(p).exists()]
    if missing:
        for p in missing:
            print(f"{p}: excluded by {self_path} but no longer present")
        print(f"::error::stale exclusion; drop it from {self_path} or restore the path")
        status = 1
    else:
        print("ok")

    if status == 0:
        print()
        print("writing guards OK")
    return status


if __name__ == "__main__":
    sys.exit(main())
