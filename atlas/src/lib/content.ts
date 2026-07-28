import { getCollection, type CollectionEntry, type CollectionKey } from 'astro:content';
import readingTime from 'reading-time';

export const SECTION_META: Record<string, { label: string; blurb: string; icon: string; accent: string }> = {
  foundations: {
    label: 'Foundations',
    blurb: 'From the pre-agentic era to the modern agent loop — the mental models.',
    icon: '◇',
    accent: 'var(--color-cyan)',
  },
  frameworks: {
    label: 'Frameworks',
    blurb: 'An Awesome-list-style catalog of SDKs, orchestrators, and protocols.',
    icon: '⬡',
    accent: 'var(--color-violet)',
  },
  patterns: {
    label: 'Patterns',
    blurb: 'Reflection, planning, multi-agent orchestration, swarms, context engineering.',
    icon: '⟲',
    accent: 'var(--color-amber)',
  },
  production: {
    label: 'Production',
    blurb: 'Harnesses, evaluation, observability, guardrails, cost — and failure modes.',
    icon: '▲',
    accent: 'var(--color-rose)',
  },
  comparisons: {
    label: 'Comparisons',
    blurb: 'Side-by-side framework matrices and failure-mode / tradeoff tables.',
    icon: '⇄',
    accent: 'var(--color-lime)',
  },
  'case-studies': {
    label: 'Case Studies',
    blurb: 'Real agentic systems in production, from public engineering blogs.',
    icon: '◈',
    accent: 'var(--color-cyan)',
  },
  'learning-paths': {
    label: 'Learning Paths',
    blurb: 'Curated tracks from beginner to architect.',
    icon: '↗',
    accent: 'var(--color-violet)',
  },
  news: {
    label: 'News',
    blurb: 'Aggregated developments across the agent ecosystem.',
    icon: '⊙',
    accent: 'var(--color-amber)',
  },
  lab: {
    label: 'Lab Notes',
    blurb: 'What we shipped in the open lab, with the evidence trail attached.',
    icon: '⌬',
    accent: 'var(--color-lime)',
  },
};

export type AnyEntry = CollectionEntry<CollectionKey>;

export function computeReadingMinutes(body: string): number {
  return Math.max(1, Math.round(readingTime(body || '').minutes));
}

/** Reading time from frontmatter if present, else computed from the body. */
export function minutesFor(entry: AnyEntry): number {
  const fm = (entry.data as { readingTime?: number }).readingTime;
  return fm ?? computeReadingMinutes(entry.body ?? '');
}

export function urlFor(entry: AnyEntry): string {
  return `/${entry.collection}/${entry.slug}`;
}

export async function getPublished<C extends CollectionKey>(collection: C) {
  const entries = await getCollection(collection, ({ data }) => import.meta.env.PROD ? !(data as { draft?: boolean }).draft : true);
  return entries.sort((a, b) => {
    const ao = (a.data as { order?: number }).order ?? 999;
    const bo = (b.data as { order?: number }).order ?? 999;
    if (ao !== bo) return ao - bo;
    return String(a.slug).localeCompare(String(b.slug));
  });
}

/**
 * Every content article across sections, newest-updated first.
 *
 * Derived from `SECTION_META` rather than a second hand-written list: this used
 * to be a literal array, and adding a collection to it was a step easy to skip.
 * The site then rendered the new section correctly everywhere except the home
 * page's article count - a wrong number is worse than a missing page, because
 * nothing looks broken. `scripts/check-collections.mjs` guards the one coupling
 * that remains, between the schema and this map.
 */
export async function getAllArticles(): Promise<AnyEntry[]> {
  const keys = Object.keys(SECTION_META) as CollectionKey[];
  const all = await Promise.all(keys.map((k) => getCollection(k)));
  return all
    .flat()
    .filter((e) => (import.meta.env.PROD ? !(e.data as { draft?: boolean }).draft : true))
    .sort((a, b) => +new Date((b.data as { updated: Date }).updated) - +new Date((a.data as { updated: Date }).updated));
}

export const LEVEL_ORDER: Record<string, number> = { beginner: 0, intermediate: 1, advanced: 2 };
