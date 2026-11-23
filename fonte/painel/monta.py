# Monta o painel do botão (artefato 02f6af4d) = topo do painel + cópia do site com fotos embutidas.
# Uso: python3 monta.py <repo catalogo-dyup> <saida.html> DD/MM/AAAA
import re,base64,os,sys
repo,saida,data=sys.argv[1:4]
D=os.path.dirname(os.path.abspath(__file__))
h=open(os.path.join(repo,'index.html')).read().replace('fotos/grande/','fotos/')
cache={}
def rep(m):
    p=os.path.join(repo,m.group(0))
    if not os.path.exists(p): return m.group(0)
    if p not in cache:
        mt='image/png' if p.endswith('.png') else 'image/jpeg'
        cache[p]=f"data:{mt};base64,"+base64.b64encode(open(p,'rb').read()).decode()
    return cache[p]
h=re.sub(r'(?:fotos|img)/[A-Za-z0-9._-]+\.(?:jpg|png)',rep,h)
topo=open(os.path.join(D,'topo.html')).read().replace('__DATA__',data)
scr=open(os.path.join(D,'script.html')).read()
i=h.index('<header class="marca">'); h=h[:i]+topo+'\n'+h[i:]
j=h.rindex('</html>'); h=h[:j]+scr+'\n'+h[j:]
open(saida,'w').write(h); print(round(len(h)/1e6,2),'MB',len(cache),'imagens')
