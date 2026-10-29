import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://kookboek.fldr.nl',
  trailingSlash: 'always',
  build: { format: 'directory' },
  compressHTML: true,
});
