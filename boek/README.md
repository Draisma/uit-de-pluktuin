# Het boek bijwerken

Hulpmiddelen voor de pdf *Uit de pluktuin 2026* (de drukversie in Google Drive, map Recepten).

| Bestand | Wat |
| --- | --- |
| `fotoprompts.json` | De Gemini-prompt per fotopagina (`p001` t/m `p202`), zoals gebruikt voor de huidige foto's |
| `vervang-fotos.py` | Zet nieuwe foto's in de pdf: `python3 vervang-fotos.py bron.pdf map-met-pNNN.jpeg uit.pdf`. Vervangt de afbeeldingsstream in place (geen duplicaten), snijdt bij tot A4 (1240×1754, JPEG q80) en past het voorwoord aan |
| `hernoem-download.sh` | Verplaatst de nieuwste Gemini-download naar `kookboek-fotos/pNNN.jpeg` |
| `fonts/` | Lora 400 en 700 (SIL Open Font License), het lettertype van het boek |

## Fotostijl

- Fotorealistisch bovenaanzicht (flat lay), staand 3:4, zacht zijlicht, geen tekst, mensen of handen.
- Elk hoofdstuk heeft zijn eigen ondergronden. Gebruik een gladde ondergrond (marmer, travertin, stucwerk, geverfde planken) of een **strak gestreken** tafelkleed. Nooit een gekreukt tafelkleed: zet in de prompt "smooth, freshly ironed, no creases".
- Gemini levert 1792×2400. Lagere resolutie (896×1200) opnieuw laten maken.

## Gemini

- Eén nieuwe chat per foto; meerdere afbeeldingen in één chat weigert Gemini soms.
- Downloaden met de knop "Download full size image". Een JavaScript-klik werkt niet, het moet een echte klik zijn.
- Wacht na de klik zo'n 13 seconden voordat je naar de volgende chat gaat, anders gaat de download verloren.
- Gemini Plus haalt ongeveer 27 foto's per venster van 5 uur.

## Pdf voor de website

`public/kookboek.pdf` is een verkleinde versie (onder de 25 MiB per bestand van Cloudflare): zet de drukversie als `boek.pdf` in de werkmap en draai `python3 ../scripts/pdf-web.py 960 72`.
