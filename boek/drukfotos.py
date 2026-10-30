"""Maakt de foto's voor de drukversie: bijsnijden tot A4 en verkleinen tot 1240x1754 (JPEG q80).

Gebruik: python3 boek/drukfotos.py map-met-originelen uitmap [slug ...]
De originelen heten SLUG.jpeg (zoals in kookboek-fotos); de uitvoer SLUG.jpg.
Zonder slugs worden alle jpegs in de map omgezet.
"""
import os, sys
from PIL import Image, ImageOps

W, H = 1240, 1754
SRC, UIT = sys.argv[1], sys.argv[2]
os.makedirs(UIT, exist_ok=True)
namen = sys.argv[3:] or sorted(f.rsplit('.', 1)[0] for f in os.listdir(SRC) if f.endswith('.jpeg'))
for n in namen:
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, n + '.jpeg'))).convert('RGB')
    w, h = im.size
    tr = 1500 / 2121  # A4
    if w / h > tr:
        nw = int(h * tr); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / tr); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im.resize((W, H), Image.LANCZOS).save(os.path.join(UIT, n + '.jpg'), 'JPEG', quality=80, optimize=True, progressive=True)
    print(n)
