#!/bin/bash
# Verplaatst de nieuwste Gemini-download naar kookboek-fotos/pPAGINA.jpeg en toont grootte en afmetingen.
# Gebruik: hernoem-download.sh PAGINA [max-seconden-wachten]
# Draait op de Mac; Downloads staat daar onder $HOME/mnt/Downloads.
D="$HOME/mnt/Downloads"; T="$D/kookboek-fotos"
for i in $(seq 1 ${2:-40}); do
  f=$(ls -t "$D"/Gemini_Generated_Image_*.jpeg "$D"/Gemini_Generated_Image_*.png 2>/dev/null | head -1)
  if [ -n "$f" ]; then s1=$(stat -c %s "$f"); sleep 1; s2=$(stat -c %s "$f"); if [ "$s1" = "$s2" ] && [ "$s1" -gt 500000 ]; then ext="${f##*.}"; mv "$f" "$T/p$1.$ext"; echo "p$1 <- $(basename "$f") $s1 $(python3 -c "from PIL import Image;print(Image.open(\"$T/p$1.$ext\").size)")"; exit 0; fi; fi
  sleep 1
done
echo "p$1 TIMEOUT"
