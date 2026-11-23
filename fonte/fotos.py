# Padroniza as fotos novas do catálogo DYUP: fundo branco 1000x1000, produto recortado e centralizado, sombra suave.
# Uso: python3 fotos.py <pasta_origem> <pasta_destino> <raw.json>
# O nome do arquivo é a referência do Linx (REF.jpg, REF_2.png ...); qualquer formato que o Pillow abra.
# Tênis: de perfil, bico para a direita (fotos viradas são espelhadas sozinhas). Roupas e acessórios: centralizados.
# Se a detecção errar: FLIP=REF1,REF2 força espelhar; NOFLIP=REF1,REF2 impede.
# v2 (23/11/2026): cor convertida pelo perfil ICC da foto; borda sem halo cinza (contorno recua 1px e herda a cor
# do próprio produto); tênis sólido por dentro (entressola branca não fura); sola sem "dentes" (perfil de baixo
# suavizado); sombra que acompanha a curva da sola.
import sys,os,json,re,io
import numpy as np
from PIL import Image, ImageFilter, ImageCms
from scipy import ndimage as ndi
try: import pillow_avif  # noqa
except Exception: pass
S=1000
SRGB=ImageCms.createProfile('sRGB')

def abrir(p):
  im=Image.open(p); im.load()
  icc=im.info.get('icc_profile')
  if im.mode in ('P','LA','L','I;16'): im=im.convert('RGBA')
  if icc and im.mode in ('RGB','RGBA','CMYK'):  # Adobe RGB / P3 / CMYK -> sRGB, senão as cores mudam
    try:
      a=im.getchannel('A') if im.mode=='RGBA' else None
      im=ImageCms.profileToProfile(im.convert('RGB') if im.mode=='RGBA' else im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), SRGB,
                                   renderingIntent=ImageCms.Intent.PERCEPTUAL, outputMode='RGB')
      if a is not None: im.putalpha(a)
    except Exception: pass
  return im.convert('RGBA')

def virado(m):
  # calcanhar é a ponta mais alta: compara o topo médio dos 25% da esquerda com os 25% da direita
  h,w=m.shape; cols=np.where(m.any(0))[0]
  if len(cols)<8: return False
  top=np.argmax(m,0).astype(float); q=w//4
  esq=[top[x] for x in cols if x<q]; dir=[top[x] for x in cols if x>=w-q]
  return bool(esq and dir) and np.mean(dir)<np.mean(esq)

def limpa_sola(m,rgb):
  # tira o fundo/sombra antiga que ficou grudado embaixo da sola: pixels da faixa de baixo com a cor do fundo
  # (cinza neutro, nunca mais claro que o fundo) ligados ao lado de fora são removidos
  h,w=m.shape; bg=cor_fundo(rgb); lb=bg.mean()
  L=rgb.mean(-1); sat=rgb.max(-1).astype(int)-rgb.min(-1)
  cols=np.where(m.any(0))[0]
  if not len(cols): return m
  bot=np.full(w,-1); bot[cols]=h-1-np.argmax(m[::-1,cols],0)
  alt=np.ptp(np.where(m.any(1))[0])
  yy=np.arange(h)[:,None]
  faixa=(yy>=bot[None,:]-alt*0.08)&(bot[None,:]>=0)
  cand=m&faixa&(L<=lb+4)&(L>=lb-35)&(sat<14)
  fora=~m
  tira=ndi.binary_propagation(fora,mask=fora|cand)&cand
  return m&~tira

def mascara_tenis(a,rgb=None):
  m=a>=128
  m=ndi.binary_opening(m,iterations=1)
  lab,n=ndi.label(m)  # só a peça principal (tira pedaços soltos do fundo)
  if n>1:
    tam=ndi.sum(m,lab,range(1,n+1)); m=lab==(1+int(np.argmax(tam)))
  m=ndi.binary_fill_holes(m)
  if rgb is not None: m=limpa_sola(m,rgb)
  h,w=m.shape; cols=np.where(m.any(0))[0]
  if not len(cols): return m
  top=np.full(w,-1); bot=np.full(w,-1)
  top[cols]=np.argmax(m[:,cols],0); bot[cols]=h-1-np.argmax(m[::-1,cols],0)
  # perfil de baixo suavizado: uma coluna não pode descer além da mediana das vizinhas (tira os "dentes" brancos)
  r=max(4,w//150); bs=bot.copy()
  for x in cols:
    v=bot[max(0,x-r):x+r+1]; v=v[v>=0]
    if len(v)>=3: bs[x]=min(bot[x],int(np.median(v))+1)
  # dentro do tênis, entre o topo e a sola, é tudo tênis (a entressola branca não fura)
  yy=np.arange(h)[:,None]
  inside=(yy>=top[None,:])&(yy<=bs[None,:])&(bs[None,:]>=0)
  # só preenche colunas onde topo e sola fazem parte da mesma silhueta (não une o cadarço solto ao chão)
  m=(m|inside)&(yy<=bs[None,:])
  k=max(8,w//35)  # fecha frestas verticais finas na sola (não mexe no vão do arco, que é largo)
  m=m|ndi.binary_closing(np.pad(m,((0,0),(k,k))),structure=np.ones((1,k)))[:,k:-k]
  m=ndi.binary_fill_holes(m)
  return m

def cor_fundo(rgb):
  b=np.concatenate([rgb[:4].reshape(-1,3),rgb[-4:].reshape(-1,3),rgb[:,:4].reshape(-1,3),rgb[:,-4:].reshape(-1,3)])
  return np.median(b,0)

def bordas(rgb,m,feather=0.8):
  # contorno recua 1px; na faixa da borda, pixel com cor puxada para o fundo antigo herda a cor do interior vizinho
  bg=cor_fundo(rgb).astype(np.float32)
  m=ndi.binary_erosion(m,iterations=1)
  core=ndi.binary_erosion(m,iterations=2)
  out=rgb.astype(np.float32).copy()
  dist=np.abs(out-bg).max(-1)
  core=core|(m&(dist>=45))  # pixel bem diferente do fundo é do produto, mesmo na borda (sola preta fina)
  if core.sum()<50: core=m
  wgt=core.astype(np.float32); num=out*wgt[...,None]; den=wgt.copy()
  for s in (1.2,2.5,5):
    n2=np.stack([ndi.gaussian_filter(num[...,c],s) for c in range(3)],-1); d2=ndi.gaussian_filter(den,s)
    fill=(den<0.5)&(d2>1e-3)
    out[fill]=n2[fill]/d2[fill,None]; num[fill]=out[fill]; den[fill]=1
  alpha=ndi.gaussian_filter(m.astype(np.float32),feather)
  alpha=np.clip((alpha-0.5)*2.2+0.5,0,1)  # antialias curto, sem auréola
  return out.clip(0,255).astype(np.uint8),(alpha*255).astype(np.uint8)

def sombra_tenis(alpha,x0,y0):
  # sombra que nasce da sola: forte onde a sola toca o chão, some onde bico e calcanhar levantam
  a=alpha>128; h,w=a.shape; cols=np.where(a.any(0))[0]
  sh=np.zeros((S,S),np.float32)
  if not len(cols): return sh
  bot=h-1-np.argmax(a[::-1,:],0); chao=bot[cols].max()
  chao_sh=np.zeros((S,S),np.float32)
  for x in cols:
    gap=chao-bot[x]; k=max(0.0,1-gap/(h*0.10))
    X=x0+x
    if not (0<=X<S): continue
    Yc=min(S-1,y0+bot[x]+2)  # contato colado na sola, seguindo a curva
    sh[Yc,X]=max(sh[Yc,X],k)
    if 0<=y0+chao<S: chao_sh[y0+chao,X]=k
  contato=ndi.gaussian_filter(sh,(2.2,3))*9
  # sombra difusa no chão, no mesmo tamanho e força do padrão antigo do catálogo
  from PIL import ImageDraw, ImageFilter
  cw=cols[-1]-cols[0]+1; xl=x0+cols[0]; yb=y0+chao
  el=Image.new('L',(S,S),0)
  ImageDraw.Draw(el).ellipse([xl+cw*0.06, yb-14, xl+cw*0.96, yb+18], fill=140)
  difusa=np.array(el.filter(ImageFilter.GaussianBlur(16)),np.float32)/255
  return np.clip(np.maximum(contato*0.8,difusa),0,0.75)

def sombra_roupa(cw,x0,yb):
  sh=np.zeros((S,S),np.float32); y=min(S-1,yb+6)
  sh[y,max(0,x0+int(cw*0.1)):min(S,x0+int(cw*0.9))]=1
  return np.clip(ndi.gaussian_filter(sh,(8,20))*14,0,0.18)

def main():
  src,dst,rawf=sys.argv[1:4]; os.makedirs(dst,exist_ok=True)
  GR={}
  for g in json.load(open(rawf)):
    if g['ref']: GR[g['ref'].upper()]=(g['ref'],g['grupo'])
  flip=set(filter(None,os.environ.get('FLIP','').split(',')))
  noflip=set(filter(None,os.environ.get('NOFLIP','').split(',')))
  ses=None; res={"ok":[],"sem_ref":[],"falha":[]}
  for f in sorted(os.listdir(src)):
    nome,ext=os.path.splitext(f)
    if f.upper().startswith('LEIA-ME') or ext.lower() not in ('.jpg','.jpeg','.jfif','.png','.webp','.avif','.heic','.bmp','.tif','.tiff'): continue
    m=re.match(r'^(.*?)(?:_(\d+))?$',nome.strip()); base,n=m.group(1).strip(),m.group(2)
    if base.upper() not in GR: res["sem_ref"].append(f); continue
    ref,gr=GR[base.upper()]
    try: im=abrir(os.path.join(src,f))
    except Exception as e: res["falha"].append(f"{f}: {e}"); continue
    tenis=gr=='Tênis'
    if im.getchannel('A').getextrema()[0]<20:  # já vem com fundo transparente: usa o recorte dela (o rembg estraga)
      a=np.array(im.getchannel('A'))
    else:
      if ses is None:
        from rembg import new_session, remove
        ses=new_session('isnet-general-use')
      a=np.array(remove(im,session=ses,only_mask=True))
    rgb=np.array(im.convert('RGB'))
    if tenis: mk=mascara_tenis(a,rgb)
    else:
      mk=ndi.binary_fill_holes(a>=160)
      mk=ndi.binary_erosion(mk,iterations=1)  # roupa clara em fundo cinza: recua mais um pouco
    if mk.sum()<100: res["falha"].append(f"{f}: não achei o produto na foto"); continue
    rgb,al=bordas(rgb,mk)
    ys,xs=np.where(al>8); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    rgb,al=rgb[y0:y1,x0:x1],al[y0:y1,x0:x1]
    if tenis and (ref in flip or (ref not in noflip and virado(al>128))): rgb,al=rgb[:,::-1],al[:,::-1]
    cut=Image.fromarray(rgb); cut.putalpha(Image.fromarray(np.ascontiguousarray(al)))
    if tenis: k=min(S*0.90/cut.width, S*0.55/cut.height)
    else: k=min(S*0.80/cut.width, S*0.80/cut.height)
    cut=cut.resize((round(cut.width*k),round(cut.height*k)),Image.LANCZOS)
    x=(S-cut.width)//2; y=round(S*0.71)-cut.height if tenis else (S-cut.height)//2-10
    A=np.array(cut.getchannel('A'))
    sh=sombra_tenis(A,x,y) if tenis else sombra_roupa(cut.width,x,y+cut.height)
    can=np.full((S,S,3),255,np.float32); cor=np.array([120,122,126],np.float32)
    can=can*(1-sh[...,None])+cor*sh[...,None]
    can=Image.fromarray(can.round().astype(np.uint8))
    can.paste(cut,(x,y),cut)
    out=ref+('_'+n if n else '')+'.jpg'
    can.save(os.path.join(dst,out),quality=90,subsampling=0); res["ok"].append({"arquivo":f,"foto":out,"grupo":gr})
  print(json.dumps(res,ensure_ascii=False))

if __name__=='__main__': main()
