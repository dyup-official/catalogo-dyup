# Padrão de foto do catálogo DYUP: fundo branco, tênis de perfil centralizado, sombra suave no chão.
# Uso: python3 padroniza.py <pasta_origem> <pasta_destino> [REF ...]
# O tênis sempre fica com o bico para a direita (calcanhar à esquerda): fotos viradas são espelhadas sozinhas.
# Se a detecção errar numa foto: FLIP=REF1,REF2 força espelhar; NOFLIP=REF1,REF2 impede.
import sys,os
from PIL import Image, ImageFilter, ImageDraw, ImageChops
from rembg import new_session, remove
S=1000; LARG=0.90; ALT_MAX=0.55; BASE=0.71
src,dst=sys.argv[1],sys.argv[2]; os.makedirs(dst,exist_ok=True)
refs=sys.argv[3:] or [os.path.splitext(f)[0] for f in sorted(os.listdir(src)) if f.endswith('.jpg')]
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
ses=new_session('isnet-general-use')
for r in refs:
  im=Image.open(os.path.join(src,r+'.jpg')).convert('RGB')
  cut=remove(im,session=ses)
  a=cut.split()[-1].point(lambda p:0 if p<20 else p); cut.putalpha(a)
  cut=cut.crop(a.getbbox())
  if r in flip or (r not in noflip and virado(cut)): cut=cut.transpose(Image.FLIP_LEFT_RIGHT); print('espelhado',r)
  k=min(S*LARG/cut.width, S*ALT_MAX/cut.height); cut=cut.resize((round(cut.width*k),round(cut.height*k)),Image.LANCZOS)
  x=(S-cut.width)//2; y=round(S*BASE)-cut.height
  can=Image.new('RGB',(S,S),'white')
  # sombra: elipse larga e difusa + sombra de contato mais escura, colada na sola
  sh=Image.new('L',(S,S),0); d=ImageDraw.Draw(sh); yb=y+cut.height
  d.ellipse([x+cut.width*0.06, yb-14, x+cut.width*0.96, yb+18], fill=140)
  sh=sh.filter(ImageFilter.GaussianBlur(16))
  ct=Image.new('L',(S,S),0); dc=ImageDraw.Draw(ct)
  dc.ellipse([x+cut.width*0.12, yb-6, x+cut.width*0.92, yb+6], fill=185)
  ct=ct.filter(ImageFilter.GaussianBlur(5))
  sh=ImageChops.lighter(sh,ct)
  can.paste((120,122,126),(0,0),sh)
  can.paste(cut,(x,y),cut)
  can.save(os.path.join(dst,r+'.jpg'),quality=88); print('ok',r)
