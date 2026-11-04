// Archivo de plenos. Se lee del disco solo durante la generación de la web.
import fs from 'node:fs';
import path from 'node:path';

const raiz = path.join(process.cwd(), 'build-data');
const leer = (n) => JSON.parse(fs.readFileSync(path.join(raiz, `${n}.json`), 'utf-8'));
const cache = {};
const uno = (n) => (cache[n] ??= leer(n));

export const debates = () => uno('debates');
export const declaraciones = () => uno('declaraciones');
export const sesiones = () => uno('sesiones');
export const votosTodos = () => uno('votos_todos');
export const personas = () => uno('personas');
export const debate = (id) => JSON.parse(fs.readFileSync(path.join(raiz, 'debates', `${id}.json`), 'utf-8'));

/** Qué se decidía, según el tipo de votación. Si el título no lo deja claro, no se dice nada. */
export function sentido(t) {
  if (/enmienda/i.test(t)) return 'Votación de enmiendas.';
  if (/^Real Decreto-ley/i.test(t)) return 'Convalidar el decreto.';
  if (/^Tramitación como Proyecto de Ley/i.test(t)) return 'Decidía si el decreto se tramitaba además como ley.';
  if (/^(Proposición no de Ley|Moción)/i.test(t)) return 'Texto sin fuerza de ley.';
  if (/dictamen|votación de conjunto/i.test(t)) return 'Votación de la ley en su tramo final.';
  if (/^Proposición de Ley/i.test(t)) return 'Si no se indica otra cosa, decidía si empezaba a tramitarse.';
  return null;
}
