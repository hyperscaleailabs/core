# Strategic level

Cadence: **1 / 3 / 6-12 months**, with a **monthly templated research
iteration**. The strategic level owns the **axis** - the standing answer to why
(mission), what (direction and horizons), and how (method and stack) - and keeps
it aligned with what the lower levels actually learn.

It defines direction; it does not decide implementation. Long form and research
evidence live in [docs/strategic/](../docs/strategic/); the compressed operative
form is [AXIS.md](../AXIS.md).

## Templated iterative research

Strategic research is **templated** and iterates **monthly**. Its subject is the
platform and the apps that use it. The initial template is extracted from the
existing strategic documents (the `research/`, `prd`, `ref-architecture`,
`pland`, `handoff` structure of the [docs/strategic/](../docs/strategic/)
packages) and is improved with every iteration.

Each iteration produces the **strategic context**: the current directional
reading the [tactical level](TACTICAL.md) carries, together with the template
itself, into its weekly review.

## Standing artifacts

| Artifact | Role |
|----------|------|
| [MISSION.md](../MISSION.md) | Why - changes rarely |
| [AXIS.md](../AXIS.md) | Compressed direction and effort weighting (short 80 / mid 15 / long 5) |
| [docs/strategic/DIRECTION.md](../docs/strategic/DIRECTION.md) | Horizons with research evidence; realignment log |
| [docs/strategic/](../docs/strategic/) packages | Scoped initiatives handed to the [tactical level](TACTICAL.md) |

## Checkpoints

| Checkpoint | Period | Activity |
|------------|--------|----------|
| **Alignment check** | 1 month | Run the monthly [templated research iteration](#templated-iterative-research) and refresh the strategic context. Read the month's architecture review and weekly digests against AXIS.md; name drift between what was built and the declared horizons; push corrections to the tactical backlog. Direction is not rewritten here. |
| **Horizon review** | 3 months | Re-examine horizon contents and the effort weighting mid-cycle; re-scope open strategic packages against what the quarter actually demanded. |
| **Realignment** | 6-12 months | Full research cycle per [DIRECTION.md](../docs/strategic/DIRECTION.md#realignment-cycle): fresh market research, horizons adjusted or retired, AXIS.md regenerated, packages opened or closed, log entry recorded. |

A checkpoint that changes nothing is a finding worth recording, not a skipped step.

## Integration

- **Down**: every tactical epic traces to a strategic package and a horizon. Work
  that cannot be traced is not started.
- **Up**: the strategic level never reads raw PRs. It consumes the aggregate -
  daily whitepapers, weekly digests, the monthly architecture review, and the
  [lessons](docs/lessons/) carried in project articles - so realignment is
  informed by what was actually built and learned, not by what was planned.
- If work repeatedly fights the axis, that is a signal to realign the axis, not to
  quietly ignore it.

## Status

First-iteration scaffolding, defined now. The axis and the 6-12 month realignment
cycle are operative
([realignment log](../docs/strategic/DIRECTION.md#realignment-log)); the 1 and 3
month checkpoints activate as the daily and tactical levels begin publishing.
