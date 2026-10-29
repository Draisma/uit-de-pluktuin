"""Haal de recepten uit de kookboek-pdf en schrijf recepten.json."""
import json, re, sys, unicodedata
import pymupdf

PDF = "boek.pdf"
d = pymupdf.open(PDF)

TAGS = {
    "AZIATISCH": "Aziatisch", "BASKISCH": "Baskisch", "BELGISCH": "Belgisch",
    "BIJGERECHT": "Bijgerecht", "CHINEES": "Chinees", "DESSERT": "Dessert",
    "DESSERT:IJS": "Dessert: ijs", "DRINKEN": "Drinken", "ENGELS": "Engels",
    "FRANS": "Frans", "GEZINSMAALTIJD": "Gezinsmaaltijd", "GRIEKS": "Grieks",
    "HOLLANDS": "Hollands", "HONGAARS": "Hongaars", "HOOFDGERECHT": "Hoofdgerecht",
    "HUISKEUKEN": "Huiskeuken", "IERS": "Iers", "INDIAAS": "Indiaas",
    "INDONESISCH": "Indonesisch", "ITALIAANS": "Italiaans", "JAPANS": "Japans",
    "KOREAANS": "Koreaans", "LIBANEES": "Libanees", "LUNCH&BORREL": "Lunch & borrel",
    "MAALTIJDSALADE": "Maaltijdsalade", "MAROKKAANS": "Marokkaans",
    "MEDITERRAAN": "Mediterraan", "MEXICAANS": "Mexicaans",
    "MIDDEN-OOSTERS": "Midden-Oosters", "NOORD-AFRIKAANS": "Noord-Afrikaans",
    "PORTUGEES": "Portugees", "SALADE": "Salade", "SOEP": "Soep", "SPAANS": "Spaans",
    "SRILANKAANS": "Sri Lankaans", "THAIS": "Thais", "TUNESISCH": "Tunesisch",
    "TURKS": "Turks", "VEGETARISCH": "Vegetarisch", "VIETNAMEES": "Vietnamees",
    "VOORGERECHT": "Voorgerecht", "ZELFGEMAAKT": "Zelfgemaakt",
    "LENTEKEUKEN": "Lentekeuken", "ZOMERKEUKEN": "Zomerkeuken",
    "MENU": "Menu", "ZOMERSEGEDEELDETAFEL": "Zomerse gedeelde tafel",
}
SEASONS = {"LENTE": "lente", "ZOMER": "zomer", "HERFST": "herfst",
           "ZOET&DRINKEN": "zoet", "EETCLUB": "eetclub"}

CHAPTERS = [  # (slug, titel, eerste receptpagina, laatste)
    ("lente", "Lente", 9, 55),
    ("zomer", "Zomer", 59, 131),
    ("herfst", "Herfst", 135, 177),
    ("zoet", "Zoet & drinken", 181, 185),
    ("eetclub", "Eetclub", 189, 201),
]
SPECIAL = {189, 191, 193}  # menu's en draaiboek: apart verwerkt


def despace(t):
    return re.sub(r"\s+", "", t)


def is_spaced_caps(t):
    t = t.strip()
    return len(t) >= 3 and bool(re.search(r"\S \S \S", t)) and t.upper() == t


def page_lines(p):
    out = []
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            spans = [s for s in l["spans"] if s["text"]]
            t = "".join(s["text"] for s in spans)
            if not t.strip():
                continue
            big = max(spans, key=lambda s: len(s["text"].strip()) * s["size"])
            out.append(dict(
                x=l["bbox"][0], y=l["bbox"][1], y1=l["bbox"][3], x1=l["bbox"][2],
                size=max(s["size"] for s in spans), color=f'{big["color"]:06x}',
                text=t, font=big["font"],
            ))
    return out


def join(lines):
    """Regels samenvoegen tot lopende tekst, met afbreekstreepjes goed."""
    s = ""
    for t in lines:
        t = t.strip()
        if not t:
            continue
        if not s:
            s = t
        elif s.endswith("-") and not s.endswith(" -"):
            nxt = t.split(" ")[0]
            if nxt in ("en", "of", "tot", "à") or (s[-2:-1].isdigit() and not nxt[:1].isdigit()):
                s += " " + t
            else:
                s += t
        else:
            s += " " + t
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def bullets(p, xmax):
    ys = []
    for dr in p.get_drawings():
        r = dr["rect"]
        if r.x1 < xmax and 2.5 < r.width < 6 and 2.5 < r.height < 6 and dr.get("fill"):
            ys.append((r.y0 + r.y1) / 2)
    return sorted(ys)


def parse_recipe(pno):
    p = d[pno - 1]
    L = page_lines(p)
    L = [l for l in L if l["y"] < 790]  # voettekst weg
    # kolomkoppen
    ing_h = next((l for l in L if despace(l["text"]) == "INGREDIËNTEN"), None)
    ber_h = next((l for l in L if despace(l["text"]) == "BEREIDING"), None)
    if not ing_h or not ber_h:
        raise ValueError(f"p{pno}: geen kolomkoppen")
    split = ber_h["x"] - 8
    body_top = min(ing_h["y"], ber_h["y"])

    head = sorted([l for l in L if l["y"] < body_top - 2], key=lambda l: (round(l["y"]), l["x"]))
    # tagregel
    tagline = [l for l in head if is_spaced_caps(l["text"]) or l["text"].strip() == "•"]
    tagwords = [despace(l["text"]) for l in sorted(tagline, key=lambda l: l["x"]) if l["text"].strip() != "•"]
    season = None
    tags = []
    for w in tagwords:
        if w in SEASONS and season is None:
            season = SEASONS[w]
        elif w in TAGS:
            tags.append(TAGS[w])
        elif w in SEASONS:
            pass
        else:
            print(f"p{pno}: onbekende tag {w}", file=sys.stderr)
    rest = [l for l in head if l not in tagline]
    title_lines = [l for l in rest if l["size"] >= 24]
    title = join([l["text"] for l in sorted(title_lines, key=lambda l: l["y"])])
    after_title = [l for l in rest if l not in title_lines]
    tmax = max(l["y1"] for l in title_lines)
    sub = [l for l in after_title if l["color"] == "6f6359" and l["y"] < tmax + 40]
    subtitle = join([l["text"] for l in sorted(sub, key=lambda l: l["y"])])
    others = [l for l in after_title if l not in sub]
    pills_y = None
    pills = []
    intro = []
    for l in sorted(others, key=lambda l: (round(l["y"]), l["x"])):
        if l["color"] == "2b2622" and (pills_y is None or abs(l["y"] - pills_y) < 4):
            pills_y = l["y"]
            pills.append(l["text"].strip())
        else:
            intro.append(l["text"])
    intro = join(intro)
    serves = next((x for x in pills if x.lower().startswith("voor ")), None)
    meta = [x for x in pills if x != serves]

    body = [l for l in L if l["y"] >= body_top - 2 and l not in (ing_h, ber_h)]
    left = sorted([l for l in body if l["x"] < split], key=lambda l: (l["y"], l["x"]))
    right = sorted([l for l in body if l["x"] >= split], key=lambda l: (l["y"], l["x"]))

    # ---- ingrediënten
    bys = bullets(p, split)
    item_x = min((l["x"] for l in left if any(abs((l["y"] + l["y1"]) / 2 - by) < 5 for by in bys)), default=84)
    groups = []  # [{"title":..., "harvest":bool, "items":[...]}]
    cur = None
    items_text = []  # werk: list van lijsten regels

    def new_group(title=None):
        g = {"titel": title, "items": []}
        groups.append(g)
        return g

    for l in left:
        mid = (l["y"] + l["y1"]) / 2
        has_bullet = any(abs(mid - by) < 5 for by in bys)
        if has_bullet:
            if cur is None:
                cur = new_group()
            cur["items"].append([l["text"]])
        elif l["x"] < item_x - 4:
            if cur is not None and cur["titel"] and not cur["items"]:
                cur["titel"] = join([cur["titel"], l["text"]])
            else:
                cur = new_group(join([l["text"]]))
        else:
            if cur is None or not cur["items"]:
                # losse regel zonder bullet: notitie (bv. 'taartvorm 24 cm')
                if cur is None:
                    cur = new_group()
                cur["items"].append([l["text"]])
            else:
                cur["items"][-1].append(l["text"])
    ingredienten = []
    for g in groups:
        items = [join(i) for i in g["items"]]
        if not items and g["titel"]:
            continue
        ingredienten.append({"titel": g["titel"], "items": items})

    # ---- bereiding
    chapter_color = ber_h["color"]
    nums = [l for l in right if re.fullmatch(r"\d{1,2}", l["text"].strip()) and l["color"] == chapter_color]
    num_x = min((l["x"] for l in nums), default=split)
    text_x = None
    steps = []
    tip_lines = []
    notes = []
    tip_mode = False
    tip_y = None
    for l in right:
        t = l["text"].strip()
        if l in nums:
            steps.append({"n": int(t), "y": l["y"], "lines": []})
            continue
        if t == "Tip" and l["size"] > 15:
            tip_mode = True
            tip_y = l["y"]
            continue
        if tip_mode:
            tip_lines.append(l["text"])
            continue
        if steps and l["x"] > num_x + 8 and l["color"] == "2b2622":
            # hoort bij de stap waarvan het nummer er het dichtst boven staat
            st = [s for s in steps if s["y"] <= l["y"] + 6]
            (st[-1] if st else steps[-1])["lines"].append(l["text"])
        else:
            notes.append(l["text"])
    bereiding = [join(s["lines"]) for s in sorted(steps, key=lambda s: s["n"])]
    return dict(
        pagina=pno, foto=f"p{pno-1:03d}", titel=title, ondertitel=subtitle,
        seizoen=season, tags=tags, personen=serves, meta=meta, intro=intro,
        ingredienten=ingredienten, bereiding=bereiding,
        serveertip=join(notes) or None, tip=join(tip_lines) or None,
    )


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s[:70].rstrip("-")


if __name__ == "__main__":
    recepten = []
    seen = set()
    for slug, naam, a, b in CHAPTERS:
        for pno in range(a, b + 1, 2):
            if pno in SPECIAL:
                continue
            r = parse_recipe(pno)
            r["hoofdstuk"] = slug
            recepten.append(r)
    import collections
    cnt = collections.Counter(r["titel"] for r in recepten)
    for r in recepten:
        name = r["titel"] if cnt[r["titel"]] == 1 else r["titel"] + " " + r["ondertitel"]
        s = slugify(name)
        assert s not in seen, s
        seen.add(s)
        r["slug"] = s
    json.dump(recepten, open("recepten.json", "w"), ensure_ascii=False, indent=1)
    print(len(recepten), "recepten")
