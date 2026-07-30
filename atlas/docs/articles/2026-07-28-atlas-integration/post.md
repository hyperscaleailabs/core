# Post variant (LinkedIn format assumed)

Audience: CTO / Architect / PM. Source of truth:
[article.md](article.md); post text below.

<!-- Paste everything below this line -->

---

Our development lifecycle said every project ends in a published article.
Nothing checked that it did. Two finished projects were sitting unpublished and
no build, no review, and no dashboard had noticed.

We integrated our public technical site into the monorepo this week and used the
move to close that gap:

- A project's article now has to become a published entry, or CI fails - and the
  check runs on the PR that creates the debt, not on some later change to the
  site.
- The published entry carries the module, the issue, the PR, the path back to
  the source article, and the **evidence tier** of the claim it summarizes.
  Simulation stays simulation on the way out to the public page. That is the
  place where the temptation to round up is strongest.
- The repository graph now has an exit node. Agents enter at the root README and
  leave through the publication surface.

Four defects showed up on the way: every
outbound link in the migrated site still pointed at the repository it had left;
a new content section registered in three of four places reported the wrong
article count on the home page - nothing looked broken, which is worse than a
missing page; and our new CI guards had nowhere to run before CI, so their first
execution was on a hosted runner, where they promptly failed on themselves.
The acceptance review then found high-severity production dependency advisories
that the build did not check.

All four are now guarded in commands a person can run before pushing. A check
you cannot run locally is a check that debugs itself in front of your reviewer.

The repo is public and the trail - issue, PR, evidence, article, published entry
- is inspectable end to end.

#AIagents #SoftwareArchitecture #DevOps #CI #TechnicalWriting
