#!/bin/bash
# Bouwt het boek uit de webfoto's in public/fotos (1600 px), net als de workflow pdf-naar-r2.yml,
# en schrijft de paginanummers terug in src/data. Zo zijn de originele foto's niet nodig.
# Gebruik (vanuit de root van de repo): boek/bouw-uit-webfotos.sh [uit.pdf]
set -e
W=$(mktemp -d)
python3 - public/fotos "$W/fotos" <<'PY'
import os, sys
from PIL import Image
src, uit = sys.argv[1], sys.argv[2]
os.makedirs(uit, exist_ok=True)
for f in os.listdir(src):
    if f.endswith('-1600.webp'):
        Image.open(os.path.join(src, f)).convert('RGB').save(os.path.join(uit, f[:-10] + '.jpeg'), quality=92)
PY
python3 boek/drukfotos.py "$W/fotos" "$W/drukfotos" > /dev/null
python3 boek/bouw.py "$W/drukfotos" "${1:-$W/boek.pdf}" --schrijf
echo "pdf: ${1:-$W/boek.pdf}"
