#!/bin/bash
# Bouwt het boek uit de webfoto's in public/fotos (1600 px), net als de workflow pdf-naar-r2.yml,
# en schrijft de paginanummers terug in src/data. Zo zijn de originele foto's niet nodig.
# Gebruik (vanuit de root van de repo): boek/bouw-uit-webfotos.sh [uit.pdf]
set -e
W=$(mktemp -d)
# De drukfoto's blijven bewaard in .cache/drukfotos; alleen nieuwe of gewijzigde foto's worden omgezet.
python3 boek/drukfotos.py --web public/fotos .cache/drukfotos > /dev/null
python3 boek/bouw.py .cache/drukfotos "${1:-$W/boek.pdf}" --schrijf
echo "pdf: ${1:-$W/boek.pdf}"
