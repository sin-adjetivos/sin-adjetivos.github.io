"""Comprueba y genera las noticias propias. Falla si una frase entre « » o una cifra no está en las fuentes de ese párrafo, si un párrafo no lleva fuente o si la redacción usa palabras valorativas.
Las páginas se guardan en raw/noticias para poder repetir la comprobación aunque el medio cambie el artículo. Con --borrador añade las de borrador_noticias.py, que no sube a GitHub, para verlas en local."""
import hashlib, html, json, os, re, sys, urllib.request
sys.path.insert(0, 'scripts')
from lib_pdf import norm
from fuente_noticias import NOTICIAS, PROPIA, OFICIAL

BORRADOR = '--borrador' in sys.argv
PUBLICADAS = {n['id'] for n in NOTICIAS}
if BORRADOR and os.path.exists('scripts/borrador_noticias.py'):
    from borrador_noticias import BORRADORES
    NOTICIAS = NOTICIAS + BORRADORES
CACHE = 'raw/noticias'; SALIDA = 'site/src/data/noticias_propias.json'
UA = {'User-Agent': 'Mozilla/5.0 (compatible; SinAdjetivos/0.2; +https://sinadjetivos.es/metodologia/)'}
VALORATIVAS = r'\b(polémic\w*|histórico|histórica|importante\w*|grave\w*|escandal\w*|escándalo\w*|enorme\w*|radical\w*|extremo|extrema|ultra\w*|duro|dura|valiente\w*|vergonz\w*|polarizad\w*|controvertid\w*|ambicios\w*|necesari\w*|buen\w*|mal[oa]s?|tragedia\w*|trágic\w*|dramátic\w*|brutal\w*|bochorn\w*|clamor\w*|golpista\w*|huy\w+|sorprendente\w*|encuesta\w*|sondeo\w*)\b'
CANDIDATURAS = {c['id'] for c in json.load(open('site/src/data/candidaturas.json', encoding='utf-8'))} | {'gobierno'}
FICHAS = {f['id']: f for f in json.load(open('site/src/data/fichas.json', encoding='utf-8'))}
errores = []

def texto_de(fuente):
    if fuente.get('local'): return json.dumps(FICHAS[fuente['local']], ensure_ascii=False)
    if fuente.get('texto'): return fuente['texto']
    os.makedirs(CACHE, exist_ok=True)
    ruta = os.path.join(CACHE, hashlib.sha1(fuente['url'].encode()).hexdigest()[:16] + '.txt')
    if os.path.exists(ruta): return open(ruta, encoding='utf-8').read()
    r = urllib.request.urlopen(urllib.request.Request(fuente['url'], headers=UA), timeout=40)
    b = r.read()
    m = re.search(rb'charset=["\']?([\w-]+)', b[:3000])
    cod = r.headers.get_content_charset() or (m.group(1).decode() if m else 'utf-8')
    t = b.decode(cod, 'replace')
    t = re.sub(r'</?(a|em|strong|b|i|span|u)\b[^>]*>', '', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t)).replace('\\"', '"').replace('\\/', '/')
    t = re.sub(r'\s+', ' ', t)
    open(ruta, 'w', encoding='utf-8').write(t)
    return t

def numeros(s):
    return re.findall(r'\d+(?:[.,:]\d+)*', s)

def comprobar(n, texto, donde, textos, exigir_fuente=True):
    """Comprueba un párrafo con sus [fuentes]."""
    refs = re.findall(r'\[([a-z0-9-]+)\]', texto)
    desconocidas = [r for r in refs if r not in textos]
    if desconocidas: errores.append(f"{n['id']}: fuente desconocida {desconocidas} en {donde}")
    if exigir_fuente and not refs: errores.append(f"{n['id']}: sin fuente en {donde}: {texto[:70]}")
    pelado = re.sub(r'\[\[([^|\]]+)\|[^\]]+\]\]', r'\1', texto)
    pelado = re.sub(r'\[[a-z0-9-]+\]', '', pelado)
    base = norm(' '.join(textos.get(r, '') for r in refs))
    for q in re.findall(r'«([^»]+)»', pelado):
        if norm(q) not in base: errores.append(f"{n['id']}: «{q[:60]}» no está en las fuentes de {donde}")
    sin_citas = re.sub(r'«[^»]+»', '', pelado)
    m = re.search(VALORATIVAS, sin_citas.replace('Plus Ultra', ''), re.I)
    if m: errores.append(f"{n['id']}: palabra valorativa «{m.group(0)}» en {donde}: {texto[:60]}")
    for x in numeros(sin_citas):
        if x in n.get('calculos', {}): continue
        if refs and not re.search(r'(?<![\d.,])' + re.escape(x) + r'(?!\d)', base):
            errores.append(f"{n['id']}: la cifra {x} no está en las fuentes de {donde}: {texto[:70]}")

def a_html(texto, orden):
    """[clave] pasa a nota numerada; [[texto|/ruta/]], a enlace; «cita», a la letra de las citas."""
    t = html.escape(texto, quote=False)
    t = re.sub(r'«([^»]+)»', r'<span class="cita-linea">«\1»</span>', t)
    t = re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\s*\[([a-z0-9-]+)\]', lambda m: f'<sup class="ref"><a href="#f{orden[m.group(1)]}">{orden[m.group(1)]}</a></sup>', t)
    return t

salida = []
fotos = [n['imagen']['archivo'] for n in NOTICIAS]
for x in {x for x in fotos if fotos.count(x) > 1}: errores.append(f'la foto {x} se repite en varias noticias')
for n in NOTICIAS:
    textos = {}
    for k, f in n['fuentes'].items():
        try:
            textos[k] = texto_de(f)
        except Exception as e:
            errores.append(f"{n['id']}: no se puede leer {k} ({e})"); textos[k] = ''
    orden = {k: i + 1 for i, k in enumerate(n['fuentes'])}
    if n.get('tipo') == 'propuesta':
        if n.get('partido') not in CANDIDATURAS - {'gobierno'}: errores.append(f"{n['id']}: una propuesta debe indicar su partido")
        if not any(v['c'] == n.get('partido') for v in n['voces']): errores.append(f"{n['id']}: una propuesta debe llevar una frase literal de su partido")
    elif n.get('tipo') or n.get('partido'): errores.append(f"{n['id']}: tipo desconocido; tipo y partido solo sirven para propuestas")
    medios = {f['nombre'].split(',')[0] for f in n['fuentes'].values() if f.get('tipo') not in (OFICIAL, PROPIA)}
    if len(medios) < 3: errores.append(f"{n['id']}: solo {len(medios)} medios distintos entre las fuentes")
    if not os.path.exists(f"site/public/noticias/{n['imagen']['archivo']}"): errores.append(f"{n['id']}: falta la imagen")
    for campo in ('autor', 'licencia', 'origen', 'alt', 'pie'):
        if not n['imagen'].get(campo): errores.append(f"{n['id']}: la imagen no indica {campo}")
    for campo in ('titulo', 'entradilla'):
        m = re.search(VALORATIVAS, n[campo], re.I)
        if m: errores.append(f"{n['id']}: palabra valorativa «{m.group(0)}» en {campo}")
    for i, x in enumerate(n['esencial']): comprobar(n, x, f'esencial {i}', textos)
    bloques = []
    for tipo, b in n['cuerpo']:
        if tipo == 'h': bloques.append(dict(tipo='h', texto=b))
        elif tipo == 'p':
            comprobar(n, b, 'cuerpo', textos); bloques.append(dict(tipo='p', html=a_html(b, orden)))
        elif tipo == 'tabla':
            comprobar(n, b['nota'] + ' ' + b['fuentes'], 'tabla', textos)
            comprobar(n, ' '.join(c for f in b['filas'] for c in f) + ' ' + b['fuentes'], 'tabla', textos)
            bloques.append(dict(tipo='tabla', titulo=b['titulo'], columnas=b['columnas'], filas=b['filas'], nota=a_html(b['nota'] + b['fuentes'], orden)))
        elif tipo == 'barras':
            comprobar(n, ' '.join(f['cifra'] for f in b['filas']) + ' ' + b['fuentes'], 'barras', textos)
            comprobar(n, b['total'] + ' ' + b['nota'] + ' ' + b['fuentes'], 'barras', textos)
            suma = round(sum(f['valor'] for f in b['filas']), 2)
            if f"{suma:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') != b['total']: errores.append(f"{n['id']}: las barras suman {suma}, no {b['total']}")
            maximo = max(f['valor'] for f in b['filas'])
            bloques.append(dict(tipo='barras', titulo=b['titulo'], unidad=b['unidad'], total=b['total'], nota=a_html(b['nota'] + b['fuentes'], orden), filas=[{**f, 'ancho': round(100 * f['valor'] / maximo, 1)} for f in b['filas']]))
        elif tipo == 'linea':
            for x in b: comprobar(n, x['que'], 'cronología', textos)
            bloques.append(dict(tipo='linea', hitos=[dict(cuando=x['cuando'], html=a_html(x['que'], orden)) for x in b]))
        elif tipo == 'posiciones':
            for x in b:
                comprobar(n, x['nota'], 'posiciones', textos)
                malos = set(x['grupos']) - CANDIDATURAS
                if malos: errores.append(f"{n['id']}: candidatura desconocida {malos}")
            bloques.append(dict(tipo='posiciones', filas=[dict(texto=x['texto'], grupos=x['grupos'], nota=a_html(x['nota'], orden)) for x in b]))
    voces = []
    for v in n['voces']:
        if norm(v['cita']) not in norm(textos.get(v['f'], '')): errores.append(f"{n['id']}: cita no literal de {v['quien']}: {v['cita'][:70]}")
        if v['c'] and v['c'] not in CANDIDATURAS: errores.append(f"{n['id']}: candidatura desconocida {v['c']}")
        voces.append(dict(candidatura=v['c'], rotulo=v.get('rotulo', 'Justicia'), quien=v['quien'], cita=v['cita'], traduccion=v.get('traduccion'), fuente=orden[v['f']], medio=n['fuentes'][v['f']]['nombre'].split(',')[0], url=n['fuentes'][v['f']]['url']))
    comprobar(n, n['sin_voz'], 'sin_voz', textos, exigir_fuente=False)
    for x in n['no_sabemos']: comprobar(n, x, 'no_sabemos', textos, exigir_fuente=False)
    salida.append(dict(id=n['id'], fecha=n['fecha'], tema=n['tema'], etiqueta=n['etiqueta'], claves=n['claves'], titulo=n['titulo'], entradilla=n['entradilla'], imagen=n['imagen'],
                       esencial=[a_html(x, orden) for x in n['esencial']], cuerpo=bloques, voces=voces, sin_voz=a_html(n['sin_voz'], orden), no_sabemos=[a_html(x, orden) for x in n['no_sabemos']],
                       fuentes=[dict(n=orden[k], nombre=f['nombre'], url=f['url'], tipo=f.get('tipo', 'prensa')) for k, f in n['fuentes'].items()], cambios=n.get('cambios', []), borrador=n['id'] not in PUBLICADAS,
                       abre=bool(n.get('abre')), tipo=n.get('tipo'), partido=n.get('partido')))
if errores:
    print('\n'.join(errores)); print(f'{len(errores)} errores. No se generan noticias.'); sys.exit(1)
# Del mismo día van antes la marcada con abre=True y las propuestas al final. Si no, se respeta el orden de fuente_noticias.py.
salida.sort(key=lambda n: (n['fecha'], n['tipo'] != 'propuesta', n['abre']), reverse=True)
json.dump(salida, open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(f'OK: {len(salida)} noticias' + (' (con borradores)' if BORRADOR else ''))
