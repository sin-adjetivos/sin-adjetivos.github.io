"""Descarga los Diarios de Sesiones que cita el conjunto de intervenciones. Reanudable y a ritmo tranquilo."""
import json, os, re, sys, time, subprocess, urllib.request, urllib.error
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) SinAdjetivos/0.2'}
filtro = sys.argv[1] if len(sys.argv) > 1 else 'Pleno'   # 'Pleno' o 'Todos'
d = json.load(open('raw/congreso/interv/IntervencionesCronologicamente.json', encoding='utf-8'))
urls = {}
for r in d:
    if filtro == 'Pleno' and r['ORGANO'] != 'Pleno': continue
    u = (r.get('ENLACEPDF') or '').split('#')[0]
    if u: urls[u] = r['SESION']
os.makedirs('raw/congreso/ds', exist_ok=True)
hechos = fallos = 0
for u in sorted(urls):
    nombre = os.path.basename(u)
    pdf = f'raw/congreso/ds/{nombre}'; txt = pdf[:-4] + '.txt'
    if os.path.exists(txt) and os.path.getsize(txt) > 0:
        hechos += 1; continue
    for intento in range(4):
        try:
            b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
            if b[:5] != b'%PDF-': raise ValueError('no es PDF')
            open(pdf, 'wb').write(b)
            subprocess.run(['pdftotext', '-enc', 'UTF-8', pdf, txt], check=True)
            hechos += 1; print('ok', nombre, len(b), flush=True); break
        except urllib.error.HTTPError as e:
            print('http', e.code, nombre, flush=True)
            if e.code == 404: fallos += 1; break
            time.sleep(10 * (intento + 1))
        except Exception as e:
            print('err', nombre, str(e)[:80], flush=True); time.sleep(10 * (intento + 1))
    else:
        fallos += 1
    time.sleep(0.6)
print('FIN', filtro, 'documentos', len(urls), 'hechos', hechos, 'fallos', fallos, flush=True)
