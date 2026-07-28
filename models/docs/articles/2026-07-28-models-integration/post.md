# Post variant (LinkedIn format assumed)

Audience: CTO / Architect / PM. Source of truth:
[article.md](article.md); post text below.

---

We just merged a small integration with an outsized lesson about AI-agent
engineering discipline.

Our model pipeline (golden datasets, LoRA fine-tuning, benchmarking,
vLLM/K3s serving) moved from a standalone repo into our open monorepo. The
interesting part is not the move - it is what "done" meant:

- The project started as a GitHub issue generated from a template whose
  alignment header is links only: mission, vision, strategic axis. No
  restated boilerplate - alignment is checked in outputs, not pasted into
  inputs.
- Every acceptance criterion mapped to a row in an evidence table: real CI
  runs, screenshots captured logged-out, transcripts with paths sanitized.
- Before acceptance, a compact regression re-ran the training smoke against
  the previously accepted baseline: 16 optimizer steps on a fixed golden
  slice, every loss metric within 0.005 of baseline. Cheap, fast, and it
  proves the pipeline survived the migration.
- A cleanup-and-refinement stage ran before merge: evidence relocated to the
  module it describes, drifted docs corrected, complexity removed rather
  than accumulated.

The whole flow is staged - Architect intent, MGMT documents, builder agents,
QA with regression, acceptance review on the issue trail, this article, final
review - and every stage pulls context by traversing the repository graph
from the root README, not by scanning the tree.

Boring discipline, compounding returns. The repo is public; the trail
(issue -> PR -> evidence -> article) is inspectable end to end.
