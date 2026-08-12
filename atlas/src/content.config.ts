import { defineCollection, reference } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

/**
 * Shared frontmatter contract for every article on Agentic Atlas.
 *
 * The pipeline (pipeline/ingest.py) and human authors both write files that
 * conform to this schema. `astro check` / `astro build` will FAIL if any file
 * violates it - this is the guardrail that keeps content consistent.
 */

const LEVELS = ['beginner', 'intermediate', 'advanced'] as const;

const source = z.object({
  title: z.string(),
  url: z.url(),
  publisher: z.string().optional(),
  // License of the *original* referenced material, so we attribute correctly.
  license: z.string().optional(),
  accessed: z.string().optional(),
});

const baseArticle = z.object({
  title: z.string().max(120),
  description: z.string().max(320),
  level: z.enum(LEVELS),
  // Estimated reading time in minutes. House rule: keep articles 5–15 min.
  readingTime: z.number().min(1).max(30).optional(),
  tags: z.array(z.string()).default([]),
  // When the article was first created. Optional so pre-existing files still
  // validate; new articles set it and it is preserved across updates.
  created: z.coerce.date().optional(),
  updated: z.coerce.date(),
  draft: z.boolean().default(false),
  // Where the knowledge came from - drives the "Sources & attribution" block.
  sources: z.array(source).default([]),
  // Content license for THIS article (defaults to repo content license).
  license: z.string().default('CC-BY-4.0'),
  // Set true when a machine drafted it and a human has not yet reviewed.
  aiGenerated: z.boolean().default(false),
  order: z.number().optional(),
});

const foundations = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/foundations' }),
  schema: baseArticle,
});

const patterns = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/patterns' }),
  schema: baseArticle.extend({
    problem: z.string().optional(),
    alsoKnownAs: z.array(z.string()).default([]),
  }),
});

const production = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/production' }),
  schema: baseArticle,
});

const comparisons = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/comparisons' }),
  schema: baseArticle,
});

const caseStudies = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/case-studies' }),
  schema: baseArticle.extend({
    company: z.string(),
    domain: z.string().optional(),
  }),
});

/** The Awesome-list-style framework catalog. Richer, structured metadata. */
const frameworks = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/frameworks' }),
  schema: baseArticle.extend({
    name: z.string(),
    category: z.enum([
      'orchestration',
      'sdk',
      'protocol',
      'rag',
      'runtime',
      'observability',
      'eval',
      'toolkit',
    ]),
    language: z.array(z.string()).default([]),
    repo: z.url().optional(),
    homepage: z.url().optional(),
    docs: z.url().optional(),
    codeLicense: z.string().optional(),
    maturity: z.enum(['experimental', 'beta', 'stable', 'mature']).default('beta'),
    maintainer: z.string().optional(),
    supportsMcp: z.boolean().default(false),
    supportsMultiAgent: z.boolean().default(false),
  }),
});

/** Generated / curated news aggregation posts. */
const news = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/news' }),
  schema: baseArticle.extend({
    published: z.coerce.date(),
  }),
});

const learningPaths = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/learning-paths' }),
  schema: baseArticle.extend({
    steps: z.array(reference('foundations').or(z.string())).default([]),
  }),
});

/**
 * Lab notes: the aggregation surface for the monorepo's own projects.
 *
 * Every project in this repository ends in a module article under
 * `<module>/docs/articles/<date>-<project>/`; `scripts/intake-module-article.mjs`
 * turns one of those into an entry here, and the atlas CI workflow fails when a
 * module article has no entry. That is what makes "publishing the article
 * triggers the Atlas update" (sdlc/LIFECYCLE.md) a mechanism rather than a
 * sentence.
 *
 * `case-studies` stays what it has always been: other people's systems, read
 * from public engineering writing. These are ours, with the evidence trail
 * attached.
 */
const lab = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/lab' }),
  schema: baseArticle.extend({
    /** Owning module, e.g. `models`, `prod`, `atlas`. */
    module: z.string(),
    /** Project slug, matching the module article's directory. */
    project: z.string(),
    /** Repository-relative path of the module article this entry summarizes. */
    articlePath: z.string(),
    /** Project issue number in the core repository. */
    issue: z.number().int().positive().optional(),
    /** PR number that delivered the project. */
    pr: z.number().int().positive().optional(),
    /**
     * Evidence tier of the strongest claim in the source article. The last five
     * are the repository's tiers from AXIS.md; `process` and `smoke` sit below
     * them for work whose evidence is a green pipeline or a scaled-down run.
     * A lab note never presents a lower tier as a higher one.
     */
    evidenceTier: z
      .enum([
        'process',
        'smoke',
        'simulation-demo',
        'simulation-benchmark',
        'distributed-benchmark',
        'hardware-in-the-loop',
        'physical',
      ])
      .default('process'),
  }),
});

export const collections = {
  foundations,
  frameworks,
  patterns,
  production,
  comparisons,
  'case-studies': caseStudies,
  news,
  'learning-paths': learningPaths,
  lab,
};
