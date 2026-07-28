# Golden Workflow Test Cases

These tests are the canonical end-to-end behaviors for implementation and verification agents.

## GW-01 — Unsafe transactional retry is blocked

**Given** a Transactional MCP experiment with `make_purchase` timeout/ambiguous outcomes, Basic Retry harness, no enforced idempotency reuse, and a blocking zero-tolerance duplicate-risk policy  
**When** 1,000 seeded iterations are executed  
**Then** at least one timed-out purchase is retried unsafely  
**And** the related trajectory contains `make_purchase → timeout → make_purchase`  
**And** the policy violation is recorded  
**And** the final release decision is **Blocked**  
**And** the decision links to the affected trajectories.

## GW-02 — Transaction-safety recovery changes the decision

**Given** the same workflow, seeds, and failure profile as GW-01  
**And** the harness classifies timeout as ambiguous transaction  
**And** recovery calls `transaction_status` before any repeat purchase  
**And** any allowed retry preserves the original idempotency key  
**When** the experiment is rerun  
**Then** duplicate-transaction policy violations are zero  
**And** blocking gates pass  
**And** recovered iterations are distinguished from first-attempt success  
**And** any remaining retry or cost threshold may produce warnings without blocking.

## GW-03 — Same-seed replay preserves dependency outcomes

**Given** a completed trajectory with a stored experiment version and seed  
**When** the operator selects Replay Same Seed  
**Then** the simulated tool/dependency outcomes and sampled latencies match the original within documented deterministic behavior  
**And** the replay links to the original trajectory  
**And** runtime/model nondeterminism, if enabled, is clearly labeled.

## GW-04 — New-seed replay changes sampled conditions

**Given** the same completed trajectory  
**When** the operator selects Replay New Seed  
**Then** a new seed is stored  
**And** at least one sampled environment outcome may differ  
**And** the configuration remains unchanged.

## GW-05 — Reliable linear support passes

**Given** Linear Chat with knowledge search, evidence grounding, structured-output validation, and bounded citation retry  
**When** 100 seeded iterations are executed  
**Then** malformed responses are normalized or repaired within limits  
**And** unauthorized profile access is refused  
**And** validation success meets the configured threshold  
**And** the decision is Passed or Passed with warnings.

## GW-06 — Hierarchical research exposes cost/latency tradeoff

**Given** a primary research agent with three parallel sub-agents  
**And** high answer quality but repeated or slow sub-agent calls  
**When** 250 iterations are executed  
**Then** quality gates pass  
**And** a cost or P95 latency manual-review gate fails  
**And** the final decision is Manual review  
**And** the operator can identify the expensive agents and trajectories.

## GW-07 — Department handoff context loss is blocked

**Given** a Router → Department → Specialist workflow  
**And** a failure profile that occasionally removes required account context  
**When** the specialist attempts a scoped customer tool call  
**Then** the handoff validator or tool policy rejects the call  
**And** the agent refuses or escalates safely  
**And** no wrong-customer data is returned  
**And** any actual cross-scope access attempt produces a blocking policy violation.

## GW-08 — Failure probabilities are validated

**Given** an outcome distribution whose enabled probabilities do not total 100%  
**When** the operator attempts to continue from Failure Profiles  
**Then** progression is blocked  
**And** the remaining or excess percentage is displayed  
**And** the invalid configuration cannot be run through the API.

## GW-09 — Completed experiment configuration is immutable

**Given** an experiment version with a completed run  
**When** the operator tries to edit the agent, failure profile, harness, or gates  
**Then** direct editing is denied  
**And** the UI offers Clone and Modify  
**And** the clone records lineage to the original version.

## GW-10 — Stop preserves completed evidence

**Given** a running 1,000-iteration experiment  
**When** the operator selects Stop and confirms  
**Then** no new iterations begin  
**And** active iterations finish or are cancelled according to policy  
**And** completed iterations, events, trajectories, metrics, and cost remain queryable  
**And** queued iterations are marked cancelled rather than failed.

## GW-11 — Telemetry delay does not corrupt results

**Given** the event/analytics consumer is delayed or unavailable  
**When** workers complete iterations  
**Then** run results are durably retained  
**And** the UI reports delayed telemetry or incomplete analytics  
**And** events can be replayed into aggregation later.

## GW-12 — Gate severity determines decision

**Given** one failed warning gate, one failed manual-review gate, and no failed blocking gate  
**When** final gate evaluation completes  
**Then** the decision is Manual review  
**And** the warning is also listed  
**And** the result is not mislabeled Blocked or Passed.

## GW-13 — Policy violation blocks despite high success

**Given** 99.9% successful iterations and one cross-tenant or duplicate-transaction policy violation  
**And** the relevant gate threshold is zero with blocking severity  
**When** evaluation completes  
**Then** the release is Blocked.

## GW-14 — Export matches displayed result

**Given** a completed run  
**When** the operator exports configuration and result JSON  
**Then** displayed metrics, gate results, identifiers, versions, and decision match the exported artifact  
**And** sensitive data is redacted.

## GW-15 — Accessibility of critical path

**Given** the operator uses only a keyboard and a screen reader  
**When** they create and run the Purchase Ambiguity experiment and inspect the result  
**Then** all required controls are reachable  
**And** focus order is logical  
**And** status and chart meaning are available without color alone.
