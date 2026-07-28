"""Deterministic RNG keyed by (seed, *keys).

All stochastic choices in the kernel derive from this so that same-seed replay reproduces
dependency outcomes (GW-03) and new-seed replay may differ (GW-04). It is a hash-based uniform
in [0, 1) — reproducible across processes and Python versions (unlike ``random``'s internal state).
"""

from __future__ import annotations

import hashlib

_DENOM = float(1 << 64)


def uniform(seed: int, *keys: object) -> float:
    """Return a deterministic float in [0, 1) for the given seed and key path."""
    h = hashlib.sha256()
    h.update(str(seed).encode())
    for k in keys:
        h.update(b"|")
        h.update(str(k).encode())
    return int.from_bytes(h.digest()[:8], "big") / _DENOM
