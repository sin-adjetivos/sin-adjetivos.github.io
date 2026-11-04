"""Frases candidatas para sustituir citas poco informativas: priman las que dicen el voto o el motivo, en castellano. Solo ayuda a elegir; la decisión es manual. Uso: candidatas.py archivo_con_lineas_expediente_grupo [n]"""
import json, re, sys
sys.path.insert(0, 'scripts')
sys.stdout.reconfigure(encoding='utf-8')
from fuente_fichas import FICHAS
from fuente_fichas_2 import FICHAS_2
from fuente_fichas_3 import FICHAS_3
from fuente_fichas_4 import FICHAS_4
OTRA_LENGUA = r"\b(els|les|amb|aquest\w*|aquesta|però|perquè|hem|vostès|senyor\w*|també|així|unha|nós|mais|polo|pola|deste|desta|ao|xa|non|moi|tamén|porque non|están a|gràcies|grazas)\b"
FORMULA = r'^(Señor|Gracias|Muchas gracias|Buen|Hoy (debatimos|hablamos|discutimos|traemos)|Debatimos|Presidenta|Presidente)'
n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
pedidos = [l.split() for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
fichas = {f['expediente']: f for f in FICHAS + FICHAS_2 + FICHAS_3 + FICHAS_4}
ultimo = None
for exp, g in pedidos:
    f = fichas[exp]
    d = json.load(open(f"site/build-data/debates/{f['debate']}.json", encoding='utf-8'))
    temas = {w for w in re.findall(r'\w{5,}', (f['titulo'] + ' ' + ' '.join(f['que_es'])).lower())}
    filas = []
    for t in d['intervenciones']:
        if t['presidencia'] or t.get('bando') != g: continue
        for s in re.split(r'(?<=[.?!])\s+(?=[«¿¡A-ZÁÉÍÓÚÑ])', ' '.join(t['parrafos'])):
            if not 70 <= len(s) <= 260: continue
            if len(re.findall(OTRA_LENGUA, s, re.I)) >= 2: continue
            p = 0
            if re.search(r'\b(vot\w+|apoy\w+|a favor|en contra|abstend\w+|abstención|rechaz\w+|respald\w+)\b', s, re.I): p += 4
            if re.search(r'\b(porque|por eso|por ello|por tanto|ya que|por lo tanto)\b', s, re.I): p += 2
            p += min(3, len(temas & set(re.findall(r'\w{5,}', s.lower()))))
            if re.search(r'\d', s): p += 1
            if re.search(FORMULA, s): p -= 3
            if re.search(r'\(|―|—', s): p -= 2
            filas.append((p, s))
    if exp != ultimo:
        print(f"\n# {exp} {f['titulo']}"); ultimo = exp
    print(f"[{g}]")
    for p, s in sorted(filas, key=lambda x: -x[0])[:n]: print(f"  {s}")
    if not filas: print('  (sin frases en castellano)')
