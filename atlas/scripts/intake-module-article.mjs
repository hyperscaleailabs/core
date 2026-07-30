#!/usr/bin/env node
/**
 * Module article -> Atlas lab note.
 *
 * The project lifecycle (sdlc/LIFECYCLE.md) ends every project with an article
 * under `<module>/docs/articles/<date>-<project>/article.md`, and says that
 * publishing it triggers the Atlas update. This script is that trigger: it reads
 * a module article and writes the corresponding `src/content/lab/<date>-<project>.md`
 * entry, with provenance back to the article, the issue, and the PR.
 *
 * It is deliberately conservative:
 *   - it never invents prose. The lab note carries a lede plus the article's own
 *     section headings as a summary skeleton, and the writer fills it in;
 *   - it never overwrites an existing entry's body. Re-running on an existing
 *     entry refreshes only the frontmatter fields it owns (`updated`,
 *     `articlePath`, `issue`, `pr`), so a hand-edited note survives;
 *   - it reports what it did and exits non-zero on anything it cannot resolve,
 *     because a silent partial intake is the failure mode the whole lifecycle
 *     is built to avoid.
 *
 * Usage, from `atlas/`:
 *   node scripts/intake-module-article.mjs ../models/docs/articles/2026-07-28-models-integration/article.md \
 *        --issue 7 --pr 8 [--level advanced] [--tier process] [--check]
 *
 * `--check` writes nothing and exits non-zero when the entry is missing or its
 * `articlePath` no longer resolves. The atlas CI workflow runs it over every
 * module article in the repository.
 */
import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, dirname, basename, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const MODULE_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const REPO_ROOT = join(MODULE_ROOT, '..');
const LAB_DIR = join(MODULE_ROOT, 'src', 'content', 'lab');

const TIERS = [
  'process',
  'smoke',
  'simulation-demo',
  'simulation-benchmark',
  'distributed-benchmark',
  'hardware-in-the-loop',
  'physical',
];

function fail(message) {
  console.error(`intake: ${message}`);
  process.exit(1);
}

function parseArgs(argv) {
  const opts = { paths: [], check: false, level: 'advanced', tier: 'process' };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--check') opts.check = true;
    else if (a === '--issue') opts.issue = Number(argv[++i]);
    else if (a === '--pr') opts.pr = Number(argv[++i]);
    else if (a === '--level') opts.level = argv[++i];
    else if (a === '--tier') opts.tier = argv[++i];
    else if (a === '--all') opts.all = true;
    else if (a.startsWith('--')) fail(`unknown option ${a}`);
    else opts.paths.push(a);
  }
  if (!TIERS.includes(opts.tier)) fail(`--tier must be one of: ${TIERS.join(', ')}`);
  return opts;
}

/** Minimal frontmatter split. Body is everything after the closing fence. */
function splitFrontmatter(raw) {
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return { fm: null, body: raw };
  return { fm: m[1], body: raw.slice(m[0].length) };
}

function fmValue(fm, key) {
  if (!fm) return undefined;
  const m = fm.match(new RegExp(`^${key}:\\s*(.*)$`, 'm'));
  if (!m) return undefined;
  return m[1].trim().replace(/^["']|["']$/g, '');
}

/** `<module>/docs/articles/<date>-<project>/article.md` -> its parts. */
function describeArticle(articleAbs) {
  const rel = relative(REPO_ROOT, articleAbs);
  const parts = rel.split('/');
  const i = parts.indexOf('articles');
  if (basename(articleAbs) !== 'article.md' || i < 1 || !parts[i + 1]) {
    fail(
      `${rel} is not a module article; expected <module>/docs/articles/<date>-<project>/article.md`,
    );
  }
  const dirName = parts[i + 1];
  const dm = dirName.match(/^(\d{4}-\d{2}-\d{2})-(.+)$/);
  if (!dm) fail(`article directory ${dirName} must be named <YYYY-MM-DD>-<project>`);
  return { rel, module: parts[0], date: dm[1], project: dm[2], slug: dirName };
}

/**
 * First markdown H1, and the first paragraph under it that is prose.
 *
 * Module articles open with an audience-and-trail block ("Audience: Architect,
 * PM. Project trail: ..."). It is metadata, not a lede: taking it as the site
 * description produced an entry that described the paperwork instead of the
 * work, so paragraphs that begin with a known metadata label are skipped.
 */
const METADATA_PARAGRAPH = /^(Audience|Project trail|Produced by|Status|Evidence tier):/i;

function readTitleAndLede(body) {
  const lines = body.split(/\r?\n/);
  let title = '';
  let paragraph = [];
  for (let i = 0; i < lines.length; i++) {
    if (!title) {
      const h1 = lines[i].match(/^#\s+(.*)$/);
      if (h1) title = h1[1].trim();
      continue;
    }
    if (lines[i].startsWith('#')) {
      if (paragraph.length) break;
      continue;
    }
    if (lines[i].trim() === '') {
      if (paragraph.length && !METADATA_PARAGRAPH.test(paragraph[0])) break;
      paragraph = [];
      continue;
    }
    paragraph.push(lines[i].trim());
  }
  const lede = METADATA_PARAGRAPH.test(paragraph[0] ?? '') ? '' : paragraph.join(' ');
  return { title, lede };
}

function readHeadings(body) {
  return body
    .split(/\r?\n/)
    .map((l) => l.match(/^##\s+(.*)$/))
    .filter(Boolean)
    .map((m) => m[1].trim());
}

/** One-line description, hard-capped to the schema's 320 characters. */
function toDescription(lede, title) {
  const text = (lede || title).replace(/\[([^\]]+)\]\([^)]*\)/g, '$1').replace(/[*`_]/g, '');
  return text.length <= 316 ? text : `${text.slice(0, 316).replace(/\s+\S*$/, '')} ...`;
}

function renderFrontmatter(fields) {
  const lines = ['---'];
  for (const [k, v] of Object.entries(fields)) {
    if (v === undefined || v === null) continue;
    if (Array.isArray(v)) lines.push(`${k}: [${v.join(', ')}]`);
    else if (typeof v === 'number' || typeof v === 'boolean') lines.push(`${k}: ${v}`);
    else if (/^\d{4}-\d{2}-\d{2}$/.test(v)) lines.push(`${k}: ${v}`);
    else lines.push(`${k}: ${JSON.stringify(v)}`);
  }
  lines.push('sources:');
  lines.push(`  - title: ${JSON.stringify(fields.__sourceTitle)}`);
  lines.push(`    url: ${JSON.stringify(fields.__sourceUrl)}`);
  lines.push('    publisher: "hsailabs"');
  lines.push('    license: "Apache-2.0"');
  lines.push('---');
  return lines.filter((l) => !l.startsWith('__')).join('\n');
}

async function intakeOne(articleAbs, opts) {
  const info = describeArticle(articleAbs);
  const raw = await readFile(articleAbs, 'utf-8');
  const { fm, body } = splitFrontmatter(raw);
  const { title, lede } = readTitleAndLede(fm === null ? raw : body);
  if (!title) fail(`${info.rel} has no level-1 heading to take a title from`);

  const target = join(LAB_DIR, `${info.slug}.md`);
  const existing = existsSync(target) ? await readFile(target, 'utf-8') : null;

  if (opts.check) {
    if (!existing) {
      console.error(
        `MISSING LAB NOTE: ${info.rel} has no Atlas entry at ` +
          `atlas/src/content/lab/${info.slug}.md (run scripts/intake-module-article.mjs)`,
      );
      return false;
    }
    const declared = fmValue(splitFrontmatter(existing).fm, 'articlePath');
    if (!declared || !existsSync(join(REPO_ROOT, declared))) {
      console.error(
        `BROKEN PROVENANCE: atlas/src/content/lab/${info.slug}.md declares ` +
          `articlePath ${declared ?? '(none)'}, which does not resolve`,
      );
      return false;
    }
    console.log(`ok  ${info.rel} -> atlas/src/content/lab/${info.slug}.md`);
    return true;
  }

  const today = new Date().toISOString().slice(0, 10);
  const frontmatter = renderFrontmatter({
    title,
    description: toDescription(lede, title),
    level: opts.level,
    updated: today,
    created: existing ? fmValue(splitFrontmatter(existing).fm, 'created') || info.date : info.date,
    tags: ['lab-notes', info.module, info.project],
    module: info.module,
    project: info.project,
    articlePath: info.rel,
    issue: opts.issue,
    pr: opts.pr,
    evidenceTier: opts.tier,
    draft: !existing,
    aiGenerated: false,
    license: 'CC-BY-4.0',
    __sourceTitle: `${title} (module article)`,
    __sourceUrl: `https://github.com/hyperscaleailabs/core/blob/main/${info.rel}`,
  });

  if (existing) {
    const kept = splitFrontmatter(existing).body;
    await writeFile(target, `${frontmatter}\n${kept}`, 'utf-8');
    console.log(`refreshed frontmatter: src/content/lab/${info.slug}.md (body kept)`);
    return true;
  }

  const headings = readHeadings(body);
  const skeleton = [
    '',
    `> Field notes from the \`${info.module}\` module. Full article, evidence, and`,
    `> review trail in [the module article](https://github.com/hyperscaleailabs/core/blob/main/${info.rel}).`,
    '',
    lede,
    '',
    ...headings.flatMap((h) => [`## ${h}`, '', 'TODO: summarize for an outside reader.', '']),
  ].join('\n');

  await mkdir(LAB_DIR, { recursive: true });
  await writeFile(target, `${frontmatter}\n${skeleton}`, 'utf-8');
  console.log(`drafted: src/content/lab/${info.slug}.md (draft: true - write it, then publish)`);
  return true;
}

/** Every `<module>/docs/articles/<date>-<project>/article.md` in the repository. */
async function findModuleArticles() {
  const found = [];
  for (const moduleDir of await readdir(REPO_ROOT, { withFileTypes: true })) {
    if (!moduleDir.isDirectory() || moduleDir.name.startsWith('.')) continue;
    const articles = join(REPO_ROOT, moduleDir.name, 'docs', 'articles');
    if (!existsSync(articles)) continue;
    for (const entry of await readdir(articles, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const article = join(articles, entry.name, 'article.md');
      if (existsSync(article)) found.push(article);
    }
  }
  return found.sort();
}

const opts = parseArgs(process.argv.slice(2));
const targets = opts.all || opts.paths.length === 0
  ? await findModuleArticles()
  : opts.paths.map((p) => resolve(p));

if (targets.length === 0) fail('no module articles found');

let ok = true;
for (const t of targets) {
  if (!existsSync(t)) fail(`no such article: ${t}`);
  ok = (await intakeOne(t, opts)) && ok;
}

if (!ok) {
  console.error('');
  console.error(
    'Every module article needs an Atlas lab note - that edge is what makes the',
  );
  console.error('lifecycle stage real. See atlas/README.md#from-module-article-to-atlas-entry.');
  process.exit(1);
}
