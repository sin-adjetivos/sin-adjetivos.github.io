"""Voto por grupo en las votaciones por llamamiento. Los datos abiertos del Congreso solo dan el total, pero el Diario de Sesiones
publica la lista nominal de quién dijo sí, no o se abstuvo. Se cuenta esa lista y solo se acepta si coincide con el total oficial."""
import collections, glob, json, os, re, sys, unicodedata
sys.path.insert(0, 'scripts')
from reglas import GRUPOS, MIXTO

def llano(s):
    s = unicodedata.normalize('NFKC', s).replace('‌', '')
    s = re.sub(r'[‐‑‒–]', '-', s)
    s = re.sub(r'\bM\s*\.?\s*[ªa]\.?\s+', 'mª ', s)
    return re.sub(r'\s+', ' ', s).lower()

def diputados():
    """Grupo de cada diputado en cada fecha, según las votaciones con datos abiertos. Quien no tiene candidatura propia en el Mixto queda sin grupo, pero cuenta para el total."""
    out = collections.defaultdict(list)
    for fn in sorted(glob.glob('raw/congreso/votos/Leg15_*_json')):
        d = json.load(open(fn, encoding='utf-8'))
        fecha = re.search(r'_(\d{8})_Votacion', fn).group(1)
        for x in d['votaciones']:
            k = GRUPOS.get(x['grupo'])
            if x['grupo'] == 'GMx': k = next((c for n, c in MIXTO if n in x['diputado']), None)
            if x['diputado'].startswith('Micó Micó'): k = 'compromis'
            if not out[x['diputado']] or out[x['diputado']][-1][1] != k: out[x['diputado']].append((fecha, k))
    return out

def grupo_en(tramos, fecha):
    k = tramos[0][1]
    for f, g in tramos:
        if f <= fecha: k = g
    return k

CAB = re.compile(r'^(cve: DSCD\S+|DIARIO DE SESIONES DEL CONGRESO DE LOS DIPUTADOS|PLENO Y DIPUTACI[OÓ]N PERMANENTE|N[uú]m\. \d+|\d+\s+de\s+\w+\s+de\s+\d{4}|P[aá]g\. \d+|\d+\s+\S.*)$', re.I)
MARCA = re.compile(r'^(Señoras y señores diputados|Miembros del Gobierno|Miembros de la Mesa|Votos? nulos?)\b.*', re.I)
FIN = re.compile(r'La señora PRESIDENTA|escrutinio|recuento', re.I)

def listas(v):
    """Devuelve {'Sí': texto, 'No': texto, 'Abstención': texto} con los nombres que da el Diario para esa votación, o None."""
    m = re.search(r'(DSCD-15-PL-\d+)\.PDF\?*#page=(\d+)', v.get('diario') or '')
    if not m: return None
    fn = f'raw/congreso/ds/{m.group(1)}.txt'
    if not os.path.exists(fn): return None
    texto = '\n'.join(open(fn, encoding='utf-8', errors='replace').read().split('\f')[int(m.group(2)) - 1:])
    i = re.search(r'se procede al llamamiento', texto)
    if not i: return None
    out = collections.defaultdict(str); actual = None
    for lin in texto[i.end():].split('\n')[1:]:
        lin = lin.strip()
        if not lin or CAB.match(lin): continue
        if FIN.search(lin) and not MARCA.match(lin): break
        if MARCA.match(lin):
            actual = 'Sí' if '«sí»' in lin else 'No' if '«no»' in lin else 'Abstención' if re.search(r'abst', lin, re.I) else None
            continue
        if actual: out[actual] += ' ' + lin
    return out

def grupos_de(v, dips):
    """Reparto por grupo si la lista cuadra con el total oficial; si no, None y el motivo."""
    ls = listas(v)
    if not ls: return None, 'sin lista en el Diario'
    fecha = v['fecha'].replace('-', ''); g = collections.defaultdict(collections.Counter); cuenta = collections.Counter(); sin = []
    orden = sorted(dips, key=len, reverse=True)
    vistos = set(); restos = {}
    for voto, texto in ls.items():
        t = llano(texto)
        for nombre in orden:
            n = llano(nombre)
            if n in t:
                t = t.replace(n, ' ', 1); cuenta[voto] += 1; vistos.add(nombre)
                k = grupo_en(dips[nombre], fecha)
                if k: g[k][voto] += 1
        restos[voto] = t
    # Segunda pasada: el Diario escribe algún nombre de otra forma (sin coma, «María» por «Mª»). Se busca por apellidos, y el total oficial sigue siendo la prueba.
    for voto, t in restos.items():
        for nombre in orden:
            ap = llano(nombre.split(',')[0])
            if nombre not in vistos and ap in t:
                t = t.replace(ap, ' ', 1); cuenta[voto] += 1; vistos.add(nombre)
                k = grupo_en(dips[nombre], fecha)
                if k: g[k][voto] += 1
        resto = re.sub(r'[\s.,;:()«»]+', ' ', t).strip()
        if resto: sin.append(resto[:120])
    if (cuenta['Sí'], cuenta['No'], cuenta['Abstención']) != (v['si'], v['no'], v['abst']):
        return None, f"no cuadra: lista {dict(cuenta)} oficial {v['si']}/{v['no']}/{v['abst']} sobra {sin}"
    return {k: dict(c) for k, c in g.items()}, None

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    dips = diputados(); print(len(dips), 'diputados')
    for v in json.load(open('site/build-data/votos_todos.json', encoding='utf-8')):
        if v.get('json') or (v.get('expediente') or '').startswith('240'): continue
        g, err = grupos_de(v, dips)
        print(v['fecha'], v['si'], v['no'], v['abst'], v['titulo'][:50], '\n   ', err or g)
