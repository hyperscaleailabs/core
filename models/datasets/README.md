# Datasets: domain packs

Note: large-scale, externally sourced datasets live in `goldens/` (HF-backed
golden dataset configs). Domain packs below are the complementary small,
hand-curated, in-repo suites focused on failure modes.

A domain pack is a pluggable bundle describing one application domain:
what typical inputs look like, and demonstrations of how models fail on them.
The benchmark runner discovers packs automatically; adding a domain means
adding a directory, no code changes.

## Structure

```
datasets/domain-packs/<domain>/
├── pack.yaml             # metadata (see pack.schema.json)
├── typical_inputs.jsonl  # representative inputs; also usable as training data
└── failure_modes.jsonl   # failure demonstrations with expected behavior
```

## typical_inputs.jsonl

One JSON object per line:

```json
{"id": "ecom-001", "modality": "text", "input": "...", "reference": "...", "tags": ["product-qa"]}
```

- `input`: the prompt / user input
- `reference`: a known-good response (used for training and judge-based scoring)
- `tags`: free-form task tags within the domain

## failure_modes.jsonl

One JSON object per line:

```json
{
  "id": "ecom-f001",
  "category": "hallucinated-specs",
  "modality": "text",
  "input": "...",
  "observed_failure": "what a model typically does wrong",
  "expected_behavior": "what a correct model must do",
  "check": {"type": "must_not_contain", "values": ["..."]}
}
```

`check` is a machine-verifiable assertion the benchmark runner executes:

| type | meaning |
|------|---------|
| `must_contain` | response must contain at least one of `values` (case-insensitive) |
| `must_not_contain` | response must contain none of `values` |
| `regex` | response must match `pattern` |

Failure categories are free-form but should be reused across packs where they
generalize (e.g. `hallucinated-specs`, `unit-confusion`, `refusal-miss`,
`asr-entity-error`).
