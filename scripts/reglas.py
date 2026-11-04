"""Reglas públicas de extracción. Se muestran tal cual en la web: cualquiera puede comprobar por qué una frase aparece."""
TEMA_RX = {
 'vivienda': r'viviend|alquiler|arrendamiento|desahuci|lanzamientos|okupa|ocupaci[oó]n ilegal|inquilin|hipotec|suelo urbano|Sareb',
 'pensiones': r'pensi[oó]n|pensiones|revaloriz|Pacto de Toledo|jubilaci|Seguridad Social|cotizaci[oó]n',
 'inmigracion': r'inmigra|migrant|migrator|extranjer[ií]a|extranjeros|regularizaci[oó]n|asilo|refugiad|menores no acompa|fronter|Ceuta|Melilla|arraigo|remigraci',
 'impuestos': r'impuesto|tributari|fiscal|IRPF|\bIVA\b|presupuestos generales|senda de d[eé]ficit|objetivos de estabilidad|estabilidad presupuestaria|deuda p[uú]blica|Hacienda|Agencia Tributaria|financiaci[oó]n auton',
 'empleo': r'empleo|laboral|salario|\bSMI\b|jornada|desempleo|despido|trabajador|aut[oó]nomos|siniestralidad|Estatuto de los Trabajadores|paro\b|huelga',
 'sanidad': r'sanidad|sanitari|\bsalud\b|\bELA\b|Esclerosis|listas de espera|medicamento|m[eé]dic|enfermer|atenci[oó]n primaria|MIR\b|hospital|tabaco|Muface',
 'educacion': r'educaci|educativ|escuela|escolar|alumn|docente|universi|\bbecas?\b|formaci[oó]n profesional|profesor',
 'energia': r'energ[ií]|nuclear|apag[oó]n|el[eé]ctric|clim[aá]t|renovable|carbono|emisiones|incendios|dana\b|transici[oó]n ecol[oó]gica|agua\b|sequ[ií]a|medio ambiente|gas\b|combustible',
 'defensa': r'defensa|militar|fuerzas armadas|otan\b|ucrania|gaza|palestin|israel|ir[aá]n\b|armament|exterior|sahara|marruecos|venezuela|gibraltar|uni[oó]n europea|trump|estados unidos|tratado',
 'territorio': r'amnist[ií]a|Catalu[nñ]a|autonom|Estatuto de Autonom|lenguas?\b|cooficial|catal[aá]n|euskera|gallego|independen|referendum|referéndum|Puigdemont|cupo|concierto econ|traspaso|competencias|transferencia|Navarra|Pa[ií]s Vasco|Euskadi|Galicia|Canarias|condonaci',
 'justicia': r'corrupci|poder judicial|\bCGPJ\b|Ministerio Fiscal|Fiscal General|fiscal general|secretos oficiales|mordaza|seguridad ciudadana|justicia|Koldo|Tribunal Constitucional|Tribunal Supremo|comisi[oó]n de investigaci[oó]n|transparencia|lawfare|C[oó]digo Penal|\bjueces\b|enjuiciamiento',
 'igualdad': r'igualdad|paritari|paridad|violencia de g[eé]nero|violencia sobre|violencia machista|machis|feminis|aborto|\btrans\b|lgtbi|mujeres|prostituci|trata de|brecha',
}
# Sentido del voto, en castellano, catalán y gallego. Se excluyen las referencias al voto de otros en lo posible.
VOTO_RX = r"\b((vamos a|voy a|va a|van a) votar (a favor|en contra|s[ií]\b|no\b|que s[ií]|que no|favorablemente|negativamente)|votaremos (a favor|en contra|s[ií]\b|no\b|favorablemente)|votar[eé] (a favor|en contra|s[ií]\b|no\b)|nuestro voto (ser[aá]|va a ser|es)|nuestro grupo (votar[aá]|apoyar[aá]|no va a)|vamos a apoyar|apoyaremos|no vamos a apoyar|no apoyaremos|vamos a abstenernos|nos vamos a abstener|nos abstendremos|votamos (s[ií]\b|no\b|a favor|en contra)|votarem (a favor|en contra|s[ií]|no\b|favorablement)|el nostre vot ser[aà]|vai votar a favor|vai votar en contra|imos votar (a favor|en contra)|o noso voto (ser[aá]|vai)|vamos a respaldar)"
PROPUESTA_RX = r"\b(proponemos|exigimos|nuestra propuesta|reclamamos|planteamos|nuestra enmienda|hemos presentado|proposem|exigim|la nostra proposta|prop[oó]ñemos|esiximos|hemos aprobado|vamos a aprobar|vamos a derogar|vamos a bajar|vamos a subir|vamos a crear)\b"
GRUPOS = {'GP': 'pp', 'GS': 'psoe', 'GVOX': 'vox', 'GSUMAR': 'frente-amplio', 'GR': 'erc', 'GJxCAT': 'junts', 'GEH Bildu': 'eh-bildu', 'GV (EAJ-PNV': 'pnv', 'GV (EAJ-PNV)': 'pnv'}
MIXTO = [('Rego Candamil', 'bng'), ('Valido García', 'coalicion-canaria'), ('Belarra', 'podemos'), ('Sánchez Serna', 'podemos'), ('Santana Perera', 'podemos'), ('Velarde', 'podemos'), ('Muñoz Dalda', 'podemos'), ('Micó Micó', 'compromis')]
GOBIERNO_RX = r'Ministr|Presidente del Gobierno|Vicepresident[ae].*Gobierno|Vicepresident[ae] (Primer|Segund|Tercer|Cuart)'
