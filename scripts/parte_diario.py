"""Parte diario: qué mirar hoy para escribir noticias. Sin IA: cuenta titulares y compara con lo publicado. Lo escribe en la salida estándar, en Markdown.
Lo publica como aviso de GitHub el paso «Preparar el parte diario» de actualizar.yml. Son datos públicos: no leer aquí los borradores."""
import datetime as dt, json, os, random, re, sys

ALMACEN = 'data/noticias.json'; GRUPOS = 'site/src/data/actualidad.json'; PROPIAS = 'site/src/data/noticias_propias.json'
HORAS = 48; MIN_MEDIOS = 4; MAX_TEMAS = 10; MAX_PROPUESTAS = 5
# Sin re.I: «Podemos» y «podemos» no son lo mismo. Mismo patrón para todas: nombre del partido y de quien encabeza su lista.
PARTIDOS = {
 'pp': ('PP', r'\bPP\b|Feijóo'), 'psoe': ('PSOE', r'\bPSOE\b|Pedro Sánchez|\bSánchez\b'), 'vox': ('Vox', r'\bVox\b|Abascal'),
 'frente-amplio': ('Frente Amplio', r'Frente Amplio|Colau'), 'podemos': ('Podemos', r'\bPodemos\b|Irene Montero'), 'compromis': ('Compromís', r'Compromís|Àgueda Micó'),
 'unidad-pueblo-canario': ('Unidad del Pueblo Canario', r'Unidad del Pueblo Canario'), 'ara-mes': ('Ara Més', r'Ara Més|Carme Gomila'), 'erc': ('ERC', r'\bERC\b|Esquerra|Rufián'),
 'junts': ('Junts', r'\bJunts\b|Nogueras'), 'eh-bildu': ('EH Bildu', r'\bBildu\b|Matute'), 'pnv': ('PNV', r'\bPNV\b|Maribel Vaquero'),
 'bng': ('BNG', r'\bBNG\b|Néstor Rego'), 'coalicion-canaria': ('Coalición Canaria', r'Coalición Canaria|Cristina Valido'),
}
PROPUESTA = re.compile(r'\b(promet\w+|propon\w+|propuesta\w*|presentará\w*|plan(es)? (de|para)|medidas?|bajará\w*|subirá\w*|eliminará\w*|derogará\w*|suprimirá\w*|programa electoral|si (gobierna|gana|llega)|contrato con españa)\b', re.I)
PROGRAMA = re.compile(r'programa (electoral|de gobierno)', re.I)
FECHAS = [
 ('2026-11-11', 'Huelga general convocada. Actualizar la noticia de la huelga.'),
 ('2026-11-12', 'La Diputación Permanente vota los decretos 28 y 29/2026. Añadir el resultado a las dos fichas de vivienda de octubre.'),
 ('2026-11-13', 'Empieza la campaña. Vigilar programas y debates.'),
 ('2026-11-19', 'Acaba el plazo para pedir el voto por correo.'),
 ('2026-11-24', 'Desde hoy y hasta el 28 está prohibido publicar encuestas. Actualidad enlaza titulares.'),
 ('2026-11-25', 'Acaba el plazo para enviar el voto por correo.'),
 ('2026-11-28', 'Jornada de reflexión. No publicar nada nuevo, salvo correcciones.'),
 ('2026-11-29', 'Elecciones.'),
]

def limpio(s):
    """Un titular no debe avisar a nadie en GitHub ni enlazar a otro aviso."""
    return s.replace('@', '@​').replace('#', '#​').replace('[', '(').replace(']', ')')

def enlace(t):
    return f"[{limpio(t['titulo'])}]({t['url']})"

def explicada(g, propias):
    return next((n for n in propias if set(g['comunes']) & set(n['claves'])), None)

def temas_sin_noticia(act, propias):
    sueltos = [g for g in act['grupos'] if not explicada(g, propias)]
    fuertes = [g for g in sueltos if g['medios'] >= MIN_MEDIOS][:MAX_TEMAS]
    out = ['## Temas sin noticia propia', '', f'Publicados por {MIN_MEDIOS} medios o más, de más a menos. La guía permite saltar guías prácticas y sucesos sin interés público.', '']
    out += [f"- **{g['medios']} medios:** {enlace(g['titulares'][0])}" for g in fuertes] or ['- Ninguno.']
    return out

def novedades(act, propias):
    out = ['## Noticias nuestras con algo nuevo', '', 'Titulares posteriores al último cambio. Pueden no aportar nada: hay que leerlos.', '']
    filas = []
    for n in propias:
        ultima = (n['cambios'][-1]['fecha'] if n['cambios'] else n['fecha'])
        grupos = [g for g in act['grupos'] if explicada(g, [n]) and g['hasta'][:10] > ultima]
        if grupos:
            filas.append(f"- **{limpio(n['titulo'])}** ({n['fecha']}): " + '; '.join(enlace(g['titulares'][0]) for g in grupos[:3]))
    return out + (filas or ['- Nada todavía.'])

def propuestas(titulares, propias, hoy):
    # Primero la candidatura que lleva más tiempo sin propuesta. Los empates, al azar pero fijos para ese día, para que ninguna vaya siempre delante.
    ultima = {}
    for n in propias:
        if n.get('tipo') == 'propuesta': ultima[n['partido']] = max(n['fecha'], ultima.get(n['partido'], ''))
    orden = sorted(PARTIDOS, key=lambda c: random.Random(hoy + c).random())
    orden.sort(key=lambda c: ultima.get(c, ''))
    out = ['## Hueco de propuestas', '', f'Titulares de las últimas {HORAS} horas con una palabra de propuesta y el nombre del partido o de quien encabeza su lista. Es un filtro automático y se cuela de todo. Se empieza por la primera candidatura de la lista que tenga una propuesta real.', '']
    filas = []
    for c in orden:
        sigla, rx = PARTIDOS[c]
        suyos = {t['url']: t for t in titulares if PROPUESTA.search(t['titulo']) and re.search(rx, t['titulo'])}
        if suyos:
            cuando = f"última el {ultima[c]}" if c in ultima else 'ninguna todavía'
            filas.append(f'- **{sigla}** ({cuando})')
            filas += [f"  - {t['medio']}: {enlace(t)}" for t in list(suyos.values())[:MAX_PROPUESTAS]]
    sin = [PARTIDOS[c][0] for c in orden if not any(PROPUESTA.search(t['titulo']) and re.search(PARTIDOS[c][1], t['titulo']) for t in titulares)]
    if sin: filas.append(f"- Sin titulares que pasen el filtro: {', '.join(sin)}.")
    return out + filas

def programas(titulares):
    filas = {t['url']: t for t in titulares if PROGRAMA.search(t['titulo'])}
    return ['## Programas', ''] + ([f"- {t['medio']}: {enlace(t)}" for t in filas.values()] or ['- Ningún titular menciona un programa electoral.'])

def fechas(hoy):
    limite = (dt.date.fromisoformat(hoy) + dt.timedelta(days=3)).isoformat()
    cerca = [f'- **{d}:** {t}' for d, t in FECHAS if hoy <= d <= limite]
    return ['## Fechas de los próximos tres días', ''] + (cerca or ['- Ninguna del calendario.'])

def lectores(act):
    fallan = [k for k, v in act['estado'].items() if isinstance(v, str)]
    return [f"Medios que no se han podido leer: {', '.join(fallan)}."] if fallan else []

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ahora = dt.datetime.now().astimezone()   # Hora local: el paso de actualizar.yml define TZ=Europe/Madrid.
    hoy = ahora.date().isoformat()
    act = json.load(open(GRUPOS, encoding='utf-8'))
    propias = [n for n in json.load(open(PROPIAS, encoding='utf-8')) if not n.get('borrador')]
    desde = (ahora.astimezone(dt.timezone.utc) - dt.timedelta(hours=HORAS)).isoformat()
    titulares = [t for t in json.load(open(ALMACEN, encoding='utf-8')) if (t['fecha'] or '') >= desde] if os.path.exists(ALMACEN) else []
    ultima = max((n['fecha'] for n in propias), default='ninguna')
    partes = [
     [f"Para escribir, abre Claude Code y escribe `/noticia`. Última noticia publicada: {ultima}. Titulares leídos en las últimas {HORAS} horas: {len(titulares)}.", *lectores(act)],
     fechas(hoy), temas_sin_noticia(act, propias), novedades(act, propias), propuestas(titulares, propias, hoy), programas(titulares),
    ]
    print('\n\n'.join('\n'.join(p) for p in partes))

if __name__ == '__main__':
    main()
