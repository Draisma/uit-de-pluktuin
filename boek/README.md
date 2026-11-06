# Het boek bijwerken

De drukversie van *Uit de pluktuin 2026* (de pdf in Google Drive, map Recepten) wordt gebouwd uit dezelfde gegevens als de site: `src/data/recepten.json`, `eetclub.json` en `boek.json`. Inhoudsopgave, hoofdstukpagina's en paginanummers rekent het bouwscript zelf uit.

| Bestand | Wat |
| --- | --- |
| `bouw.py` | Bouwt het boek als html en zet het met Playwright/Chromium om naar een A4-pdf. Met `--schrijf` zet hij de paginanummers terug in `recepten.json` en `eetclub.json` |
| `boek.css` | De opmaak van het boek: A4, kleuren per hoofdstuk, ingrediëntenvak, genummerde stappen |
| `drukfotos.py` | Snijdt de originele foto's bij tot A4 (1240×1754, JPEG q80) voor in de pdf |
| `fotoprompts.json` | De Gemini-prompt per foto, op slug |
| `hernoem-download.sh` | Verplaatst de nieuwste Gemini-download naar `kookboek-fotos/SLUG.jpeg` |
| `fonts/` | Playfair Display, Lora en Caveat (SIL Open Font License) |

## Een recept toevoegen

1. Zet het recept in `src/data/recepten.json`, achteraan in zijn hoofdstuk, met `"pagina": null` en `"foto"` gelijk aan de slug. `intro` en `serveertip` mogen een lijst van alinea's zijn.
2. Maak de foto met Gemini (zie hieronder) en zet hem als `SLUG.jpeg` in `kookboek-fotos`.
3. Drukfoto's: `python3 boek/drukfotos.py kookboek-fotos drukfotos`
4. Webfoto's: `python3 scripts/fotos.py kookboek-fotos public/fotos` (en de deelplaatjes in `public/fotos/og`, verplaats die naar `public/og`).
5. Boek: `python3 boek/bouw.py drukfotos kookboek.pdf --schrijf`. Het script meldt recepten die niet op één pagina passen; tekst wordt tot 0,76× verkleind voordat het zover is.
6. Push naar main. De workflow `pdf-naar-r2.yml` bouwt de pdf dan opnieuw (met de webfoto's van 1600 px) en zet hem op https://dl.fldr.nl/kookboek/uit-de-pluktuin-2026.pdf. De pdf uit stap 5, met de originele foto's, is de versie voor Google Drive en om af te drukken.

Foto's staan altijd links (even pagina's), recepten rechts. Alles na het nieuwe recept schuift twee pagina's op; omdat foto's op slug heten, hoeft er niets hernoemd te worden.

## Fotostijl

- Fotorealistisch bovenaanzicht (flat lay), staand 3:4, zacht zijlicht, geen tekst, mensen of handen.
- Elk hoofdstuk heeft zijn eigen ondergronden. Gebruik een gladde ondergrond (marmer, travertin, stucwerk, geverfde planken) of een **strak gestreken** linnen tafelkleed. Nooit een gekreukt tafelkleed: zet in de prompt "smooth, freshly ironed linen tablecloth, pulled taut and completely flat, no creases, no wrinkles, no folds".
- Gemini levert 1792×2400. Lagere resolutie (896×1200) opnieuw laten maken.

## Gemini

- Eén nieuwe chat per foto; meerdere afbeeldingen in één chat weigert Gemini soms.
- Downloaden met de knop "Download full size image". Een JavaScript-klik werkt niet, het moet een echte klik zijn, en de knop moet in beeld staan.
- Wacht na de klik zo'n 13 seconden voordat je naar de volgende chat gaat, anders gaat de download verloren.
- Gemini Plus haalt ongeveer 27 foto's per venster van 5 uur.
