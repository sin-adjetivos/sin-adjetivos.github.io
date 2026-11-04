"""Archivo de plenos: debates íntegros, posición declarada por reglas y todas las votaciones. Sin IA: todo es literal y reproducible."""
import json, os, re, sys, glob, shutil, collections, datetime as dt
sys.path.insert(0, 'scripts')
from parse_ds import turnos, casa, es_presidencia, apellidos
from lib_pdf import norm
from reglas import TEMA_RX, VOTO_RX, PROPUESTA_RX, GRUPOS, MIXTO, GOBIERNO_RX
from llamamientos import diputados, grupos_de

OUT = 'site/build-data'; shutil.rmtree(OUT, ignore_errors=True); os.makedirs(f'{OUT}/debates')
filas = json.load(open('raw/congreso/interv/IntervencionesCronologicamente.json', encoding='utf-8'))
PLENO = [r for r in filas if r['ORGANO'] == 'Pleno' and r['TIPOINTERVENCION'] == 'Intervención' and re.search(r'-PL-[0-9]+', r.get('ENLACEPDF') or '')]

def fecha(s): return dt.datetime.strptime(s, '%d/%m/%Y').date().isoformat()
def temas_de(t): return [k for k, rx in TEMA_RX.items() if re.search(rx, t, re.I)]
def persona(o): return re.sub(r'\s*\([^)]*\)\s*$', '', o).strip()
def codigo(o):
    m = re.search(r'\((G[^)]*\)?)\)?\s*$', o); return m.group(1).rstrip(')') if m else None
def slug(s):
    import unicodedata
    return re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', s.lower()).encode('ascii', 'ignore').decode()).strip('-')
def bando(f):
    """Candidatura a la que se atribuye una intervención: su grupo el día que habló. El Gobierno va aparte."""
    if f.get('CARGOORADOR') and re.search(GOBIERNO_RX, f['CARGOORADOR'], re.I): return 'gobierno'
    c = codigo(f['ORADOR'])
    if c == 'GMx':
        p = persona(f['ORADOR'])
        return next((k for n, k in MIXTO if n in p), None)
    if persona(f['ORADOR']).startswith('Micó Micó'): return 'compromis'
    return GRUPOS.get(c)
def frases(texto):
    return [s.strip() for s in re.split(r'(?<=[.?!])\s+(?=[«¿¡A-ZÁÉÍÓÚÑ])', texto) if s.strip()]

por_doc = collections.defaultdict(list)
for r in PLENO:
    u, _, fr = r['ENLACEPDF'].partition('#')
    r['_pag'] = int(re.search(r'page=(\d+)', fr).group(1)) if 'page=' in fr else 1
    r['_doc'] = os.path.basename(u)
    por_doc[r['_doc']].append(r)

indice = []; declaraciones = []; sesiones = []; personas = collections.defaultdict(list)
stats = collections.Counter()
for doc in sorted(por_doc, key=lambda d: int(re.search(r'PL-(\d+)', d).group(1))):
    txt = f'raw/congreso/ds/{doc[:-4]}.txt'
    if not os.path.exists(txt): stats['docs_sin_texto'] += 1; continue
    raw = open(txt, encoding='utf-8', errors='replace').read()
    pre, ts = turnos(raw)
    fs = sorted(por_doc[doc], key=lambda r: (fecha(r['SESION']), r['_pag'], r.get('INICIOINTERVENCION') or ''))
    # Casar filas con turnos en orden del documento
    i = 0
    for f in fs:
        f['_t'] = None; stats['filas'] += 1
        if f.get('CARGOORADOR') and re.match(r'(Vicep|P)residenta? del Congreso', f['CARGOORADOR']): stats['filas_presidencia'] += 1; continue
        for j in list(range(i, min(i + 80, len(ts)))):
            if ts[j]['pagina'] > f['_pag'] + 3: break
            if ts[j]['pagina'] >= f['_pag'] - 1 and casa(ts[j], f['ORADOR']):
                f['_t'] = j; i = j + 1; stats['filas_casadas'] += 1; break
    # Segunda pasada: el orden de las filas no siempre coincide con el del documento
    usados = {f['_t'] for f in fs if f['_t'] is not None}
    for f in fs:
        if f['_t'] is not None or (f.get('CARGOORADOR') and re.match(r'(Vicep|P)residenta? del Congreso', f['CARGOORADOR'])): continue
        for j, t in enumerate(ts):
            if j not in usados and f['_pag'] - 2 <= t['pagina'] <= f['_pag'] + 4 and casa(t, f['ORADOR']):
                f['_t'] = j; usados.add(j); stats['filas_casadas'] += 1; break
    fs.sort(key=lambda r: (fecha(r['SESION']), r['_t'] if r['_t'] is not None else 10**9, r['_pag']))
    def clave_de(f): return ('/'.join((f.get('NUMEXPEDIENTE') or '').split('/')[:2]), re.sub(r'\s+', ' ', f['OBJETOINICIATIVA']).strip())
    # Debates: filas seguidas con el mismo objeto. Varias iniciativas pueden debatirse a la vez y sus filas
    # se alternan; si un objeto reaparece a poca distancia, todo lo intermedio es el mismo debate.
    bloques = []
    for f in (x for x in fs if x['_t'] is not None):
        c = clave_de(f)
        k = next((i for i in range(len(bloques) - 1, max(-1, len(bloques) - 8), -1) if bloques[i]['clave'] == c or c in bloques[i]['otros']), None)
        if k is None:
            bloques.append(dict(clave=c, otros=[], filas=[f], fecha=fecha(f['SESION'])))
            continue
        for b in bloques[k + 1:]:
            bloques[k]['filas'] += b['filas']
            for x in [b['clave']] + b['otros']:
                if x != bloques[k]['clave'] and x not in bloques[k]['otros']: bloques[k]['otros'].append(x)
        del bloques[k + 1:]
        bloques[k]['filas'].append(f)
    inicios = [min(f['_t'] for f in b['filas']) for b in bloques]
    # Filas sin turno propio: mismo discurso que otra iniciativa acumulada. Se anotan en el debate donde está ese turno.
    for f in (x for x in fs if x['_t'] is None):
        if f.get('CARGOORADOR') and re.match(r'(Vicep|P)residenta? del Congreso', f['CARGOORADOR']): continue
        t = next((j for j, x in enumerate(ts) if f['_pag'] - 2 <= x['pagina'] <= f['_pag'] + 4 and casa(x, f['ORADOR'])), None)
        k = next((i for i in range(len(inicios) - 1, -1, -1) if t is not None and inicios[i] <= t), None)
        if k is None: stats['filas_sin_turno'] += 1; continue
        c = clave_de(f)
        if c != bloques[k]['clave'] and c not in bloques[k]['otros']: bloques[k]['otros'].append(c)
        stats['filas_acumuladas'] += 1
    n = 0; por_turno = {f['_t']: f for f in fs if f['_t'] is not None}
    num = int(re.search(r'PL-(\d+)', doc).group(1))
    ses = dict(num=num, doc=doc, url=f'https://www.congreso.es/public_oficiales/L15/CONG/DS/PL/{doc}', fecha=min(b['fecha'] for b in bloques), debates=[])
    for pos, (b, ini) in enumerate(zip(bloques, inicios)):
        sig = inicios[pos + 1] if pos + 1 < len(inicios) else len(ts)
        n += 1; did = f'{num}-{n}'
        titulo = b['clave'][1]
        otros = [c[1] for c in b['otros'] if c[1] != titulo]
        tm = temas_de(' '.join([titulo] + otros))
        expedientes = sorted({c[0] for c in [b['clave']] + b['otros'] if c[0]})
        salida = []; meta0 = b['filas'][0]
        for j in range(ini, sig):
            t = ts[j]; f = por_turno.get(j)
            pres = es_presidencia(t)
            inferido = False
            if not f and not pres:
                # Réplicas del mismo orador: los metadatos no siempre tienen fila propia. Se toma su grupo de otra fila cercana.
                f = next((x for x in fs if abs(x['_pag'] - t['pagina']) <= 8 and casa(t, x['ORADOR'])), None)
                inferido = f is not None
            d = dict(rotulo=t['rotulo'], detalle=t['detalle'], pagina=t['pagina'], parrafos=t['parrafos'], presidencia=pres)
            if f:
                d.update(orador=persona(f['ORADOR']), grupo=codigo(f['ORADOR']), cargo=f.get('CARGOORADOR'), bando=bando(f), video=None if inferido else f.get('ENLACEDIFERIDO'), inicio=None if inferido else f.get('INICIOINTERVENCION'))
                texto = ' '.join(t['parrafos'])
                # Posición declarada: primera frase con sentido de voto; si no hay, primera propuesta.
                sel = None; tipo = None
                fr = frases(texto)
                fr = [x for x in fr if not x.startswith(('¿', '¡')) and not x.endswith('?')]
                for s in fr:
                    if 40 <= len(s) <= 420 and re.search(VOTO_RX, s, re.I): sel, tipo = s, 'voto'; break
                if not sel:
                    for s in fr:
                        if 50 <= len(s) <= 420 and re.search(PROPUESTA_RX, s, re.I): sel, tipo = s, 'propuesta'; break
                if sel:
                    assert norm(sel) in norm(texto)
                    d['destacada'] = sel
                    if d.get('bando'):
                        declaraciones.append(dict(cita=sel, tipo=tipo, bando=d['bando'], orador=d['orador'], grupo=d['grupo'], fecha=b['fecha'], debate=did, titulo=titulo, temas=tm, pagina=t['pagina'], turno=len(salida), doc=doc))
                        stats['declaraciones'] += 1
                personas[d['orador']].append(dict(debate=did, titulo=titulo, fecha=b['fecha'], turno=len(salida), pagina=t['pagina'], cargo=f.get('CARGOORADOR'), grupo=d['grupo'], destacada=d.get('destacada'), temas=tm, caracteres=len(texto)))
            salida.append(d)
        meta = dict(id=did, num=num, fecha=b['fecha'], titulo=titulo, tipo=meta0.get('TIPOINICIATIVA'), autor=meta0.get('AUTOR'), expediente=b['clave'][0] or None, expedientes=expedientes, otros=otros, temas=tm, doc=doc, pagina=salida[0]['pagina'], turnos=len(salida), oradores=sum(1 for x in salida if x.get('orador')))
        json.dump(dict(meta, intervenciones=salida), open(f'{OUT}/debates/{did}.json', 'w', encoding='utf-8'), ensure_ascii=False)
        indice.append(meta); ses['debates'].append(did); stats['debates'] += 1
        stats['caracteres_publicados'] += sum(sum(len(p) for p in x['parrafos']) for x in salida)
    stats['caracteres_doc'] += sum(sum(len(p) for p in t['parrafos']) for t in ts)
    sesiones.append(ses)

# --- Todas las votaciones ---
idx = json.load(open('data/votaciones_todas.json', encoding='utf-8'))
por_exp = collections.defaultdict(list)
for m in indice:
    for e in m['expedientes']: por_exp[e].append(m['id'])
votos = []; faltan = 0; expediente_a = 0; dips = diputados()
for v in idx:
    if v['si'] is None: continue
    rec = {k: v.get(k) for k in ('fecha', 'titulo', 'expediente', 'si', 'no', 'abst', 'diario')}
    rec['temas'] = temas_de(v['titulo']); rec['grupos'] = None; rec['json'] = None
    if v['json']:
        rec['json'] = 'https://www.congreso.es' + v['json']
        fn = 'raw/congreso/votos/' + re.sub(r'\W+', '_', v['json'].split('/opendata/votaciones/')[-1])
        if os.path.exists(fn):
            d = json.load(open(fn, encoding='utf-8'))
            if (d['totales']['afavor'], d['totales']['enContra']) != (v['si'], v['no']): stats['votos_no_cuadran'] += 1
            g = collections.defaultdict(collections.Counter)
            for x in d['votaciones']:
                k = GRUPOS.get(x['grupo'])
                if x['grupo'] == 'GMx': k = next((c for n, c in MIXTO if n in x['diputado']), None)
                if x['diputado'].startswith('Micó Micó'): k = 'compromis'
                if k: g[k][x['voto']] += 1
            rec['grupos'] = {k: dict(c) for k, c in g.items()}
        else: faltan += 1
    else:
        rec['grupos'], motivo = grupos_de(v, dips)
        if rec['grupos']: rec['origen_grupos'] = 'diario'; stats['llamamientos_contados'] += 1
        elif v.get('diario'): print('Sin voto por grupo:', v['fecha'], v['titulo'][:70], '|', motivo[:120])
    deb = por_exp.get(v.get('expediente') or '', [])
    rec['debates'] = deb
    if deb: expediente_a += 1
    rec['resultado'] = 'Salió adelante' if v['si'] > v['no'] else 'No salió adelante'
    votos.append(rec)

pers = []
for nombre, its in personas.items():
    its.sort(key=lambda x: x['fecha'], reverse=True)
    pers.append(dict(nombre=nombre, slug=slug(nombre), n=len(its), cargo=next((x['cargo'] for x in its if x['cargo']), None), grupo=its[0]['grupo'], intervenciones=its))
pers.sort(key=lambda p: p['nombre'])
for nombre, datos in dict(debates=indice, declaraciones=declaraciones, sesiones=sesiones, votos_todos=votos, personas=pers).items():
    json.dump(datos, open(f'{OUT}/{nombre}.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(dict(stats))
print('filas acumuladas', stats['filas_acumuladas'], 'sin turno', stats['filas_sin_turno'], 'debates', len(indice), 'con varias iniciativas', sum(1 for m in indice if m['otros']))
print('filas casables', stats['filas'] - stats['filas_presidencia'], 'casadas', stats['filas_casadas'], f"= {stats['filas_casadas'] / max(1, stats['filas'] - stats['filas_presidencia']):.1%}")
print('texto publicado respecto a turnos del documento', f"{stats['caracteres_publicados'] / max(1, stats['caracteres_doc']):.1%}")
print('votos', len(votos), 'sin descargar aún', faltan, 'unidos a debate por expediente', expediente_a)
print('declaraciones', len(declaraciones), collections.Counter(d['tipo'] for d in declaraciones), collections.Counter(d['bando'] for d in declaraciones).most_common(14))
print('debates por tema', {k: sum(1 for m in indice if k in m['temas']) for k in TEMA_RX}, 'sin tema', sum(1 for m in indice if not m['temas']))
print('votos por tema', {k: sum(1 for m in votos if k in m['temas']) for k in TEMA_RX})
print('personas', len(pers))
