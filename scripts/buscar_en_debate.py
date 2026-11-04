"""Frases de un debate que coinciden con una expresión, por grupo. Uso: buscar_en_debate.py ID 'regex' [max_por_grupo]"""
import json, re, sys, collections
did, rx = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 2
d = json.load(open(f'site/build-data/debates/{did}.json', encoding='utf-8'))
print(f"=== {did} {d['fecha']} {d['titulo'][:110]}")
c = collections.Counter()
for t in d['intervenciones']:
    if t['presidencia'] or not t.get('orador'): continue
    k = t.get('bando') or t['orador'].split(',')[0]
    for s in re.split(r'(?<=[.?!])\s+(?=[«¿¡A-ZÁÉÍÓÚÑ])', ' '.join(t['parrafos'])):
        if 50 <= len(s) <= 320 and re.search(rx, s, re.I) and c[k] < n:
            c[k] += 1; print(f'[{k}] p{t["pagina"]} {s}')
