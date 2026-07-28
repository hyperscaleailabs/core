---
name: atlas-changelog-post
description: Review what shipped in the Atlas corpus since the last announcement, write the change summary as a module article, and draft the ready-to-paste social post beside it. Use when asked to announce recent updates, summarize what changed on the site, or draft a changelog post.
---

# atlas-changelog-post

Turn recent Atlas activity into the two artifacts this repository already has a
place for: an `article.md` (Architect and PM audiences) and a platform-neutral
`post.md`, under
`atlas/docs/articles/<YYYY-MM-DD>-<slug>/`. That is the same shape every project
produces at the RESEARCHER/PUBLISHER stage
([sdlc/LIFECYCLE.md](../../../sdlc/LIFECYCLE.md#stages)) - the skill this was
adapted from invented a separate `marketing/` directory, which this repository
does not need and does not have.

The post is written for a human to paste; this skill never posts anywhere. The
change ships through the normal cycle via `pr-flow`: Architect LGTM merges, and
merging is what publishes.

## Inputs

Optional: a change range or theme. With none, default to everything on `main`
since the last announcement:

1. If `atlas/docs/articles/` already has dated entries, use the newest as the
   lower bound: `git log --since=<that date> -- atlas/`.
2. Else use the latest tag.
3. Else judge the last release-worthy boundary from `git log --oneline -20`.

## Procedure

### 1. Frame and branch
`pr-flow` step 1 and 2. Horizon: short. This is an `atlas`-bounded PR.

### 2. Review what actually changed
Focus on reader-visible change, not churn:

```bash
git log --oneline --stat <range> -- atlas/
git diff --stat <range> -- atlas/
```

Pay attention to new and updated articles under `atlas/src/content/**` (title,
collection, what topic it adds), new frameworks cataloged, new Lab Notes
entries, and anything that moves the counts on the home page. Open the changed
files when a commit message is thin: describe the change, not the commit text.
Verify every title and slug so the links in the post are real.

### 3. Write `article.md`
`atlas/docs/articles/<date>-<slug>/article.md`, factual and engineer-facing:
what shipped, what it covers, what changed about the site's scope, and the
counts before and after. Use root-relative site paths (`/frameworks/langgraph`)
so links resolve on the deployed domain.

### 4. Write `post.md`
Same directory. Final text, not a template: a concrete hook (what is new, not
"excited to share"), three to five lines naming the actual content and its value
to someone building agents, one link, three to six hashtags, roughly 90-200
words. First person, builder to builder. **Claim only what shipped** - the
numbers come from the article, and the article's numbers come from the diff.

Mark where the pasteable copy starts:
`<!-- Paste everything below this line -->`.

### 5. Take it through the intake
An article in a module needs its Lab Notes entry, and this one is no exception:

```bash
cd atlas
node scripts/intake-module-article.mjs docs/articles/<date>-<slug>/article.md --issue <n> --pr <n>
make intake-check
```

Then write the entry's body for an outside reader and set `draft: false`.

### 6. Verify and open the PR
From `atlas/`: `make verify`, then `pr-flow` step 4 and `pr-verify`.

### 7. Report
The PR link, the two file paths, and **the full post text inline in the reply**
so it can be copied without opening a file. Say explicitly that nothing was
posted anywhere and that merging the PR is what publishes the article.
