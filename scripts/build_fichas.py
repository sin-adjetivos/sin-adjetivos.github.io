"""Comprueba y genera las fichas. Falla si una cita no es literal, si no la dijo esa candidatura o si la redacción usa adjetivos valorativos."""
import json, re, sys, unicodedata
sys.path.insert(0, 'scripts')
from lib_pdf import norm
from fuente_fichas import FICHAS
from fuente_fichas_2 import FICHAS_2
from fuente_fichas_3 import FICHAS_3
from fuente_fichas_4 import FICHAS_4
FICHAS = FICHAS + FICHAS_2 + FICHAS_3 + FICHAS_4
from seleccion_fichas import elegir

VALORATIVAS = r'\b(polémic\w*|histórico|histórica|importante\w*|grave\w*|escandal\w*|enorme\w*|radical\w*|extremo|extrema|ultra\w*|duro|dura|valiente\w*|vergonz\w*|polarizad\w*|controvertid\w*|ambicios\w*|necesari\w*|buen\w*|mal[oa]s?)\b'
errores = []; salida = []
todos = json.load(open('site/build-data/votos_todos.json', encoding='utf-8'))
sel = elegir(20)
elegidos = {(t, x.get('expediente')) for t, xs in sel.items() for x in xs}
for f in FICHAS:
    d = json.load(open(f"site/build-data/debates/{f['debate']}.json", encoding='utf-8'))
    if (f['tema'], f['expediente']) not in elegidos:
        errores.append(f"{f['expediente']} no sale de las reglas de selección en {f['tema']}")
    vs = [v for v in todos if v.get('expediente') == f['expediente'] and f['debate'] in (v.get('debates') or []) and not re.search(r'(?<!las )enmiendas? (?!a la totalidad)|^Votaci[oó]n de la enmienda', v['titulo'], re.I)]
    if f.get('voto_fecha'): vs = [x for x in vs if x['fecha'] == f['voto_fecha']]
    if not vs: errores.append(f"{f['expediente']}: sin votación"); continue
    v = next((x for x in vs if re.search(r'^Real Decreto-ley|conjunto|dictamen', x['titulo'], re.I)), vs[0])
    for texto in f['que_es'] + [f['despues'], f['titulo']]:
        m = re.search(VALORATIVAS, texto, re.I)
        if m: errores.append(f"{f['expediente']}: palabra valorativa «{m.group(0)}» en: {texto[:60]}")
    posturas = []
    turnos = [(i, t) for i, t in enumerate(d['intervenciones']) if not t['presidencia']]
    for c, cita in f['citas'].items():
        n = norm(cita); hit = None
        for i, t in turnos:
            if n in norm(' '.join(t['parrafos'])):
                hit = (i, t); break
        if not hit: errores.append(f"{f['expediente']}/{c}: cita no literal: {cita[:70]}"); continue
        i, t = hit
        if t.get('bando') != c:
            errores.append(f"{f['expediente']}/{c}: la dijo {t.get('orador') or t['rotulo']} ({t.get('bando')})"); continue
        posturas.append(dict(candidatura=c, cita=cita, orador=t['orador'].split(', ')[-1] + ' ' + t['orador'].split(', ')[0] if t.get('orador') else t['rotulo'], turno=i, pagina=t['pagina']))
    hablaron = {t.get('bando') for _, t in turnos if t.get('bando') and t.get('bando') != 'gobierno'}
    faltan = sorted(hablaron - set(f['citas']))
    if faltan: print(f"AVISO {f['expediente']}: intervinieron sin cita en la ficha: {faltan}")
    sl = re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', f['titulo'].lower()).encode('ascii', 'ignore').decode()).strip('-')[:70].strip('-')
    salida.append(dict(id=sl, tema=f['tema'], titulo=f['titulo'], que_es=f['que_es'], fuente=f.get('fuente'), despues=f['despues'], despues_fuente=f.get('despues_fuente'), debate=f['debate'], debate_fecha=d['fecha'], num=d['num'], doc=d['doc'], posturas=posturas, fecha=v['fecha'], voto=v))
if errores:
    print('\n'.join(errores)); print(f'{len(errores)} errores. No se generan fichas.'); sys.exit(1)
json.dump(salida, open('site/src/data/fichas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(f'OK: {len(salida)} fichas, {sum(len(f["posturas"]) for f in salida)} citas comprobadas con su autor')
