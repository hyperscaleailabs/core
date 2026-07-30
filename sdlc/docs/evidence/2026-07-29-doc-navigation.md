# Evidence: deployment documentation navigation

Project: [issue #16](https://github.com/hyperscaleailabs/core/issues/16) and
[pull request #17](https://github.com/hyperscaleailabs/core/pull/17).
Collected 2026-07-29 from the project branch.

Evidence tier: **process**. This record supports documentation navigation and
policy behavior only.

## Baseline reproduction

The repository link check was green even though three deployment table cells
contained four unlinked module references:

```text
$ bash tools/policy/check_links.sh
markdown links OK

$ inspect README.md#target-deployment Backed by cells
UNLINKED BACKED BY: Meet -> `meet/`
UNLINKED BACKED BY: APIs -> `agents/`, `models/`
UNLINKED BACKED BY: D-twins -> `dtwins/`
```

The declared links were valid. The defect was the absence of links, which the
existing checker had no assertion for.

## Guard exercised

The navigation assertion was added before fixing the table. It failed against
the reproduced state:

```text
MISSING NAVIGATION LINK: README.md deployment row Meet has unlinked Backed by cell: `meet/`
MISSING NAVIGATION LINK: README.md deployment row APIs has unlinked Backed by cell: `agents/`, `models/`
MISSING NAVIGATION LINK: README.md deployment row D-twins has unlinked Backed by cell: `dtwins/`
guard exit: 1
```

After linking all four module references:

```text
$ bash tools/policy/check_links.sh
markdown links OK
```

The existing target and anchor checks validate the four newly declared links.
The new assertion ensures the table cannot silently return to plain text.

## New-document scan exercised

The first local pass after adding the project article returned
`markdown links OK` even though the article contained a broken relative link.
The article was untracked, and the checker enumerated only tracked files.

After changing the scan to include tracked and non-ignored untracked Markdown,
the same command exposed the defect:

```text
BROKEN LINK: sdlc/docs/articles/2026-07-29-doc-navigation/article.md -> ../../../../LIFECYCLE.md#stages
untracked scan exit: 1
```

The relative path was corrected and the final scan passed. Ignored dependency
documentation remains excluded through Git's standard ignore rules.

## Regression review

| Check | Result |
|-------|--------|
| Root documentation graph | All tracked documentation nodes intended for the graph are reachable from `README.md` |
| Existing Markdown targets and anchors | clean |
| Atlas static build | 49 pages, 36 indexed documents |
| Atlas internal link crawl | 1,625 local links checked, 0 broken routes or fragments |
| Browser verification | Home, Lab index, and article at desktop and mobile widths: 6 HTTP 200 responses, no console errors, overlays, or horizontal overflow |
| Navigation guard failing direction | 3 unlinked cells reported, exit 1 |
| Navigation guard passing direction | clean |
| Untracked-document failing direction | broken article link reported, exit 1 |
| Final tracked plus untracked scan | clean |

## Scope

The content change is limited to the `Backed by` cells in
`README.md#target-deployment`. The policy change is limited to that table's
navigation contract. No external links, strategic claims, module behavior, or
deployment configuration changed.
