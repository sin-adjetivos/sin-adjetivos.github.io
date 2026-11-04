"""Vuelca lo esencial de un debate para redactar una ficha: quién presenta y qué dice cada grupo. Uso: leer_debate.py ID [car_por_turno]"""
import json, re, sys
def vuelca(did, n=900):
    d = json.load(open(f'site/build-data/debates/{did}.json', encoding='utf-8'))
    print(f"\n=== {did} {d['fecha']} | {d['titulo'][:170]}")
    if d.get('otros'): print('   junto con:', [o[:90] for o in d['otros']])
    vistos = {}
    for i, t in enumerate(d['intervenciones']):
        if t['presidencia'] or not t.get('orador'): continue
        clave = t.get('bando') or t['orador']
        texto = ' '.join(t['parrafos'])
        if clave in vistos and len(texto) < 400: continue
        if vistos.get(clave, 0) >= 1: continue     # primera intervención larga de cada grupo
        if len(texto) < 300: continue
        vistos[clave] = 1
        limite = n * 2 if not vistos or clave == 'gobierno' else n
        cab = texto[:limite // 2]; col = texto[-limite // 2:] if len(texto) > limite else ''
        print(f"\n[{clave}] {t['orador']} t{i} p{t['pagina']} ({len(texto)} car.)\n{cab}" + (f"\n[...]\n{col}" if col else ''))
if __name__ == '__main__':
    n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 900
    for did in sys.argv[1].split(','): vuelca(did, n)
