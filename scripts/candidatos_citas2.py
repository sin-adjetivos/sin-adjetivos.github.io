"""Frases candidatas por tema a nivel de oración (revisión humana)."""
import sys, re, os
sys.path.insert(0, 'scripts')
from lib_pdf import pages
T = {
 'vivienda': r'viviend|alquiler|desahuci|habitatge|lloguer|vivenda|aluguer|etxebizitza',
 'pensiones': r'pensi[oóo]n|pensions|revaloriz|xubilaci|pensió',
 'inmigracion': r'inmigra|migrant|migraci|extranjer[ií]a|regulariz|immigra|estrangeria|asilo\b|expuls',
 'impuestos': r'\birpf\b|impuesto sobre|imposto|impost sobre|fiscal|deflact|\biva\b|impuesto de sociedades|grandes fortunas',
 'empleo': r'salario m[ií]nimo|\bsmi\b|jornada|reforma laboral|salari m[ií]nim|despido|xornada|salario mínimo|acomiadament',
 'sanidad': r'listas? de espera|sanidad p[uú]blica|sistema nacional de salud|atención primaria|llistes d.espera|sanidade pública|salut pública',
 'educacion': r'educaci[oó]n|escuela|\bbecas?\b|universidad p|educació|escola p|ensino|educación',
 'energia': r'nuclear|renovables|cambio clim|emergencia clim|canvi clim|transici[oó]n energ|transició energ|cambio climático|energ[ií]a',
 'defensa': r'\botan\b|gasto en defensa|gasto militar|despesa militar|fuerzas armadas|pol[ií]tica exterior|nato\b|palestin|sahara|gibraltar',
 'territorio': r'autodeterminaci|concierto econ|financiaci[oó]n auton|financiament|plurinacional|federal|referèndum|refer[eé]ndum|lenguas? cooficial|estado auton|estat plurinac|soberan',
 'justicia': r'corrupci|cgpj|consejo general del poder judicial|independencia judicial|puertas giratorias|portes giratòries|corrupció|fiscal[ií]a general|transparencia',
 'igualdad': r'violencia de g[eé]nero|violencia machista|violència masclista|violencia sobre a muller|igualdad salarial|brecha salarial|bretxa salarial|paridad|lgtbi|ley trans|fenda salarial',
}
PROP = r'\b\w+(ar[eé]mos|er[eé]mos|ir[eé]mos|rem|arem|irem|erem|aremos|eremos|iremos)\b|\b(defendemos|proponemos|proposem|defensem|reclam\w+|exig\w+|plantexamos|propomos|defendemos|apostamos|pedimos|demandamos)\b|^(\W*)(garantizar|aprobar|derogar|crear|impulsar|reformar|eliminar|reducir|bajar|subir|establecer|regular|prohibir|ampliar|garantir|impulsar|derrogar|crear|revalorizar)\b'
top = int(os.environ.get('TOP', 2))
for doc in sys.argv[1:]:
    pg = pages(f'raw/programas/{doc}.pdf')
    print(f'\n##### {doc}')
    for tema, rx in T.items():
        c = []
        for i, p in enumerate(pg, 1):
            t = re.sub(r'-\s*\n\s*(?=[a-záéíóúñ])', '', p); t = re.sub(r'\s+', ' ', t)
            for s in re.split(r'(?<=[.;])\s+(?=[A-ZÁÉÍÓÚÑ•·\d])|•|·', t):
                s = s.strip(' •·-')
                if not 70 <= len(s) <= 420: continue
                k = len(re.findall(rx, s, re.I)); pr = bool(re.search(PROP, s, re.I))
                if k and pr: c.append((k * 2 - abs(len(s) - 200) / 220, i, s))
        c.sort(reverse=True); seen = []
        print(f'[{tema}]' + ('' if c else ' NADA'))
        for sc, i, s in c:
            if len(seen) >= top: break
            if any(s[:40] == x[:40] for x in seen): continue
            seen.append(s); print(f' p{i}: {s}')
