# Operator UI Mock Application Specification

**Product:** Agent Simulation Control Plane  
**Application type:** Desktop-first technical operator console  
**Document version:** 0.1  
**Purpose:** Define page layouts, reusable components, states, mock data, and interactions for a realistic clickable demonstration and later production implementation.

## 1. Product objective

The application demonstrates how an operator prepares, runs, observes, and evaluates a pre-production agent simulation:

```text
Select workflow
→ Configure persona and assistant agents
→ Attach tools, resources, skills, and policies
→ Configure probabilistic failures
→ Attach validation and recovery harnesses
→ Define evaluation gates
→ Run repeated simulations
→ Review reliability, latency, and cost
→ Inspect failed trajectories
→ Approve or block the candidate
```

## 2. Scope

Required behavior:

- Create/edit/clone/archive experiments.
- Select one of four predefined workflows.
- Configure one persona, one primary assistant, and sub-agents where relevant.
- Select tools/resources/skills/policies.
- Configure tool outcome probabilities and latency.
- Select or edit a harness.
- Define evaluation gates and cost estimates.
- Run a deterministic browser simulation with live progress.
- Compare candidate and baseline.
- Calculate a release decision.
- Inspect and replay trajectories.
- Export configuration and results JSON.

Mocked infrastructure may include LLM execution, MCP, Kafka, Flink, Druid, OpenTelemetry, CI/CD checks, and rollback. UI boundaries must make later replacement possible.

## 3. Primary demonstration

1. Open Overview.
2. Create or open the Transactional MCP experiment.
3. Configure a retail persona, purchasing assistant, purchase tools, assumed failure distributions, an unsafe/basic retry harness, and gates.
4. Run 1,000 accelerated iterations.
5. Show a blocked result caused by terminal error/duplicate transaction risk.
6. Inspect the failing trajectory.
7. Apply transaction-safety recovery: idempotency plus status verification.
8. Rerun and show a passing or warning-only result.

## 4. Information architecture

```text
Overview
Experiments
Runs
Results
Trajectories
Configuration
  Workflows
  Agents
  Personas
  MCP Simulators
  Harnesses
  Policies
  Evaluation Gates
Production Evidence
Settings
```

Priority pages: Overview, Experiments, Builder, Experiment Detail, Live Run, Results, Trajectory Inspector, and shared registries.

## 5. Route structure

```text
/overview
/experiments
/experiments/new
/experiments/:experimentId
/experiments/:experimentId/edit
/experiments/:experimentId/runs/:runId
/experiments/:experimentId/runs/:runId/results
/trajectories
/trajectories/:trajectoryId
/configuration/workflows
/configuration/agents
/configuration/personas
/configuration/tools
/configuration/harnesses
/configuration/policies
/configuration/gates
/production-evidence
/settings
```

## 6. Application shell

Desktop grid:

```text
┌──────────────────────────────────────────────────────────────┐
│ Product / Environment / Search / Notifications / Operator    │
├─────────────────┬────────────────────────────────────────────┤
│ Left navigation │ Breadcrumbs                                │
│                 ├────────────────────────────────────────────┤
│                 │ Main page                                  │
├─────────────────┴────────────────────────────────────────────┤
│ Optional integration and worker status bar                   │
└──────────────────────────────────────────────────────────────┘
```

Header: product name, environment selector, search, notifications, docs, profile. Sidebar: collapsible icon/label navigation with badges for active runs, blocked results, and anomalies. Optional status bar shows Simulation API, workers, telemetry queue, analytics freshness.

## 7. Interaction principles

The operator must always understand: what page is shown, whether the experiment is healthy, what failed, why it failed, and what action is available.

Status terms:

- Experiment: Draft, Ready, Running, Analyzing, Passed, Passed with warnings, Manual review, Blocked, Stopped, Failed.
- Iteration: Successful, Recovered, Partial, Failed, Cancelled.
- Gate: Pass, Warning, Review, Block.

Use text/icon plus semantic color. Technical tables support search, sort, filters, saved views, column selection, sticky headers, and detail drawers.

## 8. Overview dashboard

Header includes **New Experiment**.

Summary cards:

- Active runs.
- Iterations executed.
- Overall success rate.
- Projected cost change.
- Blocked candidates and pending reviews.

Charts:

- Baseline versus candidate reliability trend.
- Gate outcome distribution.
- Failure-mode frequency.
- Cost versus reliability scatter.

Recent experiments table columns: Experiment, Candidate, Workflow, Iterations, Success, Terminal error, Cost change, Gate status, Completed, Owner. Row actions: open, clone, rerun, export, archive.

## 9. Experiments list

Views: All, Active, Needs review, Blocked, Passed, Drafts, Archived.

Columns: Name, Version, Workflow, Candidate, Baseline, Last run, Iterations, Decision, Owner, Updated. Single click selects and opens compact details; name opens detail. Bulk operations: tag, archive, export, compare.

## 10. Experiment builder

Full-page eight-step wizard:

1. Workflow.
2. Persona.
3. Agents.
4. Tools and resources.
5. Failure profiles.
6. Harnesses.
7. Evaluation gates.
8. Review and run.

Behavior: autosave locally, inline validation, backward navigation, disabled future steps until required data is valid, evolving summary drawer, confirmation before resetting incompatible settings.

### Step 1 — Workflow

Cards:

- Linear Chat: depth 0, low complexity/cost.
- Hierarchical Research: depth 1, medium complexity/cost.
- Department Routing: depth 2, high complexity/cost.
- Transactional MCP: transaction risk, depth 0–1.

A selected card opens topology preview, recommended tools/harnesses, and an example modal.

### Step 2 — Persona

Two-column form and preview. Fields: name, role, description, objective, initial message, turns, style, persistence, ambiguity, cooperation, escalation, satisfaction conditions, model. Presets include Retail customer, Enterprise administrator, Technical requester, Procurement manager, Internal employee, Adversarial user, Custom.

### Step 3 — Agents

Primary fields: name/version/model/prompt/temperature/tokens/steps/skills/harness/policy/tool-call policy/fallback. Model cards show cost, latency, structured output, tool use, and acceleration.

Hierarchical workflows show an editable topology with up to five sub-agents and depth two. Operators assign tools/skills and sequential or parallel execution.

### Step 4 — Tools, resources, skills, policies

Tabs for Tools, Resources, Skills, Access Policies. Tool rows show name, MCP server, risk, transactional flag, version, and assigned agents. Access matrix exposes read/execute/transactional permissions and conditions. Invalid combinations show warnings.

### Step 5 — Failure profiles

Dependency list plus selected editor. Configure exclusive outcomes that must sum to 100%, latency distribution, source label (Assumed, Historical, Production learned, Modified), optional correlation rules, and a preview of expected failures per 1,000 runs.

### Step 6 — Harnesses

Presets: Strict structured output, Transaction safety, Tool reliability, Low latency, Low cost, Evidence-grounded, Custom.

Flow preview:

```text
Input validation → Context → Model → Parsing → Schema
→ Failure classification → Retry/Recovery/Fallback → Final validation
```

Retry table is keyed by failure class. Bounds include retries, steps, depth, tokens, cost, duration, and tool calls. Side panel estimates reliability/cost/latency impact.

### Step 7 — Evaluation gates

Editable table with metric, comparison, threshold, severity, enabled state, optional minimum sample size, scope, and description. Presets include Standard, Transaction-safe, Low-latency, Low-cost, and High-reliability.

### Step 8 — Review and run

Read-only configuration summary with edit links, expected and maximum cost, runtime/parallelism estimate, and preflight validation. Actions: Save Draft, Export Configuration, Run Experiment, preview-only Schedule Run, Cancel.

## 11. Experiment detail

Header: name, version, workflow, owner, Edit/Clone/Run/Compare/More.

Tabs: Summary, Configuration, Runs, Results, Audit History. Completed configurations display an immutable warning and require clone-to-edit. Audit events include creation, changes, runs, decisions, overrides, clones, and exports.

## 12. Live run monitor

Header contains status, start time, iteration progress, Pause/Resume/Stop.

Main areas:

- Progress bar and outcome counters.
- Throughput, workers, and cost.
- Outcome trend.
- Provisional gate table.
- Failure distribution.
- Worker status.
- Streaming event list.

Events open a detail drawer with iteration, trace, agent, tool, input/output, failure, recovery, and a link to the full trajectory.

Pause stops new iterations and lets active work finish. Stop confirms that completed data remains and queued iterations are cancelled. The mock completes 1,000 iterations in roughly 90–180 seconds.

## 13. Results

Decision header prominently shows Passed, Passed with warnings, Manual review, or Blocked, with gate counts and a plain-language explanation.

Actions: Compare, Review Failures, Clone and Modify, Export Report, optional Override, preview-only Send to Release Pipeline.

Tabs: Executive Summary, Reliability, Cost, Latency, Tools and Agents, Anomalies, Gate Details, Configuration.

Candidate/baseline table shows absolute values, percentage or percentage-point change, and gate status. Cost projection inputs update monthly and annual estimates. Reliability shows outcomes, failure classes, recovery, retries, confidence ranges, and failed trajectories. Latency shows histogram and stage/tool breakdown. Anomalies include unexpected sequences, new refusals, excessive depth, or behavior absent from baseline.

## 14. Trajectory list and inspector

Filters: Experiment, Run, Outcome, Agent, Tool, Failure, Recovery, Latency, Cost, Retry count, Anomaly, Gate relevance.

Inspector layout: trajectory tree on the left; selected event details on the right. Event types include persona, agent, delegation, tool, validation, classification, retry, recovery, fallback, policy, final response, persona evaluation, and telemetry.

Do not show hidden chain-of-thought. Show concise operational decision summaries.

Replay options:

- Same seed: same configured dependency outcomes.
- New seed: resampled outcomes.
- Optional Modify and replay: compare original and changed harness side by side.

## 15. Registry pages

Reusable registry layout for workflows, agents, personas, MCP tools, harnesses, policies, and gate sets. Each includes search, filters, version/status columns, and a selected-item detail drawer.

## 16. State transitions

Experiment:

```text
Draft → Ready → Running → Analyzing
Running ↔ Paused
Running → Stopping → Stopped
Analyzing → Passed / Warnings / Review / Blocked
Any pre-run state → Archived
Fatal execution → Failed
```

Iteration:

```text
Queued → Initializing → Persona → Agent → Tool/Sub-agent
→ Validation → Optional Recovery → Final Evaluation
→ Successful / Recovered / Partial / Failed
```

Gate: Not evaluated → Provisional → Final.

An optional manual override requires reason, approver, expiration, linked issue, and acknowledgement.

## 17. General UI behavior

- Tables support sorting, search, filters, pagination, column visibility, row selection, and export.
- Drawers are for quick detail; full pages are for editing, results, and trace inspection.
- Tooltips define metrics, gate calculations, distribution source, cost assumptions, and recovery classes.
- Unsaved changes prompt: Discard, Continue Editing, Save Draft.
- Destructive actions require confirmation.
- Filters/tabs are deep-linkable where practical.

## 18. Loading, empty, and error states

Use skeletons and progress labels. Provide clear empty states for no experiments, no failures, and no production distributions. Error states distinguish simulation unavailable, delayed telemetry, and incomplete analytics while preserving saved configuration and completed execution.

## 19. Sample data

Canonical examples are in `examples/`. The MVP should ship at least four presets:

1. Reliable linear support — Passed.
2. Hierarchical research overload — Manual review.
3. Department context loss — Blocked.
4. Purchase ambiguity — Blocked before fix, Passed with warnings after fix.

## 20. Mock simulation logic

Use a deterministic pseudo-random generator keyed by experiment seed and iteration index. Per iteration: create persona variant, select path, sample tool outcomes, apply policies, validate, classify, recover, calculate outcome/latency/cost, emit events, update metrics.

Cost model:

```text
persona + primary agent + sub-agents + tools + retries + recovery
```

Latency model:

```text
agents + tools + validation + retry/recovery
```

Harnesses deterministically change a subset of outcomes: schema validation reduces malformed terminal outputs; normalization repairs some failures; retries trade cost/latency for success; idempotency prevents duplicate transactions; status verification resolves ambiguity; bounds stop loops.

## 21. Recommended component inventory

Shell: ApplicationShell, SidebarNavigation, TopHeader, Breadcrumbs, EnvironmentSelector, SystemStatusBar.

Shared: StatusBadge, MetricCard, DeltaIndicator, Tooltip, EmptyState, ErrorBanner, Dialog, Drawer.

Builder: ExperimentStepper, WorkflowCard/Topology, PersonaEditor, AgentEditor, SubAgentTreeEditor, Tool/Resource/Skill selectors, AccessMatrix, FailureDistributionEditor, LatencyEditor, HarnessFlowEditor, RetryPolicyTable, GateEditor, CostEstimate, PreflightPanel.

Analytics: RunProgress, OutcomeCounter, LiveGateStatus, EventStream, WorkerTable, OutcomeChart, FailureChart, LatencyHistogram, CostProjection, BaselineComparison, GateScorecard, AnomalyCard.

Trajectory: TrajectoryTree, EventDetailPanel, TraceMetadata, ReplayDialog, TrajectoryComparison.

## 22. Responsive and accessibility requirements

Desktop target is 1,280px and above. Below 1,100px collapse navigation and stack panels; mobile may be read-only with a desktop recommendation.

All controls are keyboard accessible; focus is visible; labels are explicit; status does not rely on color; charts have summaries; dialogs trap focus; tables expose headers; contrast targets WCAG AA; reduced motion is honored.

## 23. Acceptance criteria

The UI is complete when an operator can navigate all primary sections, create a four-template experiment, configure personas/agents/sub-agents/tools/resources/policies/failures/harnesses/gates, review cost, run/pause/resume/stop, observe live events and provisional gates, receive a final decision, compare baseline/candidate, inspect and replay trajectories, clone and modify a completed experiment, observe a changed result, export JSON, and demonstrate immutability.

## 24. Recommended implementation boundary

```text
UI components
    ↓
Feature/page state
    ↓
Mock or real application API
    ↓
Deterministic simulation engine / orchestration service
    ↓
Fixture repository / production stores
```

The current HTML implements the browser-only form of this boundary. Production work should replace layers behind stable API and domain contracts rather than rewriting the operator journey.
