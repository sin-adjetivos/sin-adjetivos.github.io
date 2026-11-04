"""Actualidad: recoge titulares de feeds públicos y agrupa los que hablan de lo mismo. Sin IA: solo titular, medio, fecha y enlace."""
import json, os, re, math, sys, html, unicodedata, collections, datetime as dt, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
sys.path.insert(0, 'scripts')
from reglas import TEMA_RX

FEEDS = {
 'ABC': 'https://www.abc.es/rss/2.0/espana/', 'Ara': 'https://www.ara.cat/rss/politica/', 'COPE': 'https://www.cope.es/rss/actualidad.xml',
 'El Confidencial': 'https://rss.elconfidencial.com/espana/', 'elDiario.es': 'https://www.eldiario.es/rss/politica/', 'El Español': 'https://www.elespanol.com/rss/espana/',
 'El Mundo': 'https://e00-elmundo.uecdn.es/elmundo/rss/espana.xml', 'El País': 'https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/espana/portada',
 'Europa Press': 'https://www.europapress.es/rss/rss.aspx?ch=00066', 'infoLibre': 'https://www.infolibre.es/rss', 'La Vanguardia': 'https://www.lavanguardia.com/rss/politica.xml',
 'Libertad Digital': 'https://feeds2.feedburner.com/libertaddigital/nacional', 'OKdiario': 'https://okdiario.com/espana/feed', 'RTVE': 'https://api2.rtve.es/rss/temas_espana.xml',
 'The Objective': 'https://theobjective.com/feed/', '20minutos': 'https://www.20minutos.es/rss/nacional/',
 'El Debate': 'https://www.eldebate.com/rss/espana.xml', 'La Razón': 'https://www.larazon.es/espana/?outputType=xml',
}
SIN_FEED = ['Público', 'Vozpópuli']
ALMACEN = 'data/noticias.json'; SALIDA = 'site/src/data/actualidad.json'
UA = {'User-Agent': 'Mozilla/5.0 (compatible; SinAdjetivos/0.2; +https://sin-adjetivos.github.io/metodologia/)'}
VACIAS = set("""a al algo ante antes como con contra cual cuando de del desde donde dos durante e el ella ellas ello ellos en entre era es esa ese eso esta este esto estos fue ha han hasta hay la las le les lo los mas me mi mientras muy ni no nos o otra otro para pero por porque que quien se sea segun ser si sin sobre son su sus tambien te tiene tras tu un una uno unos unas y ya yo va van dice dicen asi aun ahora hoy ayer este esta tras vez anos ano dia dias""".split())

def llano(s):
    return unicodedata.normalize('NFKD', s.lower()).encode('ascii', 'ignore').decode()
def tokens(s):
    return [t for t in re.findall(r'[a-z0-9]{3,}', llano(s)) if t not in VACIAS]
def limpio(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()
def fecha(s):
    if not s: return None
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        try: d = dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
        except Exception: return None
    if d.tzinfo is None: d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(dt.timezone.utc).isoformat(timespec='minutes')

def leer(medio, url):
    b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
    raiz = ET.fromstring(b); out = []
    for it in raiz.iter():
        if it.tag.split('}')[-1] not in ('item', 'entry'): continue
        d = {}
        for h in it:
            k = h.tag.split('}')[-1]
            if k == 'link' and not (h.text or '').strip(): d.setdefault('link', h.get('href'))
            else: d.setdefault(k, h.text)
        t = limpio(d.get('title')); l = (d.get('link') or '').strip()
        if t and l.startswith('http'):
            # El resumen se usa solo para agrupar; no se publica.
            out.append(dict(medio=medio, titulo=t, url=l, fecha=fecha(d.get('pubDate') or d.get('published') or d.get('updated') or d.get('date')), _r=limpio(d.get('description') or d.get('summary'))[:400]))
    return out

def agrupar(items):
    """Agrupación voraz por similitud del coseno TF-IDF. Pesa más el titular que el resumen."""
    df = collections.Counter()
    vec = []
    for it in items:
        c = collections.Counter(tokens(it['titulo']) * 3 + tokens(it.get('_r', '')))
        vec.append(c); df.update(c.keys())
    N = len(items) or 1
    pesos = []
    for c in vec:
        v = {t: f * math.log(1 + N / df[t]) for t, f in c.items()}
        n = math.sqrt(sum(x * x for x in v.values())) or 1
        pesos.append({t: x / n for t, x in v.items()})
    grupos = []
    for i in sorted(range(len(items)), key=lambda k: items[k]['fecha'] or ''):
        mejor = None; ms = 0
        for g in grupos:
            sim = sum(pesos[i].get(t, 0) * x for t, x in g['c'].items())
            if sim > ms: ms, mejor = sim, g
        if mejor and ms >= 0.34:
            mejor['i'].append(i)
            for t, x in pesos[i].items(): mejor['s'][t] += x
            n = math.sqrt(sum(x * x for x in mejor['s'].values())) or 1
            mejor['c'] = {t: x / n for t, x in mejor['s'].items()}
        else:
            s = collections.Counter(pesos[i]); grupos.append(dict(i=[i], s=s, c=dict(pesos[i])))
    return grupos

def main():
    viejas = json.load(open(ALMACEN, encoding='utf-8')) if os.path.exists(ALMACEN) else []
    por_url = {n['url']: n for n in viejas}; estado = {}
    ahora = dt.datetime.now(dt.timezone.utc)
    for medio, url in FEEDS.items():
        try:
            nuevas = leer(medio, url); estado[medio] = len(nuevas)
            for n in nuevas:
                if not n['fecha']: n['fecha'] = ahora.isoformat(timespec='minutes')
                if n['url'] in por_url: por_url[n['url']]['_r'] = n['_r']
                else: por_url[n['url']] = n
        except Exception as e:
            estado[medio] = 'ERROR ' + str(e)[:50]
    limite = (ahora - dt.timedelta(days=45)).isoformat()
    todas = sorted((n for n in por_url.values() if (n['fecha'] or '') >= limite), key=lambda n: n['fecha'], reverse=True)
    # El resumen del medio solo se usa aquí, para agrupar. No se guarda ni se publica.
    json.dump([{k: v for k, v in n.items() if k != '_r'} for n in todas], open(ALMACEN, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    ventana = (ahora - dt.timedelta(hours=72)).isoformat()
    recientes = [n for n in todas if n['fecha'] >= ventana and n['fecha'] <= (ahora + dt.timedelta(hours=2)).isoformat()]
    grupos = agrupar(recientes); salida = []
    for g in grupos:
        its = sorted((recientes[i] for i in g['i']), key=lambda n: n['fecha'])
        por_medio = {}
        for n in its: por_medio.setdefault(n['medio'], n)   # un titular por medio: el primero publicado
        if len(por_medio) < 3: continue
        titulares = list(por_medio.values())
        texto = ' '.join(n['titulo'] for n in titulares)
        temas = [k for k, rx in TEMA_RX.items() if re.search(rx, texto, re.I)]
        cuenta = collections.Counter(t for n in titulares for t in set(tokens(n['titulo'])))
        comunes = [t for t, c in cuenta.most_common(8) if c >= max(2, len(titulares) // 2)]
        salida.append(dict(medios=len(por_medio), desde=its[0]['fecha'], hasta=its[-1]['fecha'], temas=temas, comunes=comunes,
                           titulares=[{k: n[k] for k in ('medio', 'titulo', 'url', 'fecha')} for n in sorted(titulares, key=lambda n: llano(n['medio']))]))
    salida.sort(key=lambda g: (-g['medios'], g['hasta']))
    json.dump(dict(actualizado=ahora.isoformat(timespec='minutes'), estado=estado, sin_feed=SIN_FEED, grupos=salida[:40], recogidas=len(recientes)), open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('feeds', estado); print('recientes', len(recientes), 'grupos con 3 o más medios', len(salida))
    for g in salida[:9]:
        print(f"\n[{g['medios']} medios] comunes={g['comunes'][:5]} temas={g['temas']}")
        for t in g['titulares'][:5]: print('  ', t['medio'], '|', t['titulo'][:100])
if __name__ == '__main__':
    main()
