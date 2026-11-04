"""Intervenciones de los grupos sin cita en las fichas, para elegir la frase leyendo el discurso. Uso: turnos_grupo.py [expediente] [grupo]"""
import json, sys
sys.path.insert(0, 'scripts')
sys.stdout.reconfigure(encoding='utf-8')
from fuente_fichas import FICHAS
from fuente_fichas_2 import FICHAS_2
from fuente_fichas_3 import FICHAS_3
from fuente_fichas_4 import FICHAS_4
from fuente_fichas_5 import FICHAS_5
exp = sys.argv[1] if len(sys.argv) > 1 else None
grupo = sys.argv[2] if len(sys.argv) > 2 else None
for f in FICHAS + FICHAS_2 + FICHAS_3 + FICHAS_4 + FICHAS_5:
    if exp and f['expediente'] != exp: continue
    d = json.load(open(f"site/build-data/debates/{f['debate']}.json", encoding='utf-8'))
    turnos = [t for t in d['intervenciones'] if not t['presidencia'] and t.get('bando') and t['bando'] != 'gobierno']
    faltan = {grupo} if grupo else {t['bando'] for t in turnos} - set(f['citas'])
    if not faltan: continue
    print(f"\n##### {f['expediente']} | {f['debate']} | {f['titulo']}")
    for g in sorted(faltan):
        for t in (x for x in turnos if x['bando'] == g):
            print(f"\n--- [{g}] {t.get('orador')} p{t['pagina']}{' (inferido)' if t.get('inferido') else ''}\n{' '.join(t['parrafos'])}")
