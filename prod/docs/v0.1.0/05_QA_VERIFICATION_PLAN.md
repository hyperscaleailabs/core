# QA and Verification Plan

## 1. Verification strategy

Quality is verified at five layers:

1. **Static contract verification:** schemas, required fields, immutable versions, probability totals, and gate definitions.
2. **Deterministic unit verification:** seeded random outcomes, cost/latency calculations, recovery rules, and gate decisions.
3. **Service integration verification:** experiment creation, run state, event streaming, aggregation, persistence, and replay.
4. **End-to-end operator verification:** golden workflows through the UI.
5. **Production-readiness verification:** security, observability, scalability, isolation, and CI/CD evidence.

## 2. Release-critical scenarios

The following must pass before each release:

- Purchase ambiguity blocks under unsafe retry.
- Same scenario passes blocking gates after idempotency/status-verification recovery.
- Same-seed replay reproduces dependency outcomes.
- Completed experiment versions cannot be edited.
- Gate calculations use the correct sample and severity.
- Policy violations cannot be hidden by high aggregate success.
- Stopping a run preserves completed iterations.
- Telemetry correlates iteration, trajectory, trace, and gate evidence.

Detailed cases are in `08_GOLDEN_WORKFLOW_TEST_CASES.md`.

## 3. Unit test areas

### Probability and sampling

- Exclusive outcome probabilities must total exactly 1.0 within an allowed numeric tolerance.
- Disabled outcomes are not sampled.
- Same seed and configuration produce the same dependency sequence.
- New seed changes at least one outcome over a sufficient sample.
- Correlation rules modify the intended conditional probability only.

### Harness

- Failure classification maps known errors correctly.
- Retry limits are enforced per stage and trajectory.
- Authorization failures never retry.
- Ambiguous transactions use status verification.
- Idempotency key is preserved when retry is allowed.
- Cost, token, step, and duration bounds terminate execution.
- Recovery outcome is labeled separately from first-attempt success.

### Metrics

- Rates use the correct denominator.
- Percentage-point and percentage changes are not confused.
- Cost per success excludes unsuccessful outcomes from the denominator only as defined.
- P50/P95/P99 calculations are stable and documented.
- Cancelled iterations do not incorrectly count as failures.
- Projected monthly cost uses explicit traffic assumptions.

### Gate engine

- Warning does not block.
- Manual-review severity produces review, not block.
- Any failed blocking gate produces Blocked.
- Policy violations with threshold zero block.
- Minimum sample size can produce Inconclusive/Review according to policy.
- Final decisions are immutable for a completed run; overrides create audit records.

## 4. API and integration verification

- Create, read, clone, and archive experiment.
- Reject modification of an experiment version with completed runs.
- Start, pause, resume, and stop run with valid transitions.
- Reject invalid transitions.
- Stream events in chronological order or with explicit sequence numbers.
- Persist results if the analytics consumer is delayed.
- Replay the same seed and retain lineage to the original trajectory.
- Export configuration and result JSON matching schema.

## 5. UI verification

### Navigation

All primary routes load, highlight active navigation, support browser back/forward, and preserve filters in URLs where specified.

### Builder

- Required fields block progression.
- Workflow changes warn before removing incompatible agents.
- Failure probabilities display remaining percentage and reject invalid totals.
- Cost and runtime estimates update after model, iterations, parallelism, or harness changes.
- Unsaved changes prompt works.

### Live run

- Progress, counters, cost, workers, and provisional gates update.
- Pause does not discard active work.
- Stop confirmation is accurate.
- Clicking a failure filters events and trajectories.
- Telemetry-delay and analytics-incomplete states are distinct.

### Results

- Decision text matches gate engine output.
- Candidate and baseline labels are never reversed.
- Each failed gate links to related trajectories.
- Projected cost updates when monthly volume changes.
- Exported result matches displayed values.

### Trajectory inspector

- Events are ordered and nested correctly.
- Sanitized payload is shown; secrets are not.
- Decision summary does not expose hidden chain-of-thought.
- Same-seed and new-seed replays are distinguishable.

## 6. Accessibility verification

- Keyboard-only completion of primary workflow.
- Focus order and visible focus.
- Dialog focus trap and return.
- Form labels and error association.
- Status communicated without color alone.
- Chart summaries available.
- Table headers and row labels available to screen readers.
- WCAG AA contrast.
- Reduced-motion behavior for live updates.

## 7. Security and privacy verification

- Secrets never appear in prompts, logs, events, exports, or screenshots.
- Tool authorization is enforced server-side, not only in the UI.
- Cross-tenant identifiers cannot be substituted.
- Transactional actions require configured confirmation and idempotency.
- Sensitive fields are redacted before queue emission.
- Audit records are append-only.
- Retention and deletion policies are testable.

## 8. Performance verification

Initial targets:

- Operator API reads normally respond in under one second in the development environment.
- UI remains interactive during a 1,000-iteration run.
- Event updates are batched to avoid rendering overload.
- 100 concurrent or rapidly batched iterations do not violate configured resource limits.
- Telemetry consumer delay does not lose run results.

## 9. Test environments

- **Static package:** current standalone HTML.
- **Local integration:** frontend + API + deterministic simulator + database.
- **Development Kubernetes:** worker scaling, queue, telemetry, and observability.
- **Staging:** real model/MCP adapters with restricted credentials and synthetic data.

## 10. Test evidence required in CI

- JUnit or equivalent unit/integration report.
- Browser end-to-end report and trace.
- Accessibility report.
- Coverage summary.
- Schema compatibility report.
- Dependency and container scan.
- Golden workflow result fixtures.
- Screenshots for Overview, Builder, Live Run, Results, and Trajectory.
- Performance summary for simulation changes.

## 11. Exit criteria

A release is eligible when:

- All release-critical scenarios pass.
- No open critical/high security issue.
- No unexplained change in golden workflow outputs.
- Coverage and quality thresholds pass.
- Build is reproducible.
- Required evidence artifacts are retained.
- Rollback procedure is verified for deployment-affecting changes.
