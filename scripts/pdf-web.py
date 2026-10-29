import pymupdf, io, sys
from PIL import Image
W=int(sys.argv[1]); Q=int(sys.argv[2])
d=pymupdf.open('boek.pdf')
xrefs={im[0] for p in d for im in p.get_images(full=True)}
for x in xrefs:
    info=d.extract_image(x)
    if info["width"]<600: continue
    im=Image.open(io.BytesIO(info["image"])).convert("RGB")
    h=round(im.height*W/im.width)
    buf=io.BytesIO(); im.resize((W,h),Image.LANCZOS).save(buf,"JPEG",quality=Q,optimize=True)
    d.update_stream(x, buf.getvalue(), compress=False)
    for k,v in [("Filter","/DCTDecode"),("Width",str(W)),("Height",str(h)),("ColorSpace","/DeviceRGB"),("BitsPerComponent","8"),("DecodeParms","null")]:
        d.xref_set_key(x,k,v)
d.set_metadata({**d.metadata, "title": "Uit de pluktuin · Seizoenskookboek 2026"})
d.save('kookboek.pdf', garbage=4, deflate=True, use_objstms=1)
