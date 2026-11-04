"""Une y comprueba todos los datos del portal. Si una cita no aparece literal en su fuente, falla y no genera nada."""
import sys, re, json, os, unicodedata, shutil
sys.path.insert(0, 'scripts')
from lib_pdf import pages, norm
from fuente_candidaturas import TEMAS, DOCS, CAND
from fuente_posiciones import P, DIJO, V, MANUALES

OUT = 'site/src/data'; PUB = 'site/public/datos/papeleta'
os.makedirs(OUT, exist_ok=True); shutil.rmtree(PUB, ignore_errors=True); os.makedirs(PUB)
errores = []

# --- Citas de programas: localizar la página en el PDF original ---
paginas = {d: [norm(p) for p in pages(f'raw/programas/{d}.pdf')] for d in DOCS}
def localizar(doc, cita):
    n = norm(cita)
    for i, p in enumerate(paginas[doc], 1):
        if n in p: return i
    return None
posiciones = []; n_citas = 0
for tema, por_doc in P.items():
    for doc, cita in por_doc.items():
        pag = localizar(doc, cita); n_citas += 1
        if not pag: errores.append(f'CITA NO LITERAL {tema}/{doc}: {cita[:70]}'); continue
        m = DOCS[doc]
        posiciones.append(dict(tema=tema, candidatura=m['c'], doc=doc, cita=cita, pagina=pag, doc_nombre=m['nombre'], doc_anio=m['anio'],
                               doc_tipo=m['tipo'], url=f"{m['url']}#page={pag}", copia=m.get('copia'), idioma=m.get('idioma')))

# --- Citas del Diario de Sesiones ---
ds = [norm(p) for p in open('raw/congreso/DS210.txt', encoding='utf-8', errors='replace').read().split('\f')]
dijo = []
for tema, b in DIJO.items():
    for c, (orador, cita) in b['citas'].items():
        n = norm(cita); pag = next((i for i, p in enumerate(ds, 1) if n in p), None); n_citas += 1
        if not pag: errores.append(f'DIARIO NO LITERAL {c}: {cita[:70]}'); continue
        dijo.append(dict(tema=tema, candidatura=c, orador=orador, cita=cita, pagina=pag, debate=b['titulo'], url=f"{b['url']}#page={pag}"))

# --- Votaciones: los totales ya se comprobaron contra el JSON del Congreso en fetch_votos.py ---
vs = json.load(open('data/votaciones_sel.json', encoding='utf-8')); votos = []
for v in vs:
    et = [e for e in V if e[0] == v['tema'] and e[1] == v['fecha'] and (not e[2] or e[2] in v['titulo'])]
    if not et: errores.append(f"SIN ETIQUETA {v['tema']} {v['fecha']}"); continue
    v['corto'] = et[0][3]; v['sentido'] = et[0][4]; votos.append(v)
votos += MANUALES
g2c = {c['grupo']: c['id'] for c in CAND if c['grupo']}
for v in votos:
    v['id'] = f"{v['fecha']}-{re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', v['corto'].lower()).encode('ascii', 'ignore').decode())[:50].strip('-')}"
    v['resultado'] = 'Salió adelante' if v['si'] > v['no'] else 'No salió adelante'
    if v.get('grupos'):
        v['por_candidatura'] = {g2c[g]: t for g, t in v['grupos'].items() if g in g2c}
    else:
        v['por_candidatura'] = None
    if v.get('expediente'):
        v['ficha'] = f"https://www.congreso.es/busqueda-de-iniciativas?p_p_id=iniciativas&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_iniciativas_mode=mostrarDetalle&_iniciativas_legislatura=XV&_iniciativas_id={v['expediente']}"
votos.sort(key=lambda v: v['fecha'], reverse=True)

# --- Listas del BOE ---
boe = json.load(open('data/candidaturas_boe.json', encoding='utf-8'))
def slug(s):
    s = unicodedata.normalize('NFKD', s.lower()).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')
def capit(p):
    return ' '.join(w if w in ('de','la','las','el') else w.capitalize() for w in p.lower().split()).replace('Illes Balears', 'Illes Balears').replace('A Coruña', 'A Coruña')
def mapa(c):
    txt = (c['sigla'] or '') + ' | ' + c['nombre']
    for k in CAND:
        if re.search(k['siglas'], c['sigla'] or '', re.I) or re.search(k['siglas'], c['nombre'], re.I): return k['id']
    return None
indice = []; total_c = 0; no_proc = 0
for prov, d in boe.items():
    ls = []
    for c in d['congreso']:
        if c.get('no_proclamada'): no_proc += 1; continue
        total_c += 1
        ls.append(dict(nombre=re.sub(r'\s*\([^()]*(\([^()]*\))?[^()]*\)\s*$', '', c['nombre']).strip(), sigla=c['sigla'], lista=c['lista'], suplentes=c['suplentes'], expediente=mapa(c)))
    s = slug(prov); nombre = capit(prov)
    indice.append(dict(slug=s, nombre=nombre, escanos=max((len(x['lista']) for x in ls), default=0), n=len(ls)))
    json.dump(dict(slug=s, nombre=nombre, candidaturas=ls), open(f'{PUB}/{s}.json', 'w', encoding='utf-8'), ensure_ascii=False)
indice.sort(key=lambda x: unicodedata.normalize('NFKD', x['nombre'].lower()).encode('ascii', 'ignore').decode())

# --- Cabezas de lista contra el BOE ---
cand = []
for k in CAND:
    lst = boe[k['circ']]['congreso']
    hit = next((c for c in lst if c['lista'] and re.search(k['boe'], c['lista'][0], re.I)), None)
    if not hit: errores.append(f"CABEZA NO ESTÁ EN EL BOE {k['id']} {k['circ']}"); continue
    if not re.search(k['siglas'], hit['sigla'] or hit['nombre'], re.I): errores.append(f"SIGLA NO COINCIDE {k['id']}: {hit['sigla']}")
    c = {x: y for x, y in k.items() if x not in ('boe', 'siglas')}
    c['circ_nombre'] = capit(k['circ']); c['circ_slug'] = slug(k['circ']); c['nombre_boe'] = hit['nombre']; c['ant_fuente'] = list(k['ant_fuente'])
    c['entorno'] = k.get('entorno', [])
    cand.append(c)

# --- Casos (base DatosClaros, CC BY 4.0) ---
crudos = json.load(open('raw/datosclaros/casos.json', encoding='utf-8'))
ESTADOS = {'investigacion':'En investigación','juicio_pendiente':'Pendiente de juicio o sentencia','condena_no_firme':'Condena no firme','condena_firme':'Condena firme','archivado':'Archivado','absuelto':'Absolución','prescrito':'Prescrito','indultado':'Indulto o amnistía','otros':'Otros'}
casos = []
for o in crudos:
    a = o['attrs']
    par = re.search(r'data-partidos="\|?([^"]*?)\|?"', a).group(1).split('|'); est = re.search(r'data-estado="([^"]+)"', a).group(1); anio = re.search(r'data-anio="(\d+)"', a).group(1)
    t = o['texto']; m = re.match(r'^\d{4}\s+(.*?)\s+(' + '|'.join(re.escape(x) for x in par) + r')(?:\s+(?:' + '|'.join(re.escape(x) for x in par) + r'))*\s+(' + '|'.join(re.escape(x) for x in ESTADOS.values()) + r')\s+(.*)$', t, re.S)
    if not m: errores.append(f"CASO SIN PARSEAR {o['id']}: {t[:60]}"); continue
    nombre, _, _, resto = m.groups()
    fe = re.search(r'Estado a\s+([0-9-]+)', resto); fecha = fe.group(1) if fe else None
    resto = re.split(r'\s*Estado a\s+[0-9-]+', resto)[0]
    # La lista de personas de la base original no se publica en esta fase.
    corte = re.search(r'(?<=[.)])\s+[A-ZÁÉÍÓÚÑ][^.:]{2,60}\([^)]{2,120}\):\s*(?:investigad|condenad|absuelt|imputad|procesad|acusad|archivad|juzgad|indultad|sobresed|fallecid|prescri|sin )', resto)
    desc = (resto[:corte.start()] if corte else resto).strip()
    links = [dict(url=u, texto=(x.strip() or 'fuente')) for u, x in o['links'] if not re.search(r'datosclaros|creativecommons', u)]
    casos.append(dict(id=o['id'], nombre=nombre, anio=int(anio), partidos=par, estado=est, estado_txt=ESTADOS[est], descripcion=desc, fecha_estado=fecha, fuentes=links))
from revision_casos import REVISION, FECHA as FECHA_REV
for c in casos:
    r = REVISION.get(c['id'])
    if r:
        if r.get('estado'):
            c['estado'] = r['estado']; c['estado_txt'] = ESTADOS[r['estado']]
        if r.get('estado_txt'): c['estado_txt'] = r['estado_txt']
        c['revision'] = dict(fecha=FECHA_REV, resultado=r['resultado'], nota=r['nota'], fuente=list(r['fuente']) if r.get('fuente') else None)
faltan_rev = set(REVISION) - {c['id'] for c in casos}
if faltan_rev: errores.append(f'REVISIÓN DE CASOS INEXISTENTES {faltan_rev}')
casos.sort(key=lambda c: (-c['anio'], c['nombre']))

if errores:
    print('\n'.join(errores)); print(f'\n{len(errores)} errores de {n_citas} citas. No se escribe nada.'); sys.exit(1)

for nombre, datos in dict(temas=[dict(id=a, nombre=b) for a, b in TEMAS], candidaturas=cand, posiciones=posiciones, dijo=dijo, votos=votos, provincias=indice, casos=casos, estados=ESTADOS,
                          resumen=dict(citas=n_citas, votos=len(votos), casos=len(casos), candidaturas_congreso=total_c, no_proclamadas=no_proc, provincias=len(indice), candidatos=sum(len(c['lista']) for v in boe.values() for c in v['congreso'] if not c.get('no_proclamada')))).items():
    json.dump(datos, open(f'{OUT}/{nombre}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(f'OK: {n_citas} citas literales comprobadas, {len(votos)} votaciones, {len(casos)} casos, {total_c} candidaturas al Congreso ({no_proc} no proclamadas excluidas), {len(indice)} circunscripciones.')
sin = {}
for p in os.listdir(PUB):
    for c in json.load(open(f'{PUB}/{p}', encoding='utf-8'))['candidaturas']:
        if not c['expediente']: sin[c['sigla'] or c['nombre'][:24]] = sin.get(c['sigla'] or c['nombre'][:24], 0) + 1
print('Sin expediente (no tenían grupo en el Congreso):', dict(sorted(sin.items(), key=lambda x: -x[1])[:24]))
print('Muestra caso:', casos[0]['nombre'], '|', casos[0]['descripcion'][:200], '|', casos[0]['fecha_estado'], casos[0]['fuentes'][:1])
