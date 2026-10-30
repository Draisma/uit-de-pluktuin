# Uit de pluktuin

Website van het seizoenskookboek *Uit de pluktuin 2026*: 104 recepten met de wekelijkse oogst van pluktuin De Gagelgaard, plus de twee eetclubmenu's met draaiboek.

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
| `public/fotos/` | Foto's per recept, genoemd naar de slug (`slug-480/960/1600.webp`) |
| `public/og/` | Deelplaatjes 1200×630 voor WhatsApp en sociale media (`slug.jpg`) |
| `scripts/extract.py` | Haalde de eerste 90 recepten uit de oude kookboek-pdf (niet meer nodig: het boek wordt nu uit de data gebouwd) |
| `scripts/fotos.py` | Zet de originele foto's om naar webformaten |
| `boek/` | De drukversie van het boek: bouwscript, opmaak, lettertypen en fotoprompts (zie `boek/README.md`) |
| `public/kookboek.pdf` | Het boek als download, foto's verkleind tot 960 px zodat hij onder de 25 MiB-limiet van Cloudflare blijft (`scripts/pdf-web.py 960 72`) |

Een recept aanpassen? Bewerk `src/data/recepten.json` en push: Cloudflare bouwt de site dan automatisch opnieuw.

## Cloudflare

De site draait als Cloudflare Worker met statische assets (zie `wrangler.jsonc`), gekoppeld aan deze repo via Workers Builds.

- Build command: `npm run build`
- Deploy command: `npx wrangler deploy`
- Worker-naam: `uit-de-pluktuin` (moet gelijk zijn aan `name` in `wrangler.jsonc`)
- Node-versie: via `.node-version` (22)
- Domein: https://kookboek.fldr.nl

## Licentie

| Wat | Licentie |
| --- | --- |
| Broncode: `src/` (behalve `src/data/`), `scripts/`, `boek/*.py`, `boek/*.sh`, `boek/boek.css` en configuratie | [MIT](LICENSE) |
| Inhoud: recepten en teksten (`src/data/`), foto's (`public/fotos/`, `public/og/`) en het boek (`public/kookboek.pdf`) | [CC BY-NC-SA 4.0](LICENSE-CONTENT) |
| Lettertypen in `boek/fonts/` (Lora, Playfair Display, Caveat) | [SIL Open Font License 1.1](boek/fonts/OFL.txt) |

De inhoud mag je delen en bewerken, mits je de bron vermeldt (*Uit de pluktuin*, Florian Draisma, kookboek.fldr.nl), het niet commercieel gebruikt en bewerkingen onder dezelfde licentie deelt.
