// Imágenes verticales para vídeos, generadas desde los datos de las fichas: los votos no se escriben a mano.
// Uso, desde la carpeta del proyecto: node marca/tiktok/generar.cjs   (necesita playwright-core en NODE_PATH y Chrome)
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');
const raiz = path.resolve(__dirname, '..', '..');
const fichas = JSON.parse(fs.readFileSync(path.join(raiz, 'site/src/data/fichas.json'), 'utf-8'));
const cands = JSON.parse(fs.readFileSync(path.join(raiz, 'site/src/data/candidaturas.json'), 'utf-8'));
const { VIDEOS } = require('./videos.cjs');
const COLOR = { pp: '#1D84CE', psoe: '#EF1C27', vox: '#63BE21', 'frente-amplio': '#F07901', podemos: '#9269F5', compromis: '#FF6600', erc: '#DAC125', junts: '#00C7AE', 'eh-bildu': '#00AC8E', pnv: '#4AAE4A', bng: '#ADCFEF', 'coalicion-canaria': '#FFD700' };
const lum = (h) => { const v = [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255).map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
const tinta = (h) => ((lum(h) + 0.05) / 0.05 >= 1.05 / (lum(h) + 0.05) ? '#000' : '#fff');
const nombre = (id) => { const c = cands.find((x) => x.id === id); return c.etiqueta_voto || c.sigla; };
const SEPIA = '#c4a982';
const TRAZO = (x, y, w, h, c, rot = -2) => `<g transform="rotate(${rot} ${x + w / 2} ${y + h / 2})"><path fill="${c}" d="M${x + h * .25},${y + h * .18} C${x + w * .2},${y - h * .06} ${x + w * .45},${y + h * .1} ${x + w * .62},${y + h * .02} S${x + w * .92},${y - h * .05} ${x + w - h * .1},${y + h * .16} C${x + w + h * .12},${y + h * .3} ${x + w + h * .06},${y + h * .72} ${x + w - h * .16},${y + h * .86} C${x + w * .78},${y + h * 1.04} ${x + w * .55},${y + h * .84} ${x + w * .34},${y + h * .96} S${x + h * .3},${y + h * 1.06} ${x + h * .08},${y + h * .82} C${x - h * .14},${y + h * .62} ${x - h * .04},${y + h * .3} ${x + h * .25},${y + h * .18} Z"/></g>`;
const LOGO = (lado) => `<svg width="${lado}" height="${lado}" viewBox="0 0 360 360"><text x="180" y="188" font-family="bric" font-size="176" font-weight="800" fill="#fff" text-anchor="middle" letter-spacing="-3">sin</text>${TRAZO(74, 214, 212, 40, SEPIA)}</svg>`;
const CSS = `@font-face{font-family:bric;src:url(../fuente/bricolage-grotesque-latin-standard-normal.woff2);font-weight:200 800;font-stretch:75% 100%}
*{box-sizing:border-box;margin:0}body{background:#000}
.s{width:1080px;height:1920px;background:#000;color:#fff;font-family:bric;padding:230px 150px 420px 80px;display:flex;flex-direction:column;justify-content:center;position:relative;overflow:hidden}
.tema{color:${SEPIA};font-size:44px;font-weight:700;margin-bottom:34px}
h1{font-size:112px;line-height:1;font-weight:800;letter-spacing:-.02em}
h2{font-size:78px;line-height:1.04;font-weight:800;margin-bottom:46px;letter-spacing:-.01em}
.p{font-size:54px;line-height:1.24;font-weight:500}.p+.p{margin-top:34px}
.dato{font-size:60px;font-weight:800;margin-top:46px;line-height:1.1}
.trazo{height:46px;margin-top:40px;width:430px}
.op{margin-top:30px}.op b{display:block;font-size:50px;margin-bottom:14px;color:${SEPIA}}
.c{display:inline-block;font-size:44px;font-weight:700;padding:8px 20px;margin:0 12px 14px 0}
.web{font-size:60px;font-weight:800;color:${SEPIA};margin-top:40px;word-break:break-word}
.pie{position:absolute;left:80px;bottom:440px;font-size:30px;color:#a8a8a8}
.num{position:absolute;right:150px;top:150px;}`;
const marca = `<div class="num">${LOGO(120)}</div>`;
const trazo = `<svg class="trazo" viewBox="0 0 430 46">${TRAZO(6, 4, 418, 38, SEPIA, -.7)}</svg>`;
function votos(v) {
  const g = v.grupos || {}; const f = { 'Sí': [], 'No': [], 'Abstención': [] };
  for (const id of Object.keys(COLOR)) { const t = g[id]; if (!t) continue; const u = Object.keys(f).filter((o) => t[o]); for (const o of u) f[o].push(`<span class="c" style="background:${COLOR[id]};color:${tinta(COLOR[id])}">${nombre(id)}${u.length > 1 ? ` (${t[o]})` : ''}</span>`); }
  return Object.entries(f).filter(([, l]) => l.length).map(([o, l]) => `<div class="op"><b>${o}</b>${l.join('')}</div>`).join('');
}
const fechaTxt = (iso) => { const M = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']; const [a, m, d] = iso.split('-').map(Number); return `${d} de ${M[m - 1]} de ${a}`; };
function diapositivas(vid) {
  if (vid.tipo === 'presentacion') return vid.diapos.map((d) => `<div class="s">${marca}<h1>${d.t}</h1>${trazo}${d.p ? `<p class="p" style="margin-top:40px">${d.p}</p>` : ''}${d.web ? `<p class="web">${d.web}</p>` : ''}</div>`);
  const f = fichas.find((x) => x.id === vid.ficha); if (!f) throw new Error('Sin ficha: ' + vid.ficha);
  const v = f.voto; const tema = vid.tema;
  return [
    `<div class="s">${marca}<p class="tema">${tema}</p><h1>${vid.gancho}</h1>${trazo}</div>`,
    `<div class="s">${marca}<h2>Qué era</h2>${vid.que_era.map((p) => `<p class="p">${p}</p>`).join('')}${vid.ojo ? `<p class="dato" style="color:${SEPIA}">${vid.ojo}</p>` : ''}</div>`,
    `<div class="s">${marca}<h2>Qué votó cada partido</h2><p class="p" style="font-size:40px">${fechaTxt(v.fecha)}</p>${votos(v)}<p class="p" style="font-size:30px;color:#a8a8a8;margin-top:24px">Sumar es el antecedente parlamentario de Frente Amplio.</p></div>`,
    `<div class="s">${marca}<h2>Qué pasó</h2><p class="dato" style="margin-top:0">${v.si} sí, ${v.no} no${v.abst ? `, ${v.abst} abstenciones` : ''}</p><p class="p" style="margin-top:40px">${vid.paso}</p></div>`,
    `<div class="s">${marca}<h1>Lee qué dijo cada grupo</h1>${trazo}<p class="web">sin-adjetivos.github.io</p><p class="p" style="margin-top:40px;font-size:42px">Con la fuente al lado. Si hay un error, lo corregimos.</p></div>`,
  ];
}
(async () => {
  const b = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', args: ['--allow-file-access-from-files'] });
  const tmp = path.join(__dirname, '_tmp.html');
  for (const vid of VIDEOS) {
    const dir = path.join(__dirname, vid.carpeta); fs.mkdirSync(dir, { recursive: true });
    const ds = diapositivas(vid);
    for (let i = 0; i < ds.length; i++) {
      fs.writeFileSync(tmp, `<!doctype html><meta charset="utf-8"><style>${CSS}</style>${ds[i]}`);
      const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
      await p.goto('file:///' + tmp.replace(/\\/g, '/')); await p.waitForTimeout(350);
      const sobra = await p.evaluate(() => { const s = document.querySelector('.s'); return s.scrollHeight - s.clientHeight; });
      if (sobra > 0) console.log('AVISO: no cabe', vid.carpeta, i + 1, sobra);
      await p.screenshot({ path: path.join(dir, `${String(i + 1).padStart(2, '0')}.png`) });
      await p.close();
    }
    console.log(vid.carpeta, ds.length);
  }
  fs.unlinkSync(tmp); await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
