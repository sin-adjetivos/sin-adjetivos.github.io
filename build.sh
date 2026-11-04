#!/bin/sh
# Comprueba citas y fichas contra sus fuentes y genera la web. Si algo falla, no se genera nada.
set -e
python scripts/build_data.py
python scripts/build_archivo.py
python scripts/build_fichas.py
python scripts/build_noticias.py
cd site && npm run build
