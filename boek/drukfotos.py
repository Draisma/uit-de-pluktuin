"""Maakt de foto's voor de drukversie: bijsnijden tot A4 en verkleinen tot 1240x1754 (JPEG q80).

Gebruik:
  python3 boek/drukfotos.py map-met-originelen uitmap [slug ...]
      De originelen heten SLUG.jpeg (zoals in kookboek-fotos); de uitvoer SLUG.jpg.
      Zonder slugs worden alle jpegs in de map omgezet.
  python3 boek/drukfotos.py --web public/fotos uitmap
      Gebruikt de webfoto's SLUG-1600.webp en zet alleen nieuwe of gewijzigde foto's om.
      Wat al klopt staat in uitmap/.bron.json (hash van elke bron en van dit script);
      foto's die niet meer bestaan worden uit de uitmap verwijderd.
"""
import hashlib, json, os, sys
from PIL import Image, ImageOps

W, H = 1240, 1754


def zet_om(bron, doel):
    im = ImageOps.exif_transpose(Image.open(bron)).convert('RGB')
    w, h = im.size
    tr = 1500 / 2121  # A4
    if w / h > tr:
        nw = int(h * tr); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / tr); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im.resize((W, H), Image.LANCZOS).save(doel, 'JPEG', quality=80, optimize=True, progressive=True)


def sha(pad):
    with open(pad, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def web(src, uit):
    os.makedirs(uit, exist_ok=True)
    manifest = os.path.join(uit, '.bron.json')
    try:
        oud = json.load(open(manifest))
    except (OSError, ValueError):
        oud = {}
    script = sha(__file__)
    if oud.get('_script') != script:
        oud = {}
    nieuw = {'_script': script}
    gedaan = 0
    for f in sorted(os.listdir(src)):
        if not f.endswith('-1600.webp'):
            continue
        n = f[:-10]
        h = sha(os.path.join(src, f))
        doel = os.path.join(uit, n + '.jpg')
        if oud.get(n) != h or not os.path.exists(doel):
            zet_om(os.path.join(src, f), doel)
            print(n)
            gedaan += 1
        nieuw[n] = h
    for f in os.listdir(uit):
        if f.endswith('.jpg') and f[:-4] not in nieuw:
            os.remove(os.path.join(uit, f))
    json.dump(nieuw, open(manifest, 'w'), indent=0)
    print('%d van %d foto\'s omgezet' % (gedaan, len(nieuw) - 1), file=sys.stderr)


if __name__ == '__main__':
    if sys.argv[1] == '--web':
        web(sys.argv[2], sys.argv[3])
    else:
        SRC, UIT = sys.argv[1], sys.argv[2]
        os.makedirs(UIT, exist_ok=True)
        namen = sys.argv[3:] or sorted(f.rsplit('.', 1)[0] for f in os.listdir(SRC) if f.endswith('.jpeg'))
        for n in namen:
            zet_om(os.path.join(SRC, n + '.jpeg'), os.path.join(UIT, n + '.jpg'))
            print(n)
