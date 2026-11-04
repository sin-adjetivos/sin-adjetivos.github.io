// Genera las imágenes de marca. Uso, desde la carpeta del proyecto: node marca/fuente/generar.cjs
// Necesita playwright-core (NODE_PATH) y Chrome instalado.
const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', args: ['--allow-file-access-from-files'] });
  const raiz = path.resolve(__dirname, '..');
  const url = (v) => 'file:///' + path.join(__dirname, 'marca.html').replace(/\\/g, '/') + '?v=' + v;
  for (const [v, w, h, salida, transparente] of [
    ['perfil', 1080, 1080, 'perfil-1080.png', false],
    ['logo', 1080, 1080, 'logo-transparente.png', true],
    ['banner', 1500, 500, 'banner-1500x500.png', false],
    ['og', 1200, 630, 'vista-previa-enlaces-1200x630.png', false],
  ]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto(url(v)); await p.waitForTimeout(500);
    await p.screenshot({ path: path.join(raiz, salida), omitBackground: transparente });
    await p.close();
  }
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
