// @ts-check
import { defineConfig } from 'astro/config';

// La web se publica en la raíz. BASE_PATH solo haría falta para publicar en una subcarpeta.
export default defineConfig({
  site: 'https://sinadjetivos.es',
  base: process.env.BASE_PATH || '/',
});
