"""Separa un Diario de Sesiones en turnos de palabra sin alterar el texto y los une con los metadatos oficiales."""
import re, unicodedata

CABECERA = re.compile(r'^(DIARIO DE SESIONES DEL CONGRESO DE LOS DIPUTADOS|PLENO Y DIPUTACIÓN PERMANENTE|COMISIONES|Núm\.? \d+.*|\d{1,2} de [a-záéíóú]+ de 20\d\d(\s+Pág\. ?\d+)?|Pág\. ?\d+|cve: DSCD[-\w]*|Verificable en .*|BOLETÍN OFICIAL.*)$')
TURNO = re.compile(r"^(?:El|La) (?:señor|señora|señor[ae]s?) ([A-ZÁÉÍÓÚÜÑÀÈÒÇÏ][A-ZÁÉÍÓÚÜÑÀÈÒÇÏ'’·\-, .]+?)(?: \(([^)]{2,160})\))?(?:,? desde los escaños[^:]{0,40})?: ?(.*)$")
INICIO = re.compile(r'^Se (abre|reanuda) la sesión', re.I)

def llano(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().upper()
    return re.sub(r'[^A-Z ]+', ' ', s)

def apellidos(orador):
    """'Sánchez Pérez-Castejón, Pedro' -> tokens de apellidos."""
    a = orador.split(',')[0]
    return [t for t in llano(a).split() if t not in ('DE', 'DEL', 'LA', 'LAS', 'LOS', 'I', 'Y', 'D')]

def cuerpo(raw):
    """Devuelve [(pagina, linea)] sin cabeceras ni pies. Las páginas son las del PDF."""
    out = []
    for i, pg in enumerate(raw.split('\f'), 1):
        pg = pg.replace('\u202f', ' ').replace('\u00a0', ' ')
        pg = re.sub(r'(\w)-\n(?=[a-záéíóúñü])', r'\1', pg)
        for ln in pg.split('\n'):
            l = ln.strip()
            if not l or CABECERA.match(l): continue
            out.append((i, l))
    return out

def turnos(raw):
    """Lista de turnos en orden del documento; el texto anterior al primero queda en 'preambulo'."""
    res = []; pre = []; cur = None
    for pag, l in cuerpo(raw):
        m = TURNO.match(l)
        if m and len(m.group(1)) >= 3:
            cur = dict(rotulo=m.group(1).strip(' ,'), detalle=m.group(2), pagina=pag, parrafos=[m.group(3)] if m.group(3) else [])
            res.append(cur); continue
        if cur is None: pre.append((pag, l))
        elif cur['parrafos'] and re.match(r'^[a-záéíóúñü(]', l) and not re.search(r'[.?!:»)]$', cur['parrafos'][-1]):
            cur['parrafos'][-1] += ' ' + l   # frase partida por un salto de página
        else: cur['parrafos'].append(l)
    return pre, res

def es_presidencia(t):
    return bool(re.match(r'^(VICE)?PRESIDENT[AE]', t['rotulo'])) and not re.search(r'GOBIERNO', t['rotulo'])

def casa(t, orador):
    """¿El turno pertenece a este orador? Compara apellidos con el rótulo y con el paréntesis de cargo."""
    ap = apellidos(orador)
    if not ap: return False
    txt = llano(t['rotulo'] + ' ' + (t['detalle'] or '')).split()
    return all(x in txt for x in ap[:2]) if len(ap) > 1 else ap[0] in txt

def unir(raw, filas):
    """Asigna turnos a las filas de metadatos de un documento, en orden. Devuelve pre, turnos y número de filas casadas."""
    pre, ts = turnos(raw)
    i = 0; casadas = 0
    for f in filas:
        f['_turno'] = None
        # busca hacia delante, sin saltar más de lo razonable en páginas
        for j in range(i, min(i + 60, len(ts))):
            if ts[j]['pagina'] > f['_pag'] + 2: break
            if ts[j]['pagina'] >= f['_pag'] - 1 and casa(ts[j], f['ORADOR']):
                f['_turno'] = j; i = j + 1; casadas += 1; break
    return pre, ts, casadas
