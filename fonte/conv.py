# Converte fotos enviadas (qualquer formato) para JPEG 800px fundo branco em fotos/REF.jpg
import sys,os
from PIL import Image
try: import pillow_avif  # noqa
except Exception: pass
out='/mnt/project-files/catalogo/fotos'
for f in sys.argv[1:]:
  ref=os.path.splitext(os.path.basename(f))[0]
  try:
    im=Image.open(f); im.load()
  except Exception as e:
    print('FALHA',f,e); continue
  if im.mode in ('RGBA','LA','P'):
    im=im.convert('RGBA'); bg=Image.new('RGB',im.size,'white'); bg.paste(im,mask=im.split()[-1]); im=bg
  else: im=im.convert('RGB')
  im.thumbnail((800,800))
  im.save(f'{out}/{ref}.jpg',quality=86); print('ok',ref,im.size)
