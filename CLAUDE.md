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

## Marca
Logo: «sin» blanco en Bricolage Grotesque sobre negro, con un trazo de rotulador sepia donde iría el adjetivo; se lee como una cara de expresión neutra. Lo eligió el dueño. Imágenes en `marca/`, generadas con `marca/fuente/generar.cjs`. La vista previa se copia a `site/public/og.png` y el icono a `site/public/icono-256.png`.

## Cómo funciona
- `scripts/fuente_*.py`: datos escritos a mano (candidaturas, citas, etiquetas de votaciones).
- `scripts/build_data.py`: comprueba citas contra los PDF de `raw/` y genera `site/src/data/`.
- `scripts/build_archivo.py`: debates íntegros, frases por reglas y todas las votaciones en `site/build-data/`. Reglas en `scripts/reglas.py`.
- `scripts/llamamientos.py`: en las votaciones por llamamiento los datos abiertos solo dan el total; cuenta la lista nominal del Diario de Sesiones y solo la acepta si cuadra con el total oficial.
- `scripts/crawl_votaciones2.py` y `scripts/descargar_diarios.py`: descargan datos del Congreso. Reanudables.
- `scripts/actualidad.py`: titulares por RSS y agrupación, sin IA.
- `sh build.sh`: comprueba citas y genera la web en local.
- `.github/workflows/actualizar.yml`: con cada push a `main` y tres veces al día lee titulares, genera y publica en GitHub Pages.
- Alojamiento: GitHub Pages, para no copiar a GitHub el token de Netlify, que da acceso a todos los sitios de la cuenta. La cuenta de Netlify es del plan antiguo (100 GB, sin créditos). `sin-adjetivos.netlify.app` solo redirige a Pages con un `_redirects` desplegado a mano. La organización de GitHub evita que el usuario personal aparezca en la dirección. `site/scripts/base_path.mjs` solo actúa si se define BASE_PATH.
- Si `git pull --rebase` choca en `data/noticias.json` o `site/src/data/actualidad.json`, son datos generados por el cron: quedarse con los del servidor (`git checkout --ours`) y volver a ejecutar `scripts/actualidad.py`.
- `raw/` no va al repositorio: son copias de PDF y se vuelven a descargar.

## Plan
1. Hecho: portal, colores, plenos con buscador, votaciones, Actualidad automática y la página Cómo votar.
2. Fichas de votaciones clave (`scripts/fuente_fichas*.py`, verificadas por `build_fichas.py`): 44 fichas y 428 citas, con una frase de cada grupo que intervino. Cada cita debe decir la postura o el motivo del grupo, en castellano si el Diario trae esa versión. Quedan en otro idioma una de BNG en juzgados de violencia, sin versión en castellano. Para ampliar: `scripts/seleccion_fichas.py` da las siguientes por tema, `scripts/candidatas.py` y `scripts/turnos_grupo.py` ayudan a elegir la frase.
3. Causas judiciales: revisados 24 casos abiertos en `scripts/revision_casos.py`. Quedan 38 cerrados sin comprobar, que siguen procediendo de DatosClaros.
4. Programas de 2026: a 4 de noviembre ningún partido ha publicado el suyo; solo está el Contrato con España del PP, que ya está en la web. Comprobarlo con frecuencia y actualizar el aviso de `site/src/pages/temas/[id].astro`, que lleva fecha.
5. TikTok: guiones en `marca/tiktok/guiones.md` e imágenes con `marca/tiktok/generar.cjs`. Formato fijo y equilibrio: alternar votaciones en las que perdió cada bloque. Nada de etiquetas ni de generalizar por grupos: nombrar quién votó qué y atribuir cada postura. El dueño ya está publicando: no cambiar en las fichas las citas que mencionan los guiones sin avisarle. Hay guiones hasta el 09.
6. Actualidad: faltan Público (sin feed localizado) y Vozpópuli (su feed devuelve 403 a nuestro lector; no falsear la identidad para saltarlo). Falta ver funcionar el cron programado tras el traslado: solo se han visto ejecuciones por push.
7. Tras el 29-N: resultados, pactos frente a promesas, y evolución hacia un periódico de datos. Dominio y correo propios cuando haya dinero.

## Calendario de la campaña
- 12 de noviembre: la Diputación Permanente vota los decretos 28 y 29/2026. Añadir el resultado a las dos fichas de vivienda de octubre.
- 13 de noviembre: empieza la campaña. Vigilar programas y debates; los debates siguen en negociación, RTVE propone uno de portavoces el 23.
- 19 de noviembre: acaba el plazo para pedir el voto por correo. 25: para enviarlo.
- 24 a 28 de noviembre: prohibido publicar encuestas; esta web nunca lo hace, pero Actualidad enlaza titulares.
- 28 de noviembre: jornada de reflexión. No publicar vídeos ni contenido nuevo, salvo correcciones.

## Riesgos abiertos
Publicar causas judiciales con nombre propio tiene riesgo legal y aún no lo ha revisado un abogado. Correcciones por GitHub Issues o sinadjetivosperiodico@gmail.com. Responder rápido a cualquier rectificación.
