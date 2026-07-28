#!/usr/bin/env python3
"""Verify the v0.1.0 handoff package is intact and self-contained.

The product specs live under ``docs/v0.1.0/``; the paths below track that layout. This
script previously pointed at a flat ``docs/`` that had not existed for some time, and
nothing noticed because it was only a Makefile target and never a CI job. It is a CI
job now - see .github/workflows/prod.yml.
"""

import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
SPECS = "docs/v0.1.0"
required = [
    "README.md",
    "VERSION",
    "app/agent_simulation_control_plane_mvp.html",
    "assets/architecture.png",
    f"{SPECS}/01_PRODUCT_REQUIREMENTS.md",
    f"{SPECS}/02_OPERATOR_UI_SPEC.md",
    f"{SPECS}/03_PRODUCT_MANUAL_TUTORIAL.md",
    f"{SPECS}/04_IMPLEMENTATION_HANDOFF.md",
    f"{SPECS}/05_QA_VERIFICATION_PLAN.md",
    f"{SPECS}/06_CICD_AND_DELIVERY_GUIDE.md",
    f"{SPECS}/07_ARCHITECTURE_CONTEXT.md",
    f"{SPECS}/08_GOLDEN_WORKFLOW_TEST_CASES.md",
    "examples/purchase_ambiguity_experiment.json",
]
errors = []
for rel in required:
    p = root / rel
    if not p.exists() or p.stat().st_size == 0:
        errors.append(f"missing or empty: {rel}")

html_path = root / "app/agent_simulation_control_plane_mvp.html"
if html_path.exists():
    html = html_path.read_text(encoding="utf-8")
    checks = {
        "HTML doctype": "<!doctype html" in html.lower(),
        "product title": "Agent Simulation Control Plane" in html,
        "Overview surface": "Overview" in html,
        "Experiments surface": "Experiments" in html,
        "Trajectory surface": "Traject" in html,
        "Transactional workflow": "Transactional" in html,
        "run interaction": "Run Experiment" in html or "Run experiment" in html,
        "result decision": "RELEASE BLOCKED" in html or "Blocked" in html,
    }
    for label, ok in checks.items():
        if not ok:
            errors.append(f"HTML expected surface missing: {label}")
    external = re.findall(r"(?:src|href)=[\"'](https?://[^\"']+)[\"']", html, flags=re.I)
    if external:
        errors.append("unexpected external runtime dependencies: " + ", ".join(external[:5]))
    if "<script" not in html.lower():
        errors.append("HTML contains no script block")

for p in sorted((root / "examples").glob("*.json")):
    try:
        json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {p.name}: {exc}")

if errors:
    print("PACKAGE VERIFICATION FAILED")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("PACKAGE VERIFICATION PASSED")
print(f"Root: {root}")
print(f"Standalone HTML: {html_path.stat().st_size:,} bytes")
print(f"Example JSON files: {len(list((root / 'examples').glob('*.json')))}")
