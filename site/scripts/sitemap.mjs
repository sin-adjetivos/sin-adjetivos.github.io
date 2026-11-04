// Genera sitemap.xml a partir de las páginas ya construidas, para que los buscadores encuentren todas.
import fs from 'node:fs';
import path from 'node:path';

const WEB = 'https://sinadjetivos.es';
const FUERA = new Set(['/buscar/', '/404/']);
const noticias = JSON.parse(fs.readFileSync('src/data/noticias_propias.json', 'utf-8'));
const fechas = new Map(noticias.map((n) => [`/actualidad/${n.id}/`, n.cambios.at(-1)?.fecha || n.fecha]));
const rutas = [];
function recorre(dir, ruta) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.isDirectory()) { if (!['_astro', 'pagefind', 'datos', 'noticias'].includes(e.name)) recorre(path.join(dir, e.name), `${ruta}${e.name}/`); }
    else if (e.name === 'index.html' && !FUERA.has(ruta)) rutas.push(ruta);
  }
}
recorre('dist', '/');
rutas.sort();
const urls = rutas.map((r) => `<url><loc>${WEB}${encodeURI(r)}</loc>${fechas.has(r) ? `<lastmod>${fechas.get(r)}</lastmod>` : ''}</url>`);
fs.writeFileSync('dist/sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`);
console.log(`sitemap.xml: ${rutas.length} páginas`);
