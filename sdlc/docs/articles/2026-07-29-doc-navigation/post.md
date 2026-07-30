# Post variant

Audience: CTO, Architect, PM. Source of truth:
[article.md](article.md).

Our broken-link check was green while the deployment table contained four
missing documentation links.

That was not a contradiction. The checker validated every declared edge. The
four required edges had never been declared.

We fixed the Meet, Agents, Models, and D-twins navigation paths, then added a
guard for the contract the table actually makes: every `Backed by` cell must
link to the component documentation.

The review also found that new untracked documents were invisible to the local
checker. It now scans tracked and non-ignored untracked Markdown, so a new file
cannot hide a broken link before staging.

The guard was run before the fix and named all three bad cells. After the fix,
the repository link check passed, all documentation remained reachable from the
root, and 1,625 internal links in the built publication site resolved.

The lesson is small and reusable: validating link targets is not the same as
validating navigation completeness.

#Documentation #DeveloperExperience #CI #SoftwareArchitecture
