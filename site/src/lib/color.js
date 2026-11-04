// Color de referencia de cada candidatura: el que usa Wikipedia en sus tablas electorales.
// No son referencias Pantone oficiales: los partidos no las publican de forma homogénea.
export const COLORES = {
  pp: '#1D84CE', psoe: '#EF1C27', vox: '#63BE21', 'frente-amplio': '#F07901', podemos: '#9269F5', compromis: '#FF6600',
  'unidad-pueblo-canario': '#639E42', 'ara-mes': '#45BB89', erc: '#DAC125', junts: '#00C7AE', 'eh-bildu': '#00AC8E',
  pnv: '#4AAE4A', bng: '#ADCFEF', 'coalicion-canaria': '#FFD700', gobierno: '#595959',
};
function lum(hex) {
  const v = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
}
const contraste = (a, b) => (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
/** Texto pequeño: el de mayor contraste. */
export function tinta(hex) {
  const l = lum(hex);
  return contraste(l, 1) >= contraste(l, 0) ? '#fff' : '#000';
}
/** Titular grande: blanco si llega a 3:1, que es el mínimo para letra grande; si no, negro. */
export function tintaTitular(hex) {
  return contraste(lum(hex), 1) >= 3 ? '#fff' : '#000';
}
export const estiloChip = (id) => `--c:${COLORES[id] || '#000'};--t:${tinta(COLORES[id] || '#000')}`;
