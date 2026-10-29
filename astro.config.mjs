import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://uit-de-pluktuin.pages.dev',
  trailingSlash: 'always',
  build: { format: 'directory' },
  compressHTML: true,
});
