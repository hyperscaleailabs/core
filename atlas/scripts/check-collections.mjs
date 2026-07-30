#!/usr/bin/env node
/**
 * Every content collection is registered exactly once, in both places.
 *
 * A collection lives in two files: its loader and schema in `src/content.config.ts`, and
 * its label, blurb, icon, and accent in `SECTION_META` (`src/lib/content.ts`).
 * The pages, the home-page grid, and the cross-section article list are all
 * derived from `SECTION_META`, so a collection missing from it validates,
 * builds, and renders nothing - and a `SECTION_META` entry with no collection
 * behind it produces a section page that throws at build time.
 *
 * Adding the `lab` collection is what surfaced this: the schema and the pages
 * were right, one list was not, and the only visible symptom was a wrong
 * article count on the home page.
 *
 * Run from `atlas/`: node scripts/check-collections.mjs
 */
import { readFile } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const MODULE_ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

const config = await readFile(join(MODULE_ROOT, 'src/content.config.ts'), 'utf-8');
const lib = await readFile(join(MODULE_ROOT, 'src/lib/content.ts'), 'utf-8');

/** Keys of the exported `collections` object literal. */
function collectionKeys(source) {
  const block = source.match(/export const collections = \{([\s\S]*?)\n\};/);
  if (!block) throw new Error('could not find the exported `collections` object in config.ts');
  return block[1]
    .split(',')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((entry) => {
      const named = entry.match(/^['"]([^'"]+)['"]\s*:/);
      return named ? named[1] : entry.split(':')[0].trim();
    })
    .filter(Boolean);
}

/** Top-level keys of the SECTION_META record. */
function sectionMetaKeys(source) {
  const block = source.match(/export const SECTION_META[^=]*= \{([\s\S]*?)\n\};/);
  if (!block) throw new Error('could not find SECTION_META in content.ts');
  return [...block[1].matchAll(/^ {2}('([^']+)'|([A-Za-z-]+)):\s*\{/gm)].map((m) => m[2] ?? m[3]);
}

const collections = collectionKeys(config).sort();
const meta = sectionMetaKeys(lib).sort();

const missingMeta = collections.filter((c) => !meta.includes(c));
const orphanMeta = meta.filter((m) => !collections.includes(m));

if (missingMeta.length || orphanMeta.length) {
  for (const c of missingMeta) {
    console.error(`MISSING SECTION_META: collection '${c}' has a schema but no entry in src/lib/content.ts`);
  }
  for (const m of orphanMeta) {
    console.error(`ORPHAN SECTION_META: '${m}' has an entry but no collection in src/content.config.ts`);
  }
  process.exit(1);
}

console.log(`collections registered consistently: ${collections.join(', ')}`);
