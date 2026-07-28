"""Test bootstrap: make the monorepo packages/services importable without an install step.

Adds every ``packages/*/src`` and ``services/*/src`` directory to ``sys.path`` so tests can
``import asc_domain`` / ``import asc_orchestrator`` etc. In CI/production these are installed
editable; this keeps ``pytest`` runnable from a bare checkout.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent
for _group in ("packages", "services", "stream"):
    for _src in sorted((_ROOT / _group).glob("*/src")):
        p = str(_src.resolve())
        if p not in sys.path:
            sys.path.insert(0, p)
