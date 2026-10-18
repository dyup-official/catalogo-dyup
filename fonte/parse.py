import pandas as pd,re,json,sys
f=sys.argv[1]
t=pd.read_html(f,header=None)
rows=[]
for x in t[1:]:
  for r in x.values.tolist():
    r=[str(v) for v in r]
    if re.match(r'^\d+(\.0)?$',r[0].strip()) and r[1].startswith('TÊNIS'):
      rows.append(r)
def preco(s):
  s=s.strip()
  if ',' in s: return float(s.replace('.','').replace(',','.'))
  return float(s)/100
out={}
for r in rows:
  d=re.sub(r'\s+',' ',r[1]).strip()
  m=re.match(r'^(.*?)\s+([\d]+(?:[.,]5)?)$',d); base,tam=m.group(1),m.group(2)
  ref=r[2].strip()
  if ref.endswith('.0'): ref=ref[:-2]
  g=out.setdefault(ref,{"ref":ref,"desc":base[6:],"tam":{},"preco":preco(r[6])})
  g["tam"][tam]=g["tam"].get(tam,0)+int(float(r[5]))
print(json.dumps(list(out.values()),ensure_ascii=False))
