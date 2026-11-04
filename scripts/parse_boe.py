"""Convierte el XML de BOE-A-2026-23103 (candidaturas proclamadas) en datos por circunscripción."""
import re, json, html
x = open('raw/boe/candidaturas.xml', encoding='utf-8').read()
out = {}; prov = cam = cand = None; sup = False
for cls, inner in re.findall(r'<p class="([^"]+)"[^>]*>(.*?)</p>', x, re.S):
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', inner))).strip()
    if cls == 'centro_negrita' and t.startswith('JUNTA ELECTORAL'):
        prov = re.sub(r'^JUNTA ELECTORAL (PROVINCIAL )?(DE |DEL )?', '', t).strip(); out.setdefault(prov, {'congreso': [], 'senado': []}); cam = cand = None
    elif cls == 'centro_cursiva':
        cam = 'congreso' if 'CONGRESO' in t.upper() else 'senado' if 'SENADO' in t.upper() else cam; cand = None
    elif cls == 'centro_redonda' and prov and cam:
        m = re.match(r'^(\d+)\.\s*(.+)$', t)
        if m:
            b = m.group(2).rstrip('.'); s = re.search(r'\(([^()]+)\)\s*$', b)
            cand = {'orden': int(m.group(1)), 'nombre': b, 'sigla': s.group(1) if s else None, 'lista': [], 'suplentes': []}
            out[prov][cam].append(cand); sup = False
        elif cand:
            cand['nombre'] += ' ' + t
    elif cand is not None:
        if t.startswith('No proclamada'): cand['no_proclamada'] = True; continue
        m = re.match(r'^Suplente \d+:\s*(.+)$', t)
        if m: cand['suplentes'].append(m.group(1).rstrip('.')); continue
        if re.match(r'^Suplentes?', t, re.I): sup = True; continue
        m = re.match(r'^\d+\.\s*(.+)$', t)
        if m: (cand['suplentes'] if sup else cand['lista']).append(m.group(1).rstrip('.'))
json.dump(out, open('data/candidaturas_boe.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
nc = sum(len(v['congreso']) for v in out.values()); ns = sum(len(v['senado']) for v in out.values())
np_ = [(p, k, c['nombre'][:40]) for p, v in out.items() for k in v for c in v[k] if c.get('no_proclamada')]
print(len(out), 'juntas;', nc, 'Congreso;', ns, 'Senado;', nc + ns, 'listadas; no proclamadas:', len(np_), np_[:6])
print('sin lista ni marca:', [(p, k, c['nombre'][:30]) for p, v in out.items() for k in v for c in v[k] if not c['lista'] and not c.get('no_proclamada')][:8])
print('candidatos Congreso', sum(len(c['lista']) for v in out.values() for c in v['congreso']), 'Senado', sum(len(c['lista']) for v in out.values() for c in v['senado']))
print(out['ALBACETE']['senado'][2]['lista'][:2])
