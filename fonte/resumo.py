# Resumo para a página do botão: python3 resumo.py <linx.xls> ../index.html DD/MM/AAAA [publicado_em_ms] > resumo.json
import pandas as pd,re,json,sys,time
t=pd.read_html(sys.argv[1],header=None)
tot=None
for x in t[1:]:
  for r in x.values.tolist():
    if str(r[0]).strip()=='Total Geral': tot=[v for v in r if str(v)!='nan']
it=json.loads(re.search(r'const ITENS\s*=\s*(\[.*?\]);',open(sys.argv[2]).read(),re.S).group(1))
pub=int(sys.argv[4]) if len(sys.argv)>4 else int(time.time()*1000)
print(json.dumps({"data_saldo":sys.argv[3],"publicado_em":pub,"produtos_site":len(it),"com_foto":sum(1 for i in it if i.get('foto')),
  "pecas_loja":int(float(tot[1])) if tot else None,"valor_loja":"R$ "+str(tot[3]) if tot else None,"em":int(time.time()*1000)},ensure_ascii=False))
