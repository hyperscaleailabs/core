---
title: "Reflection: Agents That Check Their Own Work"
description: "The pattern where an agent critiques and revises its output before finishing - how it works, when it pays off, and when it just burns tokens."
level: intermediate
readingTime: 6
problem: "First-pass agent output is often almost-right; how do we catch and fix errors before returning it?"
alsoKnownAs: [self-critique, self-refine, evaluator-optimizer]
updated: 2026-06-30
tags: [reflection, self-critique, quality, evaluator-optimizer]
sources:
  - title: "Building Effective Agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
    publisher: "Anthropic"
    accessed: "2026-06-30"
---

**Reflection** adds a critic step to the loop: the agent produces a candidate,
evaluates it against criteria, and revises - iterating until it passes or a budget
runs out. It's one of the highest-leverage patterns because it converts a model's
ability to *recognize* errors (often strong) into corrected *output* (the thing
you actually ship).

## The shape

In *Building Effective Agents*, the **evaluator–optimizer** workflow captures this
cleanly: one LLM call generates, another evaluates and gives feedback, and the
loop repeats.

```text
   generate ─▶ candidate ─▶ evaluate ──pass──▶ done
                   ▲                 │
                   └──── revise ◀─fail┘  (until pass or budget)
```

The evaluator can be:

- **The same model** with a critic prompt ("find errors in the above against
  these criteria").
- **A different/cheaper model** specialized as a judge.
- **A programmatic check** - tests, a compiler, a linter, a schema validator.
  When a ground-truth check exists, prefer it; it's cheaper and more reliable
  than an LLM judge.

## When it pays off

- **There's a clear success criterion** the evaluator can apply (does the code
  compile? does the JSON validate? does the answer cite a source?).
- **Errors are recognizable** even when generation is imperfect - writing, code,
  structured extraction.
- **The cost of a wrong answer** exceeds the cost of extra iterations.

## When to skip it

- **No meaningful evaluation signal** - reflection without a real criterion just
  produces confident re-assertions and doubles cost.
- **Latency-critical paths** - each cycle is another round trip.
- **The model already one-shots the task** - measure before adding loops.

## Design tips

- **Bound it.** Cap iterations; diminishing returns arrive fast.
- **Prefer objective evaluators.** A compiler or test suite beats "grade
  yourself." Reserve LLM-as-judge for subjective quality.
- **Make feedback specific.** "Line 12 dereferences a possibly-null value" drives
  a fix; "improve the code" drives churn.
- **Log the critique.** The evaluator's feedback is gold for
  [evaluation](/production/evaluation) and debugging.

## Relationship to other patterns

Reflection composes with [tool use](/patterns/tool-use) (the evaluator can *run*
the code it's judging) and with [planning](/patterns/planning) (reflect on the
plan, not just the output). At the multi-agent level, a dedicated "reviewer"
agent is reflection expressed as [orchestration](/patterns/multi-agent-orchestration).

## Next

- [Planning](/patterns/planning) - decide the steps before executing them.
- [Evaluation](/production/evaluation) - turn ad-hoc critique into measurement.
