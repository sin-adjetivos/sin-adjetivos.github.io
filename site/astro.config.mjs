// @ts-check
import { defineConfig } from 'astro/config';

// BASE_PATH solo se define al publicar en GitHub Pages.
export default defineConfig({
  site: 'https://srcapuchino.github.io',
  base: process.env.BASE_PATH || '/',
});
