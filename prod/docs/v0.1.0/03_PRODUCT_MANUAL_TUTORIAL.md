# Product Manual and Operator Tutorial

## 1. What this product is

The Agent Simulation Control Plane is an operator console for testing complete AI-agent workflows before release. It is designed for systems where results depend not only on one model response, but also on tools, external services, sub-agents, access policies, validation, retries, and recovery logic.

The core question the product answers is:

> When this agent configuration is exposed to realistic variability and dependency failures many times, is it safe, reliable, fast, and affordable enough to release?

The product is not only a prompt evaluation dashboard. It evaluates trajectories and operational behavior across a workflow.

## 2. Who uses it

### Agent developer
Uses the platform to test a new prompt, model, tool, skill, workflow, or recovery change. Their goal is to catch failures before submitting a release candidate.

### AI or ML platform engineer
Owns runtime integration, model gateways, MCP access, agent orchestration, worker execution, and infrastructure limits. Their goal is to make experiments reproducible, isolated, observable, and scalable.

### Evaluation or reliability engineer
Designs failure profiles, metrics, anomaly rules, and evaluation gates. Their goal is to transform vague quality concerns into measurable release criteria.

### Release operator
Reviews the final result and evidence. Their goal is to understand whether the candidate should pass, require review, or be blocked—and why.

### Security, governance, or risk reviewer
Defines what tools and data each agent can access, which operations require confirmation, and which violations must block release.

### QA and verification engineer
Uses golden workflows and deterministic replay to confirm behavior across releases. Their goal is to ensure the UI, simulation engine, calculations, and gate decisions remain correct.

### Product or operations leader
Uses the result summary to understand reliability-versus-cost tradeoffs, projected production impact, and unresolved release risks.

## 3. Core concepts in plain language

### Persona agent
A simulated human user. It provides the request, asks follow-up questions, behaves according to a persona, and decides whether the outcome satisfies the scenario.

### Assistant agent
The candidate being tested. It may respond directly, call tools, delegate to sub-agents, or route between departments.

### Workflow
The allowed interaction pattern. The MVP has four: linear, depth-one hierarchy, depth-two department routing, and transactional MCP.

### MCP simulator
A controlled stand-in for tools and external dependencies. It can return successes, delays, timeouts, malformed data, authorization failures, business rejections, or ambiguous outcomes according to configured probabilities.

### Harness
The reliability wrapper around an agent. It validates input/output, classifies failures, retries only safe cases, applies recovery, enforces limits, and records what happened.

### Experiment
An immutable, versioned combination of workflow, agents, tools, failure profiles, harnesses, run settings, and gates.

### Iteration
One complete execution of an experiment scenario.

### Trajectory
The chronological operational history of an iteration: messages, delegation, tool calls, validation, retries, recovery, and final outcome.

### Baseline and candidate
The baseline is the approved version. The candidate is the proposed change. Results compare them directly.

### Evaluation gate
A threshold such as “terminal failures must be no more than 0.5%.” Gates have warning, review, or blocking severity.

## 4. Running the included MVP

Open:

```text
app/agent_simulation_control_plane_mvp.html
```

The application is self-contained. It stores temporary state in the browser and uses deterministic local simulation.

The bottom status bar represents future service boundaries. It does not mean that Kafka, Flink, or production models are actually connected.

## 5. Orientation to the UI

### Overview
Use this to see recent experiments, reliability trends, cost changes, blocked candidates, and common failures.

### Experiments
Use this to create, clone, run, compare, or archive experiment configurations.

### Runs
Use this to view current and past executions.

### Results
Use this to understand final release decisions and candidate-versus-baseline changes.

### Trajectories
Use this to investigate individual executions, especially failures, recoveries, anomalies, and expensive or slow cases.

### Configuration registries
Use Workflows, Agents, Personas, MCP Simulators, Harnesses, Policies, and Evaluation Gates as reusable versioned building blocks.

## 6. Golden workflow 1 — Purchase ambiguity and safe recovery

### Why this is the primary golden workflow

Transactional ambiguity is a concrete example of why ordinary retries are unsafe. A purchase request may complete in the payment service even when the response times out. Retrying the purchase without an idempotency key can create a duplicate transaction.

### Initial configuration

- Workflow: Transactional MCP.
- Persona: Retail Customer.
- Objective: Purchase two tickets for Friday.
- Assistant: Purchase Agent candidate.
- Tools: `check_inventory`, `make_purchase`, `transaction_status`.
- Failure profile: `make_purchase` can time out or return ambiguous completion.
- Harness: Basic Retry.
- Gate: Terminal failure ≤ 0.5%; policy violations = 0.

### Operator steps

1. From Overview, open **Purchase Agent Reliability**.
2. Review the workflow and failure distribution.
3. Run the experiment.
4. Watch live events until a purchase timeout occurs.
5. Complete the run.
6. Observe that the candidate is blocked.
7. Open a failed trajectory.
8. Confirm that `make_purchase` was called again without safe idempotency or status verification.

### Expected finding

The result is blocked due to duplicate-transaction risk or excessive terminal failures. The trajectory explains the exact unsafe sequence.

### Apply the fix

1. Select **Apply recommended fix** or clone the experiment.
2. Change the harness to **Transaction Safety**.
3. Configure timeout/ambiguous completion recovery to call `transaction_status`.
4. Require reuse of the same idempotency key when a retry is safe.
5. Rerun with the same experiment size.

### Expected improved outcome

Blocking gates pass. Retry or cost may remain at warning level, demonstrating that safety improved while cost/latency tradeoffs are still visible.

### What this verifies

- Deterministic failure injection.
- Transactional ambiguity classification.
- Idempotency and verification recovery.
- Candidate-versus-baseline metrics.
- Explainable release gates.
- Trace-level root-cause analysis.

## 7. Golden workflow 2 — Reliable linear support

### Scenario

A user asks a factual support question. The assistant retrieves the relevant document and returns a structured, cited response.

### Configuration

- Workflow: Linear Chat.
- Persona: Technical support requester.
- Tools: `search_knowledge_base`, `read_customer_profile` where permitted.
- Harness: Strict Structured Output + Evidence Grounding.
- Main failure modes: malformed response, missing citation, retrieval timeout.

### Expected outcome

Passed. Malformed outputs are repaired by normalization or bounded retry. Missing citations trigger one retrieval retry. Policy-denied data remains inaccessible.

### What to inspect

- Validation success.
- Citation recovery.
- Cost per successful response.
- One recovered trajectory.
- One policy-denied trajectory that safely refuses.

## 8. Golden workflow 3 — Hierarchical research overload

### Scenario

A primary agent delegates a research request to multiple sub-agents and aggregates the result.

### Configuration

- Workflow: Hierarchical Research.
- Sub-agents: Product, Policy, and Pricing.
- Parallel execution.
- Failure modes: sub-agent timeout, duplicate research, partial source unavailability.
- Gates: answer quality, P95 latency, cost increase, maximum tool/sub-agent calls.

### Expected outcome

Manual review. Answer quality is high, but cost or long-tail latency exceeds a review threshold.

### What this teaches

A candidate can be functionally correct and still require review because orchestration overhead makes it too expensive or slow.

## 9. Golden workflow 4 — Department routing and context loss

### Scenario

A user request crosses customer support, billing, and operations. A routing agent transfers the case to department agents and specialists.

### Failure to simulate

The account identifier or user confirmation is lost during handoff, causing a specialist to use incomplete or wrong context.

### Expected outcome

Blocked if the system returns incorrect account data or violates a tool-access policy.

### Corrective changes

- Add a typed handoff envelope.
- Validate required context at every boundary.
- Restrict specialist tools to the resolved customer scope.
- Refuse or escalate when context is incomplete.

### What this verifies

- Delegation depth two.
- Context propagation.
- Tool policy inheritance.
- Handoff validation.
- Security-sensitive blocking gates.

## 10. Reading the live run page

### Progress
Completed / planned iterations. A run may be paused or stopped without deleting completed evidence.

### Successful versus recovered
A recovered result is successful only because the harness intervened. Keep it separate from first-attempt success because high recovery dependence may increase cost and hide fragility.

### Terminal failure
The workflow could not safely complete after bounded recovery.

### Provisional gates
These are estimates during the run. They become final only after all iterations and aggregation complete.

### Worker status
Represents horizontal execution. A retrying worker is not necessarily unhealthy; repeated infrastructure errors across workers are.

### Event stream
Shows important operational events such as timeout, recovery, policy denial, completion, or anomaly detection.

## 11. Reading results

### Success rate
How often the user objective was safely completed.

### Validation success
How often the response satisfied required structure, schema, evidence, and policy checks.

### Terminal error rate
How often the workflow failed after recovery was exhausted or prohibited.

### Recovery success rate
Of the recoverable failures encountered, how many were successfully corrected.

### Retry rate
How often retries were used. High retry rate can increase cost and latency even when final success is high.

### Cost per successful iteration
More useful than mean cost when failures are common, because it measures the cost of useful outcomes.

### P95 latency
The latency experienced by the slowest 5% of iterations. Agent systems often look healthy on average while having unacceptable tails.

### Policy violations
Typically blocking. Examples include unauthorized tool access, duplicate transaction risk, cross-tenant access, or sensitive data in telemetry.

## 12. Release-decision interpretation

### Passed
All blocking and review gates passed.

### Passed with warnings
Safe to proceed under the configured policy, but warning metrics require observation.

### Manual review
No blocking failure, but a cost, latency, anomaly, or business threshold needs human judgment.

### Blocked
At least one safety, reliability, or policy gate failed. The operator should inspect related trajectories before changing the candidate.

## 13. Recommended operator investigation sequence

1. Read the plain-language decision.
2. Open the failed or warning gate.
3. Review actual value, threshold, severity, and sample size.
4. Filter trajectories related to the gate.
5. Inspect representative and worst-case traces.
6. Identify whether the root cause is prompt/model, tool/dependency, policy, workflow, or harness.
7. Clone the experiment.
8. Make one bounded change.
9. Rerun using the same seed set for comparison.
10. Confirm no new anomaly or cost/latency regression was introduced.

## 14. QA use of the tutorial

QA agents should implement the golden workflows as deterministic end-to-end tests. The purchase ambiguity workflow is the release-critical test because it proves that the platform can block an unsafe configuration, explain the cause, apply a recovery improvement, and produce a changed decision under comparable conditions.

## 15. Implementation-agent use of the tutorial

Implementation agents should treat each golden workflow as a vertical slice. Build the minimum services, contracts, data, and UI required to make one workflow real before generalizing abstractions. Preserve the existing operator journey even when internal components change.

## 16. Safety and representation

The MVP is a demonstration, not evidence that production-derived distributions, real MCP dependencies, Kafka/Flink/Druid, or automated rollback are already implemented. Production screens and status indicators must clearly identify simulated, assumed, imported, or learned data sources.
