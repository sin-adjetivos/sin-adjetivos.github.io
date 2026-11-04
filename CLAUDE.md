# Sin adjetivos

Portal independiente para informar a la ciudadanía sobre las elecciones generales del 29 de noviembre de 2026 y seguir informando después. Firma Sergio Capuchino, sin vinculación con partidos y sin presupuesto. Web: https://sin-adjetivos.github.io/. Repositorio: https://github.com/sin-adjetivos/sin-adjetivos.github.io

## Principios que no se negocian
- **Objetividad comprobable:** mismo trato y mismas casillas para todos los partidos. Sin puntuaciones, rankings ni totales de casos por partido. Sin encuestas ni petición de voto.
- **Literalidad:** toda cita debe existir tal cual en su fuente. `scripts/build_data.py` falla si no aparece.
- **Honestidad sobre los límites:** «no localizado» no es «no existe». Decir de qué año es cada documento. Una investigación no es una condena.
- **Sencillez:** la gente no va a leer plenos; hay que extraer lo vital en lenguaje claro y dejar el texto íntegro como prueba.
- **Coste 0 €:** el dueño no tiene presupuesto. No usar servicios de pago ni la API de Anthropic sin que lo pida. Los resúmenes se hacen en la sesión de Claude Code.

## Diseño
Blanco y sepia de las papeletas en las páginas generales; color de cada partido en sus páginas y etiquetas (`site/src/lib/color.js`). Lo que dicen otros va en Source Serif; lo nuestro, en Archivo. Evitar la estética típica de IA: mayúsculas en etiquetas, puntos medios, flechas, fuente monoespaciada.

## Cómo funciona
- `scripts/fuente_*.py`: datos escritos a mano (candidaturas, citas, etiquetas de votaciones).
- `scripts/build_data.py`: comprueba citas contra los PDF de `raw/` y genera `site/src/data/`.
- `scripts/build_archivo.py`: debates íntegros, frases por reglas y todas las votaciones en `site/build-data/`. Reglas en `scripts/reglas.py`.
- `scripts/crawl_votaciones2.py` y `scripts/descargar_diarios.py`: descargan datos del Congreso. Reanudables.
- `scripts/actualidad.py`: titulares por RSS y agrupación, sin IA.
- `sh build.sh`: comprueba citas y genera la web en local.
- `.github/workflows/actualizar.yml`: con cada push a `main` y tres veces al día lee titulares, genera y publica en GitHub Pages.
- Alojamiento: GitHub Pages, para no copiar a GitHub el token de Netlify, que da acceso a todos los sitios de la cuenta. La cuenta de Netlify es del plan antiguo (100 GB, sin créditos). `sin-adjetivos.netlify.app` solo redirige a Pages con un `_redirects` desplegado a mano. La organización de GitHub evita que el usuario personal aparezca en la dirección. `site/scripts/base_path.mjs` solo actúa si se define BASE_PATH.
- `raw/` no va al repositorio: son copias de PDF y se vuelven a descargar.

## Plan
1. Hecho: portal, colores, plenos con buscador, votaciones, Actualidad automática.
2. Fichas de votaciones clave (`scripts/fuente_fichas*.py`, verificadas por `build_fichas.py`): hechas vivienda, pensiones e inmigración. Faltan los otros 9 temas. Antes, revisar las reglas de `seleccion_fichas.py` para cada tema, porque aún cuelan títulos ajenos (por ejemplo, un impuesto en sanidad). Herramientas: `scripts/buscar_en_debate.py` y `scripts/leer_debate.py`.
3. Revisar uno a uno los casos judiciales, empezando por los abiertos; hoy proceden de DatosClaros sin verificación propia.
4. Añadir programas de 2026 cuando se publiquen. Votación de vivienda en Diputación Permanente prevista el 12 de noviembre.
5. TikTok: guiones e imágenes verticales desde los datos, con formato fijo y registro público de cuántas veces sale cada partido.
6. Faltan medios en Actualidad: El Debate, La Razón, Público y Vozpópuli.
7. Tras el 29-N: resultados, pactos frente a promesas, y evolución hacia un periódico de datos. Dominio y correo propios cuando haya dinero.

## Riesgos abiertos
Publicar causas judiciales con nombre propio tiene riesgo legal y aún no lo ha revisado un abogado. Correcciones por GitHub Issues o sinadjetivosperiodico@gmail.com. Responder rápido a cualquier rectificación.
