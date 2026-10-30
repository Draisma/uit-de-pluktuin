# Uit de pluktuin

Website van het seizoenskookboek *Uit de pluktuin 2026*: 90 recepten met de wekelijkse oogst van pluktuin De Gagelgaard, plus de twee eetclubmenu's met draaiboek.

Statische site, gebouwd met [Astro](https://astro.build) en gehost op Cloudflare.

## Lokaal draaien

```sh
npm install
npm run dev      # http://localhost:4321
npm run build    # bouwt naar dist/
```

## Structuur

| Pad | Inhoud |
| --- | --- |
| `src/data/recepten.json` | Alle recepten, uit de pdf gehaald (titel, tags, ingrediënten per groep, bereiding, tip) |
| `src/data/eetclub.json` | De eetclubmenu's en het draaiboek |
| `src/data/boek.json` | Voorwoord en hoofdstukken |
| `public/fotos/` | Foto's per boekpagina (`pNNN-480/960/1600.webp`) |
| `public/og/` | Deelplaatjes 1200×630 voor WhatsApp en sociale media |
| `scripts/extract.py` | Haalt de recepten uit de kookboek-pdf (`python3 extract.py` naast `boek.pdf`) |
| `scripts/fotos.py` | Zet de originele foto's om naar webformaten |
| `boek/` | Hulpmiddelen voor de drukversie van het boek: fotoprompts, foto's in de pdf zetten, lettertype (zie `boek/README.md`) |
| `public/kookboek.pdf` | Het boek als download, foto's verkleind tot 960 px zodat hij onder de 25 MiB-limiet van Cloudflare blijft (`scripts/pdf-web.py 960 72`) |

Een recept aanpassen? Bewerk `src/data/recepten.json` en push: Cloudflare bouwt de site dan automatisch opnieuw.

## Cloudflare

De site draait als Cloudflare Worker met statische assets (zie `wrangler.jsonc`), gekoppeld aan deze repo via Workers Builds.

- Build command: `npm run build`
- Deploy command: `npx wrangler deploy`
- Worker-naam: `uit-de-pluktuin` (moet gelijk zijn aan `name` in `wrangler.jsonc`)
- Node-versie: via `.node-version` (22)
- Domein: https://kookboek.fldr.nl
