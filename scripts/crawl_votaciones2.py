"""Índice completo de votaciones, incluidas las anidadas (enmiendas, dictámenes), y voto de cada diputado. Reanudable."""
import json, os, re, time, html, datetime as dt, urllib.request, urllib.error
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) SinAdjetivos/0.2'}
BASE = 'https://www.congreso.es/es/opendata/votaciones?p_p_id=votaciones&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&targetLegislatura=XV&targetDate='
OUT = 'data/votaciones_todas.json'
def clean(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()
TOKEN = re.compile(r'<h5[^>]*>(?P<h5>.*?)</h5>|<h6[^>]*>(?P<h6>.*?)</h6>|_iniciativas_id=(?P<exp>[0-9/]+)|<p>S[ií]:\s*(?P<si>\d+)</p>\s*<p>No:\s*(?P<no>\d+)</p>\s*<p>Abstenciones:\s*(?P<ab>\d+)</p>|(?P<js>/webpublica/opendata/votaciones/[^"\']+\.json)|href="(?P<ds>https?://[^"]+DSCD[^"]+)"', re.S)
def parse(page, iso):
    """Máquina de estados: cada bloque de resultados toma el último título con expediente y su subtítulo."""
    votos = []; ultimo_h5 = principal = sub = exp = None; actual = None
    for m in TOKEN.finditer(page):
        g = m.groupdict()
        if g['h5'] is not None:
            ultimo_h5 = clean(g['h5']); sub = None; actual = None
        elif g['exp']:
            principal = ultimo_h5; exp = g['exp']; sub = None; actual = None
        elif g['h6'] is not None:
            sub = clean(g['h6']); actual = None
        elif g['si'] is not None:
            base = principal if (exp and principal) else ultimo_h5
            extra = sub or (ultimo_h5 if ultimo_h5 != base else None)
            titulo = base + (' ' + extra if extra and extra != base else '')
            actual = dict(fecha=iso, titulo=titulo, expediente=exp, si=int(g['si']), no=int(g['no']), abst=int(g['ab']), diario=None, json=None)
            votos.append(actual)
        elif g['js'] and actual is not None and not actual['json']:
            actual['json'] = g['js']
        elif g['ds'] and actual is not None and not actual['diario']:
            actual['diario'] = g['ds']
    return votos
def get(u, binario=False):
    for i in range(4):
        try:
            b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read()
            return b if binario else b.decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(8 * (i + 1))
        except Exception:
            time.sleep(8 * (i + 1))
    return None
if __name__ == '__main__':
    inter = json.load(open('raw/congreso/interv/IntervencionesCronologicamente.json', encoding='utf-8'))
    fechas = sorted({dt.datetime.strptime(r['SESION'], '%d/%m/%Y').date() for r in inter if r['ORGANO'] in ('Pleno', 'Diputación Permanente')})
    todas = []
    for f in fechas:
        iso = f.isoformat()
        p = get(BASE + f.strftime('%d/%m/%Y'))
        if p and re.search(r'Fecha\s*:\s*' + re.escape(f.strftime('%d/%m/%Y')), p):
            v = parse(p, iso); todas += v; print(iso, len(v), flush=True)
        json.dump(todas, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
        time.sleep(0.3)
    print('INDICE', len(todas), 'votaciones;', sum(1 for v in todas if v['json']), 'con voto por diputado', flush=True)
    os.makedirs('raw/congreso/votos', exist_ok=True); n = 0
    for v in todas:
        if not v['json']: continue
        fn = 'raw/congreso/votos/' + re.sub(r'\W+', '_', v['json'].split('/opendata/votaciones/')[-1])
        if os.path.exists(fn): continue
        b = get('https://www.congreso.es' + v['json'], binario=True)
        if b: open(fn, 'wb').write(b); n += 1
        if n % 100 == 0: print('votos descargados', n, flush=True)
        time.sleep(0.25)
    print('FIN votos nuevos', n, flush=True)
