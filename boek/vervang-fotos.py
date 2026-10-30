# Vervangt de afbeelding op elke fotopagina van het kookboek door FOTOS/pNNN.jpeg (in place, zonder duplicaten)
# en past de zin over de illustratie in het voorwoord aan.
# Gebruik: python3 vervang-fotos.py bron.pdf map-met-fotos uit.pdf
import pymupdf as fitz, glob, os, io, sys
from PIL import Image
W,H=1240,1754
SRC,FOTOS,UIT=sys.argv[1:4]
HERE=os.path.dirname(os.path.abspath(__file__))
d=fitz.open(SRC)
done=[]
for f in sorted(glob.glob(os.path.join(FOTOS,"p*.jpeg"))):
    pg=int(os.path.basename(f)[1:4])
    im=Image.open(f).convert("RGB")
    w,h=im.size; tr=1500/2121
    if w/h>tr: nw=int(h*tr); im=im.crop(((w-nw)//2,0,(w-nw)//2+nw,h))
    else: nh=int(w/tr); im=im.crop((0,(h-nh)//2,w,(h-nh)//2+nh))
    im=im.resize((W,H),Image.LANCZOS)
    buf=io.BytesIO(); im.save(buf,"JPEG",quality=80,optimize=True,progressive=True)
    imgs=d[pg-1].get_images(full=True); assert len(imgs)==1,(pg,len(imgs))
    xref=imgs[0][0]
    d.update_stream(xref, buf.getvalue(), compress=False)
    for k,v in [("Filter","/DCTDecode"),("Width",str(W)),("Height",str(H)),("ColorSpace","/DeviceRGB"),("BitsPerComponent","8")]:
        d.xref_set_key(xref,k,v)
    for k in ("DecodeParms","SMask","Decode"):
        if d.xref_get_key(xref,k)[0]!="null": d.xref_set_key(xref,k,"null")
    done.append(pg)
print("replaced",len(done))
# voorwoord: illustratie -> foto
p=d[2]
origin=None
for b in p.get_text("rawdict",clip=fitz.Rect(180,362,230,382))["blocks"]:
    for l in b.get("lines",[]):
        for s in l["spans"]:
            for c in s["chars"]:
                if c["c"]=="i" and (origin is None or c["origin"][0]<origin[0]): origin=c["origin"]
print("origin",origin)
x0,y=origin
r=fitz.Rect(x0-0.3,366.5,388.5,380.6)
p.add_redact_annot(r, fill=False)
p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
reg=fitz.Font(fontfile=os.path.join(HERE,"fonts/Lora-400.ttf")); bold=fitz.Font(fontfile=os.path.join(HERE,"fonts/Lora-700.ttf"))
col=(0x2b/255,0x26/255,0x22/255); fs=9.8
tw=fitz.TextWriter(p.rect, color=col)
x=x0
for txt,fnt in [("foto van het gerecht, ",reg),("rechts",bold),(" het recept.",reg)]:
    tw.append((x,y),txt,font=fnt,fontsize=fs); x+=fnt.text_length(txt,fs)
tw.write_text(p)
d.subset_fonts()
d.save(UIT,garbage=4,deflate=True)
print("saved")
