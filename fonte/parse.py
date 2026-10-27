import pandas as pd,re,json,sys,unicodedata
f=sys.argv[1]
t=pd.read_html(f,header=None)
# Grupos que entram no site (o Linx exporta a loja inteira; o resto fica de fora)
GRUPOS=[("Tênis","TENIS"),("Camisetas","CAMISETAS?"),("Bermudas","BERMUDAS?"),("Calças","CALCAS?"),("Moletons","MOLETOM|MOLETONS"),
  ("Jaquetas","JAQUETAS?"),("Regatas","REGATAS?"),("Bonés","BONES?"),("Bolsas","BOLSAS?"),("Tops","TOPS?"),
  ("Garrafas","GARRAFAS?"),("Meias","MEIAS?"),
  # sinônimos do Linx
  ("Bermudas","SHORTS?"),("Camisetas","CAMISAS?"),("Bolsas","MOCHILAS?|RAQUETEIRAS?|THERMOBAGS?"),("Bonés","VISEIRAS?"),("Calças","LEGGINGS?")]
sem_acento=lambda s:unicodedata.normalize('NFD',s).encode('ascii','ignore').decode().upper()
def grupo(d):
  for nome,rx in GRUPOS:
    m=re.match(r'^('+rx+r')\b\s*',sem_acento(d))
    if m: return nome,m.end()
  return None,0
rows=[]
for x in t[1:]:
  for r in x.values.tolist():
    r=[str(v) for v in r]
    if re.match(r'^\d+(\.0)?$',r[0].strip()) and grupo(r[1])[0]:
      rows.append(r)
TAM=r'(\d+(?:[.,]5)?(?:/\d+)?|\d+-\d+|\d+\|\d+|T\d+|PP|P|M|G|GG|XG|XGG|EG|EGG|EXG|P/M|M/G|G/GG|U|UN|UNICO|ÚNICO)'
def preco(s):
  s=s.strip()
  if ',' in s: return float(s.replace('.','').replace(',','.'))
  return float(s)/100
out={}
for r in rows:
  d=re.sub(r'\s+',' ',r[1]).strip()
  gr,n=grupo(d)
  d=re.sub(r'(\s+(U|UN|UNIS|UNISSEX))+$',' UN',d) if gr!='Tênis' else d
  m=re.match(r'^(.*?)\s+'+TAM+r'$',d)
  base,tam=(m.group(1),m.group(2)) if m else (d,'Único')
  if tam.upper() in ('U','UN','UNICO','ÚNICO'): tam='Único'
  ref=r[2].strip()
  if ref.endswith('.0'): ref=ref[:-2]
  if ref.lower()=='nan': ref=''
  # roupas: a mesma ref do Linx pode ter várias cores, então a chave é ref + descrição
  g=out.setdefault(ref if gr=='Tênis' else (ref,base),{"ref":ref,"grupo":gr,"desc":base[n:].strip(),"tam":{},"preco":preco(r[6])})
  g["tam"][tam]=g["tam"].get(tam,0)+int(float(r[5]))
print(json.dumps(list(out.values()),ensure_ascii=False))
