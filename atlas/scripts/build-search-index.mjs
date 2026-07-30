#!/usr/bin/env node
/**
 * Build a lightweight search index (public/search-index.json) from the Markdown
 * content collections. Mirrors what pipeline/ingest.py produces, so the index
 * can be rebuilt with either toolchain (`npm run index`).
 *
 * Intentionally dependency-free: a minimal frontmatter reader, no YAML lib.
 */
import { readdir, readFile, mkdir, writeFile } from 'node:fs/promises';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const CONTENT = join(ROOT, 'src', 'content');
const OUT = join(ROOT, 'public', 'search-index.json');

async function walk(dir) {
  const out = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, entry.name);
    if (entry.isDirectory()) out.push(...(await walk(p)));
    else if (entry.name.endsWith('.md') || entry.name.endsWith('.mdx')) out.push(p);
  }
  return out;
}

/** Extract the frontmatter block and parse the few fields we index. */
function parseFrontmatter(raw) {
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return null;
  const fm = {};
  for (const line of m[1].split(/\r?\n/)) {
    const kv = line.match(/^(\w+):\s*(.*)$/);
    if (!kv) continue;
    const key = kv[1];
    let val = kv[2].trim();
    if (val.startsWith('[') && val.endsWith(']')) {
      fm[key] = val
        .slice(1, -1)
        .split(',')
        .map((s) => s.trim().replace(/^["']|["']$/g, ''))
        .filter(Boolean);
    } else if (val === 'true' || val === 'false') {
      fm[key] = val === 'true';
    } else {
      fm[key] = val.replace(/^["']|["']$/g, '');
    }
  }
  return fm;
}

const files = await walk(CONTENT);
const index = [];
for (const file of files) {
  const raw = await readFile(file, 'utf-8');
  const fm = parseFrontmatter(raw);
  if (!fm) continue;
  const section = basename(dirname(file));
  const slug = basename(file).replace(/\.mdx?$/, '');
  index.push({
    title: fm.title ?? slug,
    description: fm.description ?? '',
    section,
    level: fm.level ?? 'intermediate',
    tags: fm.tags ?? [],
    url: `/${section}/${slug}`,
    aiGenerated: fm.aiGenerated === true,
    draft: fm.draft === true,
  });
}

index.sort((a, b) => a.title.localeCompare(b.title));
await mkdir(dirname(OUT), { recursive: true });
await writeFile(OUT, JSON.stringify(index, null, 2) + '\n', 'utf-8');
console.log(`Search index written: ${index.length} documents → public/search-index.json`);
