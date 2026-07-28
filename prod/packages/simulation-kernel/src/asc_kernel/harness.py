"""Harness modes and the tool cost/latency model for WF-04.

Two harnesses drive the Purchase Ambiguity golden workflow:
- ``BASIC_RETRY`` (unsafe): on an ambiguous/timeout transaction it retries ``make_purchase`` with a
  fresh idempotency key, creating duplicate-transaction risk (GW-01).
- ``TRANSACTION_SAFETY`` (safe): it classifies timeout as an ambiguous transaction and queries
  ``transaction_status`` before any repeat; safe retries reuse the original idempotency key (GW-02).
"""

from __future__ import annotations

from enum import StrEnum


class HarnessMode(StrEnum):
    BASIC_RETRY = "basic_retry"
    TRANSACTION_SAFETY = "transaction_safety"


# Latency (ms) contributed by each tool call, per make_purchase outcome where relevant.
CHECK_INVENTORY_MS = 150
TRANSACTION_STATUS_MS = 300
MAKE_PURCHASE_MS = {
    "success": 350,
    "insufficient_funds": 300,
    "processing_delay": 1500,
    "service_unavailable": 400,
    "timeout": 2000,
    "ambiguous_completion": 1800,
    "malformed_response": 500,
}

# Cost (USD) per tool call.
COST_CHECK_INVENTORY = 0.02
COST_MAKE_PURCHASE = 0.05
COST_TRANSACTION_STATUS = 0.02
