import temas from '../data/temas.json';
import candidaturasRaw from '../data/candidaturas.json';
import posiciones from '../data/posiciones.json';
import dijo from '../data/dijo.json';
import votos from '../data/votos.json';
import provincias from '../data/provincias.json';
import casos from '../data/casos.json';
import estados from '../data/estados.json';
import resumen from '../data/resumen.json';

// Orden alfabético sin JavaScript; con JavaScript se baraja en cada visita.
const candidaturas = [...candidaturasRaw].sort((a, b) => a.sigla.localeCompare(b.sigla, 'es'));
const porId = Object.fromEntries(candidaturas.map((c) => [c.id, c]));

export { temas, candidaturas, porId, posiciones, dijo, votos, provincias, casos, estados, resumen };

const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
export function fecha(iso) {
  const [a, m, d] = iso.split('-').map(Number);
  return d ? `${d} de ${MESES[m - 1]} de ${a}` : `${MESES[m - 1]} de ${a}`;
}

const OPCIONES = ['Sí', 'No', 'Abstención'];
/** Reparte las candidaturas por su voto. Si un grupo se dividió, indica cuántos votaron cada opción. */
export function reparto(voto) {
  const datos = voto.por_candidatura || voto.grupos;
  if (!datos) return null;
  const filas = { 'Sí': [], 'No': [], 'Abstención': [] };
  for (const c of candidaturas) {
    const t = datos[c.id];
    if (!t) continue;
    const usados = OPCIONES.filter((o) => t[o]);
    for (const o of usados) filas[o].push({ id: c.id, nombre: c.etiqueta_voto || c.sigla, n: usados.length > 1 ? t[o] : null });
  }
  return filas;
}
/** Voto de una candidatura en una votación, en palabras. */
export function votoDe(voto, c) {
  if (!c.grupo) return null;
  if (!voto.por_candidatura) return 'Sin desglose por grupo';
  const t = voto.por_candidatura[c.id];
  if (!t) return 'No consta';
  const usados = OPCIONES.filter((o) => t[o]);
  if (!usados.length) return 'No votó';
  return usados.length === 1 ? usados[0] : usados.map((o) => `${t[o]} ${o.toLowerCase()}`).join(', ');
}

export const AVISOS = {
  vivienda: {
    texto: 'Tras la caída de estos decretos, el Gobierno aprobó el 6 de octubre los decretos 28/2026 y 29/2026, que los reproducen en lo sustancial. Está previsto que la Diputación Permanente los vote el 12 de noviembre.',
    fuente: 'Legal Today',
    url: 'https://www.legaltoday.com/opinion/articulos-de-opinion/los-decretos-leyes-de-vivienda-derogacion-reaprobacion-y-convalidacion-en-plena-disolucion-2026-10-08/',
  },
};

export const REPO = 'https://github.com/sin-adjetivos/sin-adjetivos.github.io';
export const CAUSAS_INTRO = 'Revisión en prensa hecha el 4 de noviembre de 2026.';
export const SIN_CAUSA = 'No hemos localizado causas penales en las que figure como parte.';
export const CAUSA_AVISO = '«No localizado» refleja nuestra búsqueda y no es un certificado: puede haber procedimientos que no hayamos encontrado.';
