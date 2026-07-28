import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { getAllArticles, urlFor } from '../lib/content';

export async function GET(context: APIContext) {
  const articles = await getAllArticles();
  return rss({
    title: 'Agentic Atlas',
    description:
      'A technical field guide and news aggregator for AI agents, frameworks, and production patterns.',
    site: context.site ?? 'https://agentic-atlas.vercel.app',
    items: articles.slice(0, 50).map((entry) => {
      const data = entry.data as any;
      return {
        title: data.title,
        description: data.description,
        link: urlFor(entry),
        pubDate: new Date(data.published ?? data.updated),
        categories: [entry.collection, data.level, ...(data.tags ?? [])],
      };
    }),
    customData: '<language>en-us</language>',
  });
}
