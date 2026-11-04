#!/bin/sh
# Comprueba las citas contra sus fuentes y genera la web. Si una cita falla, no se publica nada.
set -e
python scripts/build_data.py
cd site && npm run build
