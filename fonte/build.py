import json,base64,re,sys,glob,os,shutil
# Gera o site do catálogo (GitHub Pages) na pasta SITE: index.html, pedido.html, fotos/ e img/
SITE=os.environ.get('SITE','site')
os.makedirs(os.path.join(SITE,'fotos'),exist_ok=True); os.makedirs(os.path.join(SITE,'img'),exist_ok=True)
from hc import HC,NOMES
A=os.path.dirname(glob.glob('/root/.claude/skills/**/dyup-posts/assets/logo-volt.png',recursive=True)[0])
raw=json.load(open('raw.json'))
DATA_SALDO=sys.argv[1]
MOD=[ # (marca, prefixo na descrição, nome, categoria)
("ASICS","GEL NIMBUS 27 TR","Gel-Nimbus 27 TR","Corrida"),
("ASICS","GEL NIMBUS 27 LUXE","Gel-Nimbus 27 Luxe","Corrida"),
("ASICS","NIMBUS 28","Gel-Nimbus 28","Corrida"),
("ASICS","SOLUTION SPEED FF 4 CLAY","Solution Speed FF 4 Clay","Quadra"),
("ASICS","SOLUTION SPEED FF 4","Solution Speed FF 4","Quadra"),
("ASICS","SOLUTION SPEED FF 3 CLAY","Solution Speed FF 3 Clay","Quadra"),
("ASICS","NETBURNER BALLISTIC FF 4","Netburner Ballistic FF 4","Quadra"),
("ASICS","SONICBLAST","Sonicblast","Corrida"),
("ASICS","GEL-CUMULUS 28","Gel-Cumulus 28","Corrida"),
("ASICS","NOVABLAST 6","Novablast 6","Corrida"),
("ASICS","S4+ YOGIRI","S4+ Yogiri","Corrida"),
("ASICS","SUPERBLAST 3","Superblast 3","Corrida"),
("ASICS","GEL-RESOLUTION X CLAY","Gel-Resolution X Clay","Quadra"),
("ASICS","RESOLUTION X","Gel-Resolution X","Quadra"),
("ASICS","GEL-CHALLENGER 15 CLAY","Gel-Challenger 15 Clay","Quadra"),
("ASICS","COURT FF 3 CLAY","Court FF 3 Clay","Quadra"),
("ASICS","GAME FF CLAY/OC","Game FF Clay/OC","Quadra"),
("ASICS","GEL GAME 9 GS","Gel-Game 9 GS","Infantil"),
("ASICS","GEL-GAME GS","Gel-Game GS","Infantil"),
("ASICS","UPCOURT 6 GS","Upcourt 6 GS","Infantil"),
("HOKA","SKYFLOW","Skyflow","Corrida"),
("HOKA","CLIFTON 10","Clifton 10","Corrida"),
("HOKA","CLIFTON PRO","Clifton Pro","Corrida"),
("HOKA","MACH7","Mach 7","Corrida"),
("HOKA","CIELO X1 3.0","Cielo X1 3.0","Corrida"),
("HOKA","SPEEDGOAT 7","Speedgoat 7","Trail"),
("NIKE","INITIATOR","Initiator","Casual"),
("NIKE","FREE METCON 6","Free Metcon 6","Treino"),
("NIKE","COURT LITE 4 CLY","Court Lite 4 Clay","Quadra"),
("NIKE","VOMERO 18","Vomero 18","Corrida"),
("NIKE","VOMERO PLUS","Vomero Plus","Corrida"),
("NEW BALANCE","INFINION 1080 V15","1080 v15","Corrida"),
("NEW BALANCE","1080 V15 INFINION","1080 v15","Corrida"),
("NEW BALANCE","INFINION SUPERCOMP REBEL","SuperComp Rebel","Corrida"),
("NEW BALANCE","FUELCELL REBEL V5","FuelCell Rebel v5","Corrida"),
("NEW BALANCE","REBEL V5","FuelCell Rebel v5","Corrida"),
("NEW BALANCE","FRESH FOAM X KAIHA ROAD V2","Fresh Foam X Kaiha Road v2","Corrida"),
("NEW BALANCE","KAIHA ROAD V2","Fresh Foam X Kaiha Road v2","Corrida"),
("NEW BALANCE","530","530","Casual"),
("NEW BALANCE","FRESH FOAM X 1080 V14","Fresh Foam X 1080 v14","Corrida"),
("NEW BALANCE","FRESH FOAM X MORE V6","Fresh Foam X More v6","Corrida"),
]
AQUI=os.path.dirname(os.path.abspath(__file__))
EXC=set(l.strip() for l in open(os.environ.get('EXCLUIR',os.path.join(AQUI,'excluir.txt'))) if l.strip() and not l.startswith('#'))
def emb(f,ref):  # foto leve para o site: 640 px, JPEG 82, em fotos/REF.jpg
  from PIL import Image
  dst=os.path.join(SITE,'fotos',ref+'.jpg')
  if not os.path.exists(dst) or os.path.getmtime(dst)<os.path.getmtime(f):
    im=Image.open(f).convert('RGB'); im.thumbnail((640,640)); im.save(dst,'JPEG',quality=82,optimize=True)
  return 'fotos/'+ref+'.jpg'
itens={};falhas=[]
for g in raw:
  if g['ref'] in EXC: continue
  d=g['desc']
  if d.startswith('NB '): d='NEW BALANCE '+d[3:]
  marca=next(m for m in ['NEW BALANCE','ASICS','HOKA','NIKE'] if d.startswith(m))
  resto=d[len(marca):].strip()
  hit=None
  for m,p,n,c in MOD:
    if m==marca and (resto==p or resto.startswith(p+' ') or resto.startswith(p+'/')): hit=(p,n,c);break
  if not hit: falhas.append(d);continue
  cor=resto[len(hit[0]):].strip(' -/')
  cor=re.sub(r'\s*/\s*',' / ',cor).replace('ESCU RO','ESCURO')
  # HOKA Cielo vem com uma referência por tamanho: junta no mesmo item
  ref=g['ref']; key=(marca,hit[1],cor,g['preco'])
  it=itens.setdefault(key,{"marca":marca,"modelo":hit[1],"cat":hit[2],"cor":cor or "",
     "refs":[], "preco":g['preco'],"tam":{}})
  it['refs'].append(ref)
  for t,q in g['tam'].items(): it['tam'][t]=it['tam'].get(t,0)+q
if falhas: print("SEM MODELO:",falhas,file=sys.stderr); sys.exit(1)
L=[]
for it in itens.values():
  it['tam']=dict(sorted(it['tam'].items(),key=lambda kv:float(kv[0].replace(',','.'))))
  it['pares']=sum(it['tam'].values())
  it['hc']=HC.get(it['modelo'],([],''))[0]
  # fotos padronizadas do projeto, se existirem; senão usa as que já estão publicadas no site
  FOT=os.environ.get('FOTOS','/mnt/project-files/catalogo/fotos-padrao')
  it['foto']=next((emb(os.path.join(FOT,r+'.jpg'),r) for r in it['refs'] if os.path.exists(os.path.join(FOT,r+'.jpg'))),'') \
    or next(('fotos/'+r+'.jpg' for r in it['refs'] if os.path.exists(os.path.join(SITE,'fotos',r+'.jpg'))),'')
  if not it['foto']: print('SEM FOTO:',it['marca'],it['modelo'],it['cor'],it['refs'],file=sys.stderr)
  if it['cat']=='Corrida' and not it['hc'] and it['modelo'] not in ('Speedgoat 7',): print('SEM HC:',it['modelo'],file=sys.stderr)
  it['tam']=list(it['tam'])  # sem quantidade: o catálogo vai para clientes
  it.pop('pares')
  L.append(it)
# data em que cada referência apareceu pela primeira vez no estoque (para ordenar por "Mais novos")
ENT_F=os.path.join(AQUI,'entrada.json'); ENT=json.load(open(ENT_F)) if os.path.exists(ENT_F) else {}
d,m,a=DATA_SALDO.split('/'); HOJE=f'{a}-{m}-{d}'
for it in L:
  for r in it['refs']: ENT.setdefault(r,HOJE)
  it['ent']=min(ENT[r] for r in it['refs'])
json.dump(dict(sorted(ENT.items())),open(ENT_F,'w'),indent=0,ensure_ascii=False)
L.sort(key=lambda i:(i['marca'],i['modelo'],i['cor']))
for f in ('logo-volt.png','logo-carbono.png','circuito.png'): shutil.copy(os.path.join(A,f),os.path.join(SITE,'img',f))
from PIL import Image
ic=Image.new('RGB',(192,192),(16,24,32)); lg=Image.open(os.path.join(A,'logo-volt.png')).convert('RGBA'); lg.thumbnail((160,160)); ic.paste(lg,((192-lg.width)//2,(192-lg.height)//2),lg); ic.save(os.path.join(SITE,'img','icone.png'))
html=open(os.path.join(AQUI,'template.html')).read()
html=html.replace('__DADOS__',json.dumps(L,ensure_ascii=False)).replace('__SALDO__',DATA_SALDO).replace('__HCNOMES__',json.dumps(NOMES,ensure_ascii=False))
html='<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'+html+'\n</html>\n'
open(os.path.join(SITE,'index.html'),'w').write(html)
shutil.copy(os.path.join(AQUI,'pedido.html'),os.path.join(SITE,'pedido.html'))
open(os.path.join(SITE,'.nojekyll'),'w').close()
print(len(L),"itens")
