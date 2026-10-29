import sys, os
from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageOps
SRC, OUT = sys.argv[1], sys.argv[2]
WIDTHS = [480, 960, 1600]
os.makedirs(OUT, exist_ok=True); os.makedirs(OUT + "/og", exist_ok=True)
def do(fn):
    name = fn.rsplit(".", 1)[0]
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, fn))).convert("RGB")
    for w in WIDTHS:
        h = round(im.height * w / im.width)
        im.resize((w, h), Image.LANCZOS).save(f"{OUT}/{name}-{w}.webp", "WEBP", quality=78, method=6)
    # deelplaatje 1200x630 (midden iets hoger, gerecht staat meestal centraal)
    W, H = 1200, 630
    s = W / im.width
    r = im.resize((W, round(im.height * s)), Image.LANCZOS)
    top = max(0, round(r.height * 0.45 - H / 2))
    r.crop((0, top, W, top + H)).save(f"{OUT}/og/{name}.jpg", "JPEG", quality=80, optimize=True, progressive=True)
    return name
files = sorted(f for f in os.listdir(SRC) if f.endswith(".jpeg"))
with ProcessPoolExecutor() as ex:
    for n in ex.map(do, files): pass
print(len(files), "foto's")
