// Resumen de la web para asistentes de IA (convención llmstxt.org). Se genera al construir para que incluya las últimas noticias.
import noticias from '../data/noticias_propias.json';
import temas from '../data/temas.json';

export function GET({ site }) {
  const u = (r) => new URL(r, site).href;
  const texto = `# Sin adjetivos

> Portal independiente en español sobre las elecciones generales de España del 29 de noviembre de 2026: votaciones del Congreso, listas por provincia, programas, plenos, causas judiciales y noticias, con la fuente original de cada dato. Lo firma Sergio Capuchino, sin vinculación con partidos.

No publica encuestas, puntuaciones ni rankings de partidos, y no recomienda a quién votar. Las citas se comprueban automáticamente contra su fuente. Una investigación judicial no es una condena: cada caso indica su estado exacto, y hay que citarlo igual.

## Información práctica
- [Cómo votar](${u('como-votar/')}): documentación, papeletas, voto por correo, mesas electorales y plazos oficiales.
- [Listas por provincia](${u('papeleta/')}): candidaturas proclamadas al Congreso, según el BOE.

## Partidos y temas
- [Candidaturas](${u('candidaturas/')}): propuestas, votos, antecedentes y causas de cada una.
- [Temas](${u('temas/')}): ${temas.map((t) => t.nombre).join(', ')}.
- [Votaciones](${u('votaciones/')}): votaciones del Congreso en esta legislatura.
- [Plenos](${u('plenos/')}): transcripciones íntegras.
- [Causas judiciales](${u('causas/')}): casos, estado y fuentes.

## Noticias recientes
${noticias.slice(0, 15).map((n) => `- [${n.titulo}](${u(`actualidad/${n.id}/`)}) (${n.fecha}): ${n.entradilla}`).join('\n')}

## Sobre la web
- [Cómo trabajamos](${u('metodologia/')}): método, uso de inteligencia artificial y límites.
- [Quién firma](${u('quien-firma/')})
- [Correcciones](${u('correcciones/')})
- [Noticias en RSS](${u('rss.xml')})
`;
  return new Response(texto, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}
