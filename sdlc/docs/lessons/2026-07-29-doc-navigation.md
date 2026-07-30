# A checker cannot validate a link that does not exist

Project: [issue #16](https://github.com/hyperscaleailabs/core/issues/16).

## Correction

The root deployment table named Meet, Agents, Models, and D-twins in inline
code. The module names looked precise but were not navigable. The existing link
check passed because every link that did exist resolved.

The correction replaced those four plain-text references with links to the
module READMEs.

The review then exposed a second blind spot: the checker scanned only tracked
Markdown. A newly created article with a broken lifecycle link passed until the
scanner was changed to include non-ignored untracked files.

## Lesson

Target validation and navigation completeness are different contracts. A
broken-link checker answers whether declared edges resolve. It cannot answer
whether a required edge was omitted.

Navigation tables are interfaces. When a table column promises the component
behind a surface, every data cell in that column must provide the path to that
component's documentation.

## Codified

`tools/policy/check_links.sh` now requires every non-header `Backed by` cell in
`README.md#target-deployment` to contain a Markdown link. The ordinary link
checker then validates each target and anchor.

The assertion was exercised before the correction and named all three unlinked
cells with a nonzero exit. It passes after the four module links are present.

The same script now enumerates tracked and non-ignored untracked Markdown
through Git. This keeps dependency documentation excluded while ensuring a new
document is checked before it is staged. The review's broken article link was
used as the failing-direction test.

Evidence:
[deployment documentation navigation](../evidence/2026-07-29-doc-navigation.md).
