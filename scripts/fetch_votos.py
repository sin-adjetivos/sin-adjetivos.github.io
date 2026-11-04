"""Descarga el JSON de cada votación elegida y agrega por grupo. Los números salen tal cual del Congreso."""
import sys, json, re, os, time, urllib.request, collections
sys.path.insert(0, 'scripts')
from manifest_votos import M
idx = json.load(open('data/votaciones_indice.json', encoding='utf-8'))
out = []
GR = {'GP':'pp','GS':'psoe','GVOX':'vox','GSUMAR':'sumar','GR':'erc','GJxCAT':'junts','GEH Bildu':'bildu','GV (EAJ-PNV)':'pnv'}
MX = [('Rego Candamil','bng'),('Valido García','cc'),('Belarra','podemos'),('Sánchez Serna','podemos'),('Santana Perera','podemos'),('Velarde','podemos'),('Muñoz Dalda','podemos'),('Micó Micó','compromis')]
for tema, fecha, rx in M:
    hits = [v for v in idx if v['fecha'] == fecha and re.search(rx, v['titulo'], re.I)]
    if not hits: print('NO HAY', tema, fecha, rx); continue
    hits.sort(key=lambda v: (0 if v['json'] else 1))
    v = hits[0]
    rec = dict(tema=tema, fecha=fecha, titulo=v['titulo'], expediente=v['expediente'], si=v['si'], no=v['no'], abst=v['abst'], diario=v['diario'], grupos=None, json=None)
    if v['json']:
        url = 'https://www.congreso.es' + v['json']; rec['json'] = url
        fn = 'raw/congreso/v_' + re.sub(r'\W+', '_', v['json'][-50:])
        if not os.path.exists(fn):
            b = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 SinAdjetivos/0.1'}), timeout=60).read(); open(fn,'wb').write(b); time.sleep(.2)
        d = json.load(open(fn, encoding='utf-8'))
        rec['titulo_json'] = d['informacion'].get('textoExpediente') or d['informacion'].get('titulo')
        t = d['totales']; assert (t['afavor'], t['enContra']) == (v['si'], v['no']), (t, v['si'], v['no'])
        g = collections.defaultdict(collections.Counter); unk = collections.Counter()
        for x in d['votaciones']:
            k = GR.get(x['grupo'])
            if x['diputado'].startswith('Micó Micó'): k = 'compromis'
            if x['grupo'] == 'GMx':
                k = next((c for n, c in MX if n in x['diputado']), None)
                if not k: unk[x['diputado']] += 1; continue
            if not k: unk[x['grupo']] += 1; continue
            g[k][x['voto']] += 1
        rec['grupos'] = {k: dict(c) for k, c in g.items()}; rec['sin_asignar'] = dict(unk)
    out.append(rec)
    print(f"{tema[:6]} {fecha} {v['si']}-{v['no']}-{v['abst']} json={bool(v['json'])} | {v['titulo'][:150]}")
json.dump(out, open('data/votaciones_sel.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out))
print(json.dumps(out[3]['grupos'], ensure_ascii=False)); print(out[3].get('sin_asignar'))
