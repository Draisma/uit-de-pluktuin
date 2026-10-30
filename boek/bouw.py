"""Bouwt de drukversie van het kookboek (A4-pdf) uit de gegevens van de site.

Gebruik:
    python3 boek/bouw.py FOTOMAP uit.pdf

FOTOMAP bevat per foto een jpeg met de slug als naam (omslag.jpg, hoofdstuk-lente.jpg,
koreaanse-bibimbap.jpg, ...), bijgesneden tot A4 (1240x1754). Maak die met
`python3 boek/drukfotos.py map-met-originelen FOTOMAP`.

Na het bouwen worden de paginanummers in recepten.json en eetclub.json bijgewerkt
(veld "pagina"), zodat site en boek gelijk blijven. Vereist Playwright met Chromium.
"""
import json, re, html, os, sys, asyncio

HIER = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HIER, '..', 'src', 'data')
RECEPTEN = json.load(open(os.path.join(DATA, 'recepten.json')))
EETCLUB = json.load(open(os.path.join(DATA, 'eetclub.json')))
BOEK = json.load(open(os.path.join(DATA, 'boek.json')))

TINT = {'lente': '#e8f0dc', 'zomer': '#f8e8d4', 'herfst': '#f4e1d8', 'zoet': '#f6e0e5', 'eetclub': '#dfe9e2'}

# ----------------------------------------------------------------- html helpers
E = lambda s: html.escape(s, quote=False)


def fmt(s):
    s = E(s)
    s = s.replace(' - ', ' – ')
    s = re.sub(r'(\d) ?°C', r'\1&nbsp;°C', s)
    s = re.sub(r'(\d) (g|ml|el|tl|cm|kg|minuten|min)\b', r'\1&nbsp;\2', s)
    return s


def lijst(x):
    if not x:
        return []
    return x if isinstance(x, list) else [x]


def chips(bits):
    return ''.join('<span class="chip">%s</span>' % fmt(b) for b in bits)


def ing_html(groups):
    o = '<h3>Ingrediënten</h3>'
    for g in groups:
        o += '<div class="grp">'
        if g.get('titel'):
            o += '<h4>%s</h4>' % fmt(g['titel'])
        o += '<ul>' + ''.join('<li>%s</li>' % fmt(i) for i in g['items']) + '</ul></div>'
    return o


def steps_html(steps, start=1, title='Bereiding'):
    o = '<h3>%s</h3><ol class="steps">' % title
    n = start
    for s in steps:
        if isinstance(s, dict):
            o += '<li class="sh">%s</li>' % fmt(s['h'])
        else:
            o += '<li><span class="n">%d</span><span class="t">%s</span></li>' % (n, fmt(s))
            n += 1
    return o + '</ol>'


def extras(r):
    o = ''
    notes = lijst(r.get('serveertip'))
    if notes:
        o += '<div class="notes">' + ''.join('<p>%s</p>' % fmt(n) for n in notes) + '</div>'
    for t in lijst(r.get('tip')):
        o += '<div class="tip"><span class="tipl">Tip</span><p>%s</p></div>' % fmt(t)
    return o


def toc_name(r):
    m = r['titel']
    if len(m.split()) <= 2 and r.get('ondertitel') and not m.startswith('Herfstdiner'):
        sub = r['ondertitel'] if r['ondertitel'].startswith('met ') else '(' + r['ondertitel'] + ')'
        return m + ' ' + sub
    return m


def kicker(ch, r):
    parts = [ch['titel']] + [p for p in r.get('tags', []) if p and p != ch['titel'] and p not in ('Eetclub', 'Zoet')]
    return ' <span class="dot">•</span> '.join(E(p) for p in parts)


def footer(pno, ch=None):
    label = 'Uit de pluktuin' + (' <span class="dot">•</span> %s' % E(ch['titel']) if ch else '')
    return '<div class="folio"><span class="fl">%s</span><span class="pn">%d</span></div>' % (label, pno)


# ----------------------------------------------------------------- inhoud per hoofdstuk
def volgorde(slug):
    """Recepten van een hoofdstuk in boekvolgorde; nieuwe recepten (zonder pagina) achteraan."""
    rs = [r for r in RECEPTEN if r['hoofdstuk'] == slug]
    oud = sorted([r for r in rs if r.get('pagina')], key=lambda r: r['pagina'])
    nieuw = [r for r in rs if not r.get('pagina')]
    items = [('recept', r) for r in oud + nieuw]
    if slug == 'eetclub':
        menus = [e for e in EETCLUB if e['type'] == 'menu']
        items = [('menu', m) for m in menus] + items
    return items


# ----------------------------------------------------------------- pagina's
class Book:
    def __init__(self, fotos):
        self.pages = []
        self.fotos = fotos

    @property
    def n(self):
        return len(self.pages) + 1

    def add(self, cls, inner, style=''):
        side = 'right' if self.n % 2 == 1 else 'left'
        self.pages.append('<section class="page %s %s" style="%s">%s</section>' % (side, cls, style, inner))
        return len(self.pages)

    def src(self, key):
        p = os.path.join(self.fotos, key + '.jpg')
        assert os.path.exists(p), ('foto ontbreekt', p)
        return 'file://' + os.path.abspath(p)

    def img(self, key, cls='illus'):
        assert self.n % 2 == 0, ('foto moet op een linkerpagina', key, self.n)
        return self.add(cls, '<img src="%s">' % self.src(key))


def recipe_page(ch, r):
    o = '<div class="inner fit" data-key="%s">' % r['slug']
    o += '<div class="kicker">%s</div>' % kicker(ch, r)
    o += '<h1>%s</h1>' % fmt(r['titel'])
    if r.get('ondertitel'):
        o += '<div class="sub">%s</div>' % fmt(r['ondertitel'])
    bits = lijst(r.get('personen')) + lijst(r.get('meta'))
    if bits:
        o += '<div class="chips">%s</div>' % chips(bits)
    if r.get('intro'):
        o += '<div class="intro">' + ''.join('<p>%s</p>' % fmt(p) for p in lijst(r['intro'])) + '</div>'
    o += '<div class="cols"><div class="ing">%s</div><div class="prep">%s%s</div></div>' % (
        ing_html(r['ingredienten']), steps_html(r['bereiding']), extras(r))
    o += '</div>'
    return o


def zomer_menu(m):
    o = '<div class="inner fit" data-key="%s"><div class="kicker">%s</div><h1>%s</h1><div class="sub">%s</div><div class="chips">%s</div>' % (
        m['slug'], 'Eetclub <span class="dot">•</span> Zomer <span class="dot">•</span> Menu', fmt(m['titel']), fmt(m['ondertitel']),
        chips(lijst(m.get('personen')) + lijst(m.get('meta'))))
    o += '<div class="intro">' + ''.join('<p>%s</p>' % fmt(p) for p in lijst(m['intro'])) + '</div>'
    o += '<div class="ing ing3">%s</div></div>' % ing_html(m['ingredienten'])
    return o


def draaiboek_page(d, menu):
    o = '<div class="inner fit" data-key="%s"><div class="kicker">%s</div><h1>%s</h1><div class="sub">%s</div>' % (
        d['slug'], 'Eetclub <span class="dot">•</span> ' + E(menu['titel']), fmt(d['titel']), fmt(d['ondertitel']))
    steps = []
    for f in d['fasen']:
        steps.append({'h': f['titel']})
        steps += f['stappen']
    hs = [i for i, x in enumerate(steps) if isinstance(x, dict)]
    cut = hs[2]
    n1 = sum(1 for x in steps[:cut] if not isinstance(x, dict))
    o += '<div class="prep prep2"><div>%s</div><div>%s%s</div></div></div>' % (
        steps_html(steps[:cut], title=''), steps_html(steps[cut:], start=n1 + 1, title=''), extras(d))
    return o


def herfst_menu(m):
    o = '<div class="inner fit" data-key="%s"><div class="kicker">Eetclub <span class="dot">•</span> Herfst <span class="dot">•</span> Menu</div>' % m['slug']
    o += '<h1>%s</h1><div class="sub">%s</div>' % (fmt(m['titel']), fmt(m['ondertitel']))
    o += '<div class="menucard">'
    for g in m['gangen']:
        o += '<div class="mc-h">%s</div>' % E(g['titel'])
        if g.get('noot'):
            o += '<div class="mc-n">%s</div>' % E(g['noot'])
        for d in g['gerechten']:
            o += '<div class="mc-d">%s</div>' % fmt(d['naam'])
    o += '</div>'
    o += '<div class="intro">' + ''.join('<p>%s</p>' % fmt(p) for p in lijst(m['intro'])) + '</div>'
    ds = m['dessert']
    o += '<div class="cols cols2"><div class="ing"><h3>%s</h3><ul>%s</ul><p class="small">%s</p></div>' % (
        E(ds['titel']), ''.join('<li>%s</li>' % fmt(x) for x in ds['items']), fmt(ds['bereiding']))
    o += '<div class="prep"><h3>Draaiboek</h3><div class="draai">'
    for f in m['draaiboek']:
        o += '<div class="dr-h">%s</div>' % fmt(f['titel'])
        for t in f['taken']:
            o += '<div class="dr-i">%s</div>' % fmt(t)
    o += '</div></div></div></div>'
    return o


def voorwoord():
    v = BOEK['voorwoord']
    o = '<div class="inner prose"><div class="kicker">Voorwoord</div><h1 class="big">%s</h1><p class="lead">%s</p>' % (E(v['titel']), E(v['lead']))
    o += ''.join('<p>%s</p>' % E(a) for a in v['alineas'])
    o += '<h3>Zo lees je de recepten</h3><ul class="how">'
    for li in v['zo_lees_je']:
        li = E(li)
        li = li.replace('foto van het gerecht, met daaronder het recept.', 'foto van het gerecht, <b>rechts</b> het recept.')
        li = re.sub(r'^Bij elk recept staat een foto', '<b>Links</b> staat steeds een foto', li)
        li = li.replace('voor 4 personen', 'voor <b>4 personen</b>')
        li = li.replace('Bij Uit de pluktuin', 'Bij <i>Uit de pluktuin</i>')
        o += '<li>%s</li>' % li
    o += '</ul><p class="sign">%s</p></div>' % E(v['slot'])
    return o


def build(pages_in=None):
    b = Book(FOTOS)
    hfd = BOEK['hoofdstukken']
    fotos = BOEK['fotos']
    # 1 omslag
    b.add('cover', '<img src="%s"><div class="covercard"><div class="cv-k">%s</div><h1>Uit de<br>pluktuin</h1>'
                   '<div class="cv-s">Recepten met de wekelijkse oogst<br>van De Gagelgaard</div><div class="cv-r"></div>'
                   '<div class="cv-f">Lente <span class="dot">•</span> Zomer <span class="dot">•</span> Herfst <span class="dot">•</span> Zoet <span class="dot">•</span> Eetclub</div></div>'
          % (b.src(fotos['omslag']), E(BOEK['bovenkop'])))
    b.img(fotos['schutblad'])
    b.add('prose', voorwoord() + footer(3))
    b.img(fotos['inhoud'])
    # 5 inhoud
    toc = '<div class="inner toc"><div class="kicker">Inhoud</div><h1 class="big">Inhoud</h1><div class="toccols">'
    if pages_in:
        for ch in hfd:
            toc += '<div class="tocch"><h4 style="color:%s"><span>%s</span><span class="tp">%d</span></h4>' % (ch['kleur'], E(ch['titel']), pages_in[ch['slug']])
            for soort, r in volgorde(ch['slug']):
                toc += '<div class="te"><span class="tt">%s</span><span class="lead"></span><span class="tp">%d</span></div>' % (fmt(toc_name(r)), pages_in[r['slug']])
            toc += '</div>'
    toc += '</div></div>'
    b.add('tocpage', toc + footer(5))
    pages = {}
    for ch in hfd:
        style = '--acc:%s;--tint:%s' % (ch['kleur'], TINT[ch['slug']])
        b.img(ch['foto'])
        lst = ''
        items = volgorde(ch['slug'])
        for soort, r in items:
            r2 = r if soort == 'recept' or r['titel'] != 'Herfstdiner voor zes' else dict(r, ondertitel='menu en draaiboek')
            lst += '<div class="te"><span class="tt">%s</span><span class="lead"></span><span class="tp">%s</span></div>' % (fmt(toc_name(r2)), (pages_in or {}).get(r['slug'], ''))
        pages[ch['slug']] = b.n
        b.add('opener', '<div class="inner"><div class="chno">Hoofdstuk %d</div><h1 class="chname">%s</h1><div class="chmonths">%s</div><div class="chrule"></div>'
                        '<p class="chintro">%s</p><div class="chlist">%s</div></div>%s' % (ch['nummer'], E(ch['titel']), E(ch['periode']), E(ch['intro']), lst, footer(b.n, ch)), style)
        for soort, r in items:
            if soort == 'menu' and isinstance(r.get('draaiboek'), str):
                b.img(r['foto'])
                pages[r['slug']] = b.n
                b.add('recipe', zomer_menu(r) + footer(b.n, ch), style)
                d = next(e for e in EETCLUB if e['slug'] == r['draaiboek'])
                b.img(d['foto'])
                pages[d['slug']] = b.n
                b.add('recipe', draaiboek_page(d, r) + footer(b.n, ch), style)
            elif soort == 'menu':
                b.img(r['foto'])
                pages[r['slug']] = b.n
                b.add('menu', herfst_menu(r) + footer(b.n, ch), style)
            else:
                b.img(r['foto'])
                pages[r['slug']] = b.n
                b.add('recipe', recipe_page(ch, r) + footer(b.n, ch), style)
    if b.n % 2 == 1:
        b.add('notes', '<div class="inner prose"><div class="kicker">Notities</div><h1 class="big">Notities</h1><div class="lines">' + '<div class="ln"></div>' * 26 + '</div></div>' + footer(b.n))
    b.add('back', '<img src="%s"><div class="backcard"><div class="cv-k">Uit de pluktuin</div><p>%s</p></div>' % (b.src(fotos['achterkant']), E(BOEK['achterflap'])))
    return b, pages


CSS = open(os.path.join(HIER, 'boek.css')).read().replace("url('fonts/", "url('file://%s/fonts/" % HIER)


def html_doc(b):
    return '<!doctype html><html lang="nl"><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (CSS, ''.join(b.pages))


FIT_JS = '''
() => {
  const res = {};
  for (const el of document.querySelectorAll('.fit')) {
    let k = 1.32;
    el.style.setProperty('--k', k);
    while (el.scrollHeight > el.clientHeight + 1 && k > 0.76) {
      k -= 0.02; el.style.setProperty('--k', k.toFixed(3));
    }
    res[el.dataset.key] = [Number(k.toFixed(3)), el.scrollHeight > el.clientHeight + 1];
  }
  // lange lijsten op de hoofdstukpagina's en de inhoud: kleiner tot ze passen
  for (const el of document.querySelectorAll('.opener .inner, .tocpage .inner')) {
    let fs = 0;
    const box = el.closest('.page').getBoundingClientRect();
    const voet = el.closest('.page').querySelector('.folio').getBoundingClientRect().top;
    const last = () => Math.max(0, ...[...el.querySelectorAll('.te')].map(t => t.getBoundingClientRect().bottom));
    const cols = el.querySelector('.toccols');
    const over = () => last() > voet - 6 || (cols && cols.scrollWidth > cols.clientWidth + 1);
    while (over() && fs < 30) { fs++; el.style.setProperty('--lijst', (1 - fs * 0.02).toFixed(2)); }
    res['lijst:' + (el.querySelector('.chname, .big').textContent)] = [1 - fs * 0.02, over()];
  }
  return res;
}
'''


async def render_pdf(doc_path, pdf_path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page()
        await pg.goto('file://' + doc_path)
        await pg.evaluate('document.fonts.ready')
        res = await pg.evaluate(FIT_JS)
        await pg.pdf(path=pdf_path, prefer_css_page_size=True, print_background=True)
        await br.close()
        return res


if __name__ == '__main__':
    FOTOS = os.path.abspath(sys.argv[1])
    uit = os.path.abspath(sys.argv[2])
    b, pages = build()
    b, pages2 = build(pages)
    assert pages == pages2
    doc = os.path.splitext(uit)[0] + '.html'
    open(doc, 'w').write(html_doc(b))
    res = asyncio.run(render_pdf(doc, uit))
    bad = {k: v for k, v in res.items() if v[1]}
    small = {k: v[0] for k, v in res.items() if v[0] < 1}
    print('pagina\'s', len(b.pages), 'te vol', bad)
    print('verkleind', small)
    # paginanummers terugschrijven
    if '--schrijf' in sys.argv:
        # alleen de waarde van "pagina" vervangen, zodat de opmaak van de json-bestanden blijft zoals hij is
        for fn in ('recepten.json', 'eetclub.json'):
            pad = os.path.join(DATA, fn)
            tekst = open(pad).read()
            def vervang(m):
                return m.group(1) + str(pages[m.group(3)])
            tekst, n = re.subn(r'("pagina":\s*)(null|\d+)(?=,\s*"foto":\s*"([^"]+)")', vervang, tekst)
            assert n == len(json.loads(tekst)), (fn, n)
            open(pad, 'w').write(tekst)
        print('paginanummers bijgewerkt')
