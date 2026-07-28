# Acceptance Matrix

| ID | Capability | Verification | Priority |
|---|---|---|---|
| AC-001 | Standalone MVP opens without internet | Open HTML and navigate all primary pages | Critical |
| AC-002 | Four workflow templates are selectable | Builder Step 1 | Critical |
| AC-003 | Persona and primary agent configurable | Builder Steps 2–3 | Critical |
| AC-004 | Hierarchical sub-agents supported to depth 2 | Hierarchical and routing presets | High |
| AC-005 | Tool outcomes total 100% | Invalid probability test | Critical |
| AC-006 | Harness supports classified bounded recovery | Transaction Safety preset | Critical |
| AC-007 | Live run updates progress/events/gates | Start Purchase experiment | Critical |
| AC-008 | Unsafe purchase candidate is blocked | GW-01 | Critical |
| AC-009 | Corrected purchase candidate changes decision | GW-02 | Critical |
| AC-010 | Candidate and baseline metrics compare correctly | Results table/export | Critical |
| AC-011 | Failed trajectory explains root cause | Open duplicate-risk trace | Critical |
| AC-012 | Same-seed replay preserves dependency outcomes | GW-03 | High |
| AC-013 | Completed config is immutable | GW-09 | Critical |
| AC-014 | Stop preserves completed evidence | GW-10 | High |
| AC-015 | Exported JSON matches UI | GW-14 | High |
| AC-016 | Keyboard critical path works | GW-15 | High |
| AC-017 | Sensitive fields are sanitized | Security test fixtures | Critical |
| AC-018 | Telemetry delay is non-destructive | GW-11 | High |
| AC-019 | Gate severity maps to final decision | GW-12 | Critical |
| AC-020 | Policy violation blocks despite high success | GW-13 | Critical |
