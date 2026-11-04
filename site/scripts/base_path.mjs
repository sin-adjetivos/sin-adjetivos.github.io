// La web se publica en una subcarpeta (usuario.github.io/sin-adjetivos). Esto añade el prefijo a los enlaces internos.
// Con dominio propio bastará con no definir BASE_PATH y este paso no hará nada.
import fs from 'node:fs';
import path from 'node:path';

const base = (process.env.BASE_PATH || '').replace(/\/$/, '');
if (!base) process.exit(0);
const sin = base.slice(1);
const atributos = new RegExp(`\\b(href|src)="/(?!/)(?!${sin}/)`, 'g');
let n = 0;
function recorre(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { if (e.name !== 'pagefind' && e.name !== 'datos') recorre(p); continue; }
    if (!e.name.endsWith('.html')) continue;
    const a = fs.readFileSync(p, 'utf-8');
    const b = a.replace(atributos, `$1="${base}/`)
      .replace(/fetch\('\/datos\//g, `fetch('${base}/datos/`)
      .replace(/baseUrl: '\/'/g, `baseUrl: '${base}/'`);
    if (a !== b) { fs.writeFileSync(p, b); n++; }
  }
}
recorre('dist');
console.log(`Prefijo ${base} aplicado en ${n} páginas`);
