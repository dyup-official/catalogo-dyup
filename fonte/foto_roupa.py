"""Foto de roupa/acessório no Branco Performance (#F8F7F2), mesmo tratamento dos tênis.
Diferença só no enquadramento: o produto cabe numa caixa de 80% x 80%, centralizado."""
import sys, numpy as np
from PIL import Image
try: import pillow_avif  # noqa
except ImportError: pass
from rembg import remove, new_session
BP=np.array([248,247,242],float); T=1000; CAIXA=0.80
def main(ent,sai,sess=None):
    im=Image.open(ent)
    transp = im.mode in ('RGBA','LA','P') and np.array(im.convert('RGBA'))[...,3].min()<20
    im=im.convert('RGBA'); w,h=im.size; L=max(w,h)
    rgb=np.array(im.convert('RGB')).astype(float)
    if transp: fundo=np.array([255.,255,255])
    else:
        c=np.concatenate([rgb[:10,:10].reshape(-1,3),rgb[:10,-10:].reshape(-1,3),rgb[-10:,:10].reshape(-1,3),rgb[-10:,-10:].reshape(-1,3)]); fundo=c.mean(0)
    q=Image.new('RGBA',(L,L),tuple(int(v) for v in fundo)+((0,) if transp else (255,)))
    q.paste(im,((L-w)//2,(L-h)//2)); q=q.resize((T,T),Image.LANCZOS)
    orig=np.array(q.convert('RGB')).astype(float)
    if transp:
        a=np.array(q)[...,3:4]/255.; orig=np.where(a>0,np.array(q)[...,:3],255).astype(float); sombra=1
    else:
        a=(np.array(remove(q.convert('RGB'),session=sess or new_session('isnet-general-use')))[...,3:4]/255.)
        sombra=1  # roupa: fundo liso, sem a sombra da foto original (evita manchas do fundo antigo)
    fin=orig*a+BP*sombra*(1-a)
    comp=Image.fromarray(fin.clip(0,255).astype('uint8'))
    ys,xs=np.where(a[...,0]>0.5); x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    if x0<=2 or x1>=T-3 or y0<=2 or y1>=T-3: print('ATENÇÃO',ent,'encosta na borda')
    k=min(CAIXA*T/(x1-x0),CAIXA*T/(y1-y0))
    n=comp.resize((round(T*k),)*2,Image.LANCZOS)
    tela=Image.new('RGB',(T,T),tuple(int(v) for v in BP))
    tela.paste(n,(round(T/2-(x0+x1)/2*k),round(T/2-(y0+y1)/2*k)))
    tela.save(sai,quality=92)
if __name__=='__main__': main(sys.argv[1],sys.argv[2])
