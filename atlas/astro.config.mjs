// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

// Update `site` to your production Vercel/custom domain once deployed.
// It is used for canonical URLs, sitemap, and RSS feed links.
const SITE = process.env.SITE_URL || 'https://agentic-atlas.vercel.app';

// https://astro.build/config
export default defineConfig({
  site: SITE,
  output: 'static',
  trailingSlash: 'ignore',
  integrations: [
    mdx(),
    sitemap(),
  ],
  vite: {
    // Cast avoids a spurious duplicate-Vite type mismatch between Astro's
    // bundled Vite and @tailwindcss/vite; the build itself is unaffected.
    plugins: [/** @type {any} */ (tailwindcss())],
  },
  markdown: {
    shikiConfig: {
      theme: 'github-dark-dimmed',
      wrap: true,
    },
  },
});
