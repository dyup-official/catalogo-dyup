# Gera teste-foto.html a partir do index.html: janela com a foto ampliada, só num produto, para aprovar o layout.
import re,sys,os
AQUI=os.path.dirname(os.path.abspath(__file__)); SITE=os.path.join(AQUI,'..')
REF=sys.argv[1] if len(sys.argv)>1 else 'WFCXLK5'
s=open(os.path.join(SITE,'index.html')).read()
css="""
/* Janela da foto ampliada */
.foto[data-zoom]{cursor:zoom-in}
.foto[data-zoom]:focus-visible{outline:2px solid var(--volt);outline-offset:-2px}
.lupa{position:absolute;right:12px;bottom:12px;z-index:1;width:34px;height:34px;border-radius:999px;background:var(--carbono);display:grid;place-items:center}
.lupa svg{width:17px;height:17px;fill:none;stroke:var(--volt);stroke-width:2.2;stroke-linecap:round}
dialog.zoom{border:0;padding:0;width:min(760px,calc(100% - 24px));max-height:calc(100% - 24px);border-radius:10px;overflow:hidden;background:var(--card);color:var(--fg)}
dialog.zoom::backdrop{background:rgba(16,24,32,.78)}
dialog.zoom[open]{animation:zin .18s ease-out}
@keyframes zin{from{opacity:0;transform:scale(.97)}}
.zoom .ft{position:relative;background:#fff;aspect-ratio:1/1;max-height:calc(100vh - 190px);width:100%}
.zoom .ft img{width:100%;height:100%;object-fit:contain;display:block}
.zoom .x{position:absolute;top:10px;right:10px;border:0;width:38px;height:38px;border-radius:999px;background:var(--carbono);color:var(--branco);font-size:20px;line-height:1;cursor:pointer}
.zoom .x:focus-visible{outline:2px solid var(--volt);outline-offset:2px}
.zoom .tx{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;padding:14px 16px 16px;border-top:1px solid var(--line)}
.zoom .tx h3{margin:2px 0 0;font-size:19px;line-height:1.15;letter-spacing:-.015em}
.zoom .preco{flex:none}
.teste{background:var(--volt);color:var(--carbono);font:600 13px/1.35 var(--sans);text-align:center;padding:10px 16px}
"""
s=s.replace('</style>',css+'</style>',1)
s=s.replace('<head>','<head>\n<meta name="robots" content="noindex">',1)
s=re.sub(r'(<body[^>]*>)',r'\1\n<div class="teste">Página de teste: toque na foto do primeiro produto (FuelCell Rebel v5 preto) para ver a janela com a foto ampliada.</div>',s,count=1)
dlg="""<dialog class="zoom" id="zoom" aria-labelledby="zoomT"><div class="ft"><img id="zoomImg" alt=""><button class="x" type="button" id="zoomX" aria-label="Fechar">×</button></div>
<div class="tx"><div><div class="mk" id="zoomM"></div><h3 id="zoomT"></h3><div class="cor" id="zoomC"></div></div><span class="preco" id="zoomP"></span></div></dialog>
"""
s=s.replace('<dialog class="car"',dlg+'<dialog class="car"',1)
old='<div class="foto${i.foto?" tem":""}">'
assert old in s
s=s.replace(old,'<div class="foto${i.foto?" tem":""}"${amplia(i)?` data-zoom="${i.id}" role="button" tabindex="0" aria-label="Ver foto maior"`:""}>',1)
old='<span class="ref">REF ${i.refs.join(" · ")}</span>'
s=s.replace(old,old+'\n        ${amplia(i)?`<span class="lupa" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21M10.5 7.5v6M7.5 10.5h6"/></svg></span>`:""}',1)
js="""
const GRANDE = %s;  // refs com foto grande em fotos/grande/
const amplia = i => !!i.foto && i.refs.some(r=>GRANDE.includes(r));
function abreZoom(id){ const i=ITENS.find(x=>x.id==id); if(!i) return;
  const r=i.refs.find(r=>GRANDE.includes(r)); $("zoomImg").src="fotos/grande/"+r+".jpg"; $("zoomImg").alt=`${i.marca} ${i.modelo} ${i.cor}`;
  $("zoomM").textContent=i.marca; $("zoomT").textContent=i.modelo; $("zoomC").textContent=i.cor; $("zoomP").textContent=brl(i.preco);
  $("zoom").showModal(); }
$("grade").addEventListener("click", e=>{ const f=e.target.closest("[data-zoom]"); if(f) abreZoom(f.dataset.zoom); });
$("grade").addEventListener("keydown", e=>{ const f=e.target.closest("[data-zoom]"); if(f&&(e.key==="Enter"||e.key===" ")){ e.preventDefault(); abreZoom(f.dataset.zoom); } });
$("zoomX").onclick=()=>$("zoom").close();
$("zoom").addEventListener("click", e=>{ if(e.target===$("zoom")) $("zoom").close(); });
""" % ('["%s"]'%REF)
s=s.replace('ITENS.forEach((i,n)=>{ i.id = n; });','ITENS.forEach((i,n)=>{ i.id = n; });'+js,1)
s=s.replace('  $("cont").textContent = L.length','  L.sort((a,b)=>amplia(b)-amplia(a));  // teste: o produto com foto grande vem primeiro\n  $("cont").textContent = L.length',1)
# o produto do teste vai para o começo da lista
m=re.search(r'const ITENS = (\[.*?\]);\n',s,re.S); import json; L=json.loads(m.group(1))
L.sort(key=lambda i: REF not in i['refs'])
s=s[:m.start(1)]+json.dumps(L,ensure_ascii=False)+s[m.end(1):]
open(os.path.join(SITE,'teste-foto.html'),'w').write(s); print('ok')
