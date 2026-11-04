// Noticias propias en formato RSS. Sin dependencias: es un archivo de texto generado al construir la web.
import noticias from '../data/noticias_propias.json';

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const fecha = (iso) => new Date(`${iso}T12:00:00Z`).toUTCString();

export function GET({ site }) {
  const entradas = noticias.map((n) => {
    const url = new URL(`actualidad/${n.id}/`, site).href;
    return `<item><title>${esc(n.titulo)}</title><link>${url}</link><guid>${url}</guid><pubDate>${fecha(n.fecha)}</pubDate><description>${esc(n.entradilla)}</description></item>`;
  });
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>Sin adjetivos</title>
<link>${site.href}</link>
<atom:link href="${new URL('rss.xml', site).href}" rel="self" type="application/rss+xml" />
<description>Lo que ha pasado, contado con hechos y con sus fuentes a la vista.</description>
<language>es-ES</language>
${entradas.join('\n')}
</channel></rss>
`;
  return new Response(xml, { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } });
}
