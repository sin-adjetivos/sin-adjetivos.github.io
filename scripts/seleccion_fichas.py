"""Elige las votaciones clave de cada tema con reglas fijas, para que la selección no dependa de quien escribe la ficha.

Reglas:
  1. Solo decisiones sobre normas: decretos ley, leyes en votación final, enmiendas a la totalidad y propuestas de ley.
     Fuera mociones, textos sin fuerza de ley, enmiendas sueltas, tratados y trámites.
  2. El título debe tratar directamente del tema (lista estricta, más corta que la de clasificación general).
  3. Debe tener debate enlazado.
  4. Orden: primero normas en vigor o rechazadas (decretos y votaciones finales), luego propuestas; dentro de cada
     nivel, el resultado más ajustado; a igualdad, la más reciente.
"""
import json, re, sys
ESTRICTO = {
 'vivienda': r'viviend|alquiler|arrendamiento|desahuci|lanzamientos|ocupaci[oó]n ilegal',
 'pensiones': r'pensi[oó]n|pensiones|revaloriz|jubilaci|Seguridad Social|Real Decreto-ley (9/2024|1/2025)',
 'inmigracion': r'extranjer[ií]a|los extranjeros|personas extranjeras|regularizaci[oó]n|migrant|arraigo|competencias estatales en materia de inmigraci|asilo',
 'impuestos': r'impuesto|tributari|medidas fiscales|IRPF|\bIVA\b|presupuestos generales|estabilidad presupuestaria',
 'empleo': r'salario m[ií]nimo|jornada|desempleo|despido|Estatuto de los Trabajadores|protecci[oó]n laboral|reforma laboral|aut[oó]nomos|permiso de nacimiento',
 'sanidad': r'sanidad|sanitari|\bsalud\b|\bELA\b|Esclerosis|medicamento|enfermer|hospital|ópticos|Muface',
 'educacion': r'educaci|educativ|escolar|alumn|universi|\bbecas?\b|formaci[oó]n profesional',
 'energia': r'energ[ií]a|nuclear|el[eé]ctric|clim[aá]t|renovable|emisiones|incendios',
 'defensa': r'Defensa Nacional|gasto en defensa|militar|fuerzas armadas|ucrania|gaza|palestin|armament|material de defensa',
 'territorio': r'amnist[ií]a|Comunidad Aut[oó]noma de Catalu|lengua|cooficial|Estatuto de Autonom|financiaci[oó]n auton|condonaci|Concierto Econ|Convenio Econ|cupo|autopista',
 'justicia': r'corrupci|poder judicial|Ministerio Fiscal|secretos oficiales|seguridad ciudadana|enjuiciamiento|C[oó]digo Penal|Servicio P[uú]blico de Justicia',
 'igualdad': r'paritari|violencia de g[eé]nero|violencia sobre|aborto|\btrans\b|lgtbi|prostituci|trata de|igualdad',
}
FUERA = r'(?<!las )enmiendas? (?!a la totalidad)|^Votaci[oó]n de la enmienda|^Moci[oó]n|^Proposici[oó]n no de Ley|^Tramitaci[oó]n como|avocaci[oó]n|prórroga|Tratado|Convenio entre|Convenio sobre|Acuerdo entre|Acuerdo Internacional|Parlamento de Catalu|Dictamen de la Comisi[oó]n del Estatuto|Elecci[oó]n|subcomisi[oó]n|Solicitud'
def nivel(t):
    if re.match(r'Real Decreto-ley', t, re.I) or re.search(r'dictamen|votaci[oó]n de conjunto|amnist[ií]a|a la totalidad', t, re.I): return 0
    return 1
def elegir(n=20):
    v = json.load(open('site/build-data/votos_todos.json', encoding='utf-8'))
    out = {}
    for tema, rx in ESTRICTO.items():
        c = [x for x in v if re.search(rx, x['titulo'], re.I) and not re.search(FUERA, x['titulo'], re.I) and x.get('debates')]
        c.sort(key=lambda x: (nivel(x['titulo']), abs(x['si'] - x['no']), -int(x['fecha'].replace('-', ''))))
        vistos = set(); r = []
        for x in c:
            k = x.get('expediente') or x['titulo']
            if k in vistos: continue
            vistos.add(k); r.append(x)
        out[tema] = r[:n]
    return out
if __name__ == '__main__':
    temas = sys.argv[1:] or list(ESTRICTO)
    sel = elegir()
    for t in temas:
        print(f'\n## {t} ({len(sel[t])})')
        for x in sel[t]:
            print(f" {x['fecha']} {x['si']}-{x['no']}-{x['abst']} {x['expediente']} deb={x['debates'][:1]} | {x['titulo'][:150]}")
