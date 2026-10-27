# Padroniza as fotos novas do catálogo DYUP: fundo branco 1000x1000, produto recortado e centralizado, sombra suave.
# Uso: python3 fotos.py <pasta_origem> <pasta_destino> <raw.json>
# O nome do arquivo é a referência do Linx (REF.jpg, REF_2.png ...); qualquer formato que o Pillow abra.
# Tênis: de perfil, bico para a direita (fotos viradas são espelhadas sozinhas). Roupas e acessórios: centralizados.
# Se a detecção errar: FLIP=REF1,REF2 força espelhar; NOFLIP=REF1,REF2 impede.
import sys,os,json,re
from PIL import Image, ImageFilter, ImageDraw, ImageChops
try: import pillow_avif  # noqa
except Exception: pass
S=1000
src,dst,rawf=sys.argv[1:4]; os.makedirs(dst,exist_ok=True)
GR={}
for g in json.load(open(rawf)):
  if g['ref']: GR[g['ref'].upper()]=(g['ref'],g['grupo'])
flip=set(filter(None,os.environ.get('FLIP','').split(',')))
noflip=set(filter(None,os.environ.get('NOFLIP','').split(',')))
def virado(cut):
  # calcanhar é a ponta mais alta: compara o topo médio dos 25% da esquerda com os 25% da direita
  a=cut.split()[-1]; w,h=a.size; px=a.load(); tops=[]
  for x in range(w):
    t=next((y for y in range(h) if px[x,y]>128),None)
    if t is not None: tops.append((x,t))
  q=w//4; esq=[t for x,t in tops if x<q]; dir=[t for x,t in tops if x>=w-q]
  return bool(esq and dir) and sum(dir)/len(dir) < sum(esq)/len(esq)
def sombra(x,yb,w,forte):
  sh=Image.new('L',(S,S),0); d=ImageDraw.Draw(sh)
  d.ellipse([x+w*0.06, yb-14, x+w*0.96, yb+18], fill=140 if forte else 70)
  sh=sh.filter(ImageFilter.GaussianBlur(16))
  if forte:  # sombra de contato mais escura, colada na sola
    ct=Image.new('L',(S,S),0); ImageDraw.Draw(ct).ellipse([x+w*0.12, yb-6, x+w*0.92, yb+6], fill=185)
    sh=ImageChops.lighter(sh,ct.filter(ImageFilter.GaussianBlur(5)))
  return sh
ses=None; res={"ok":[],"sem_ref":[],"falha":[]}
for f in sorted(os.listdir(src)):
  nome,ext=os.path.splitext(f)
  if f.upper().startswith('LEIA-ME') or ext.lower() not in ('.jpg','.jpeg','.png','.webp','.avif','.heic','.bmp','.tif','.tiff'): continue
  m=re.match(r'^(.*?)(?:_(\d+))?$',nome.strip()); base,n=m.group(1).strip(),m.group(2)
  if base.upper() not in GR: res["sem_ref"].append(f); continue
  ref,gr=GR[base.upper()]
  try: im=Image.open(os.path.join(src,f)); im.load(); im=im.convert('RGBA')
  except Exception as e: res["falha"].append(f"{f}: {e}"); continue
  if ses is None:
    from rembg import new_session, remove
    ses=new_session('isnet-general-use')
  cut=remove(im,session=ses)
  a=cut.split()[-1].point(lambda p:0 if p<20 else p); cut.putalpha(a)
  if not a.getbbox(): res["falha"].append(f"{f}: não achei o produto na foto"); continue
  cut=cut.crop(a.getbbox())
  tenis=gr=='Tênis'
  if tenis and (ref in flip or (ref not in noflip and virado(cut))): cut=cut.transpose(Image.FLIP_LEFT_RIGHT)
  if tenis: k=min(S*0.90/cut.width, S*0.55/cut.height)
  else: k=min(S*0.80/cut.width, S*0.80/cut.height)
  cut=cut.resize((round(cut.width*k),round(cut.height*k)),Image.LANCZOS)
  x=(S-cut.width)//2; y=round(S*0.71)-cut.height if tenis else (S-cut.height)//2-10
  can=Image.new('RGB',(S,S),'white')
  can.paste((120,122,126),(0,0),sombra(x,y+cut.height,cut.width,tenis))
  can.paste(cut,(x,y),cut)
  out=ref+('_'+n if n else '')+'.jpg'
  can.save(os.path.join(dst,out),quality=88); res["ok"].append({"arquivo":f,"foto":out,"grupo":gr})
print(json.dumps(res,ensure_ascii=False))
