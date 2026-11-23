# Rotina de atualização do catálogo DYUP

Pastas no computador da loja (C:\Users\User\Desktop\CLAUDE DYUP\Estoque-Catalogo DYUP):
- `ESTOQUE LINX\` planilha ExportacaoRegistroInventario*.xls (pega a de maior mtimeMs; olhar também a raiz)
- `REVISAO DE PRODUTOS.xlsx` planilha de revisão: coluna "Excluir?" tira o produto do site, "Trocar foto?" pede foto nova
- `FOTOS NOVAS\` fotos com o nome = referência do Linx (REF.jpg, REF_2.png ...)
- `fotos-padrao\` cópia das fotos já padronizadas

Controle do que já foi processado (em /mnt/project-files/catalogo/):
`ultimo-estoque.json` (planilha do Linx), `ultima-revisao.json` ({mtimeMs}), `ultimas-fotos.json` ([{nome, mtimeMs}]).

Passos (só segue se algo for novo; senão termina em silêncio):
1. `git pull -q origin main`. Traga com device_stage_files a planilha do Linx (a nova, ou a última processada se só mudou revisão/foto),
   a REVISAO DE PRODUTOS.xlsx e as fotos novas/alteradas.
2. `python3 revisao.py ler "<revisao.xlsx>"` grava excluir-revisao.txt.
3. `python3 parse.py "<linx.xls>" > raw.json`
4. Fotos: copie as novas para uma pasta vazia e rode `python3 fotos.py <pasta> /mnt/project-files/catalogo/fotos-padrao raw.json`. Tênis: refaça com foto_catalogo.py (ver padrão das fotos de tênis abaixo) por cima da saída do fotos.py.
   Saída: ok / sem_ref (nome não bate com referência: não publica e avisa) / falha. Confira as fotos geradas olhando a imagem.
   Grave a lista de refs publicadas (sem o _2) num json para o passo 6. Envie as fotos geradas para `fotos-padrao\` no computador.
5. `SITE=.. python3 build.py DD/MM/AAAA` (data do cabeçalho da planilha do Linx); `rm -f raw.json`. Compare o ITENS antes e depois.
6. `python3 revisao.py atualizar "<revisao.xlsx>" <saida.xlsx> ../index.html <refs_publicadas.json>` e grave a saída de volta em
   REVISAO DE PRODUTOS.xlsx com expectedMtimeMs da cópia lida (se rejeitar porque a pessoa mexeu ou está com o arquivo aberto, avise).
7. Commit (dyup-official) e push; copie os arquivos da fonte alterados para /mnt/project-files/catalogo/; atualize os três json de controle
   (o mtime da revisão é o do arquivo depois de gravado).
8. Responda em português, em poucas linhas: data do estoque, o que entrou/saiu/mudou, fotos publicadas, pendências.

Andamento na página do botão (https://claude.ai/artifact/1NE66C7ER1rxpLo77TgfyW), só em cliques do botão:
o documento `status/atual` do banco do artefato (ArtifactData, url do artefato) mostra o estado para o Leonardo.
- Ao começar: update `{estado:"processando", em:<agora ms>}` (com if_version lido no get).
- Ao terminar: `{estado:"pronto", em, texto:"<data do estoque e resumo em 1-2 linhas>"}`, ou `estado:"sem_novidade"`,
  ou `estado:"erro"` com o motivo (ex.: computador da loja não respondeu; planilha aberta).
- Se o computador estiver fora num clique: grave `erro` com "O computador da loja não respondeu. Tente de novo mais tarde."

Resumo na página do botão (só editores veem), em toda rotina que publicar (agendada ou botão):
`python3 resumo.py "<linx.xls>" ../index.html DD/MM/AAAA <ms do push> > <scratch>/resumo.json` e ArtifactData set em `resumo/atual`
(file_path, com if_version lido no get). Peças e valor vêm do "Total Geral" do Linx (loja inteira, preço de venda).

O painel precisa ficar privado (só o dono): público, o db_write recusa (public_audience). Hoje grava-se com mcp__claude-artifacts__db_get/db_write (slug 02f6af4d-e9a5-489b-a81c-ada65c3df71d, ifVersion).
Gravar no computador: device_commit_files com `stagedPath` (caminho em /mnt/project-files) e `fileUuid: ""`; só fileUuid dá 404.

Limpeza no clique do botão (pedido do Leonardo em 10/11/2026), depois de publicar:
- ESTOQUE LINX: manter só a planilha .xls mais recente (por mtime), a que acabou de ser processada; apagar todas as outras (pedido do Leonardo em 12/11/2026).
- FOTOS NOVAS: apagar as fotos já publicadas (as que estão em ultimas-fotos.json e cuja versão tratada está em fotos-padrao). Nunca LEIA-ME.txt.
- Só apaga se houver ferramenta de apagar no computador (device_bash); sem ela, deixa para o próximo clique.

Painel com o site (pedido do Leonardo em 23/11/2026): o artefato do botão (02f6af4d) mostra o painel em cima e uma cópia do site embaixo para ele comentar.
Depois de todo push que muda o site: `python3 painel/monta.py /home/claude/catalogo-dyup <scratch>/painel-catalogo.html DD/MM/AAAA` e
publish_files do arquivo como index.html no slug 02f6af4d (base_version do get_artifact). Comentários feitos no site viram pedidos de mudança no site real.

## Descrições de produto e página de produto (desde 23/11/2026)
- Nomes de tecnologia, espuma, placa, cabedal e solado ficam exatamente como no site da marca (com ™/®, sem traduzir: "Engineered mesh upper", "FF BLAST™ MAX cushioning"). Só o texto de ligação fica em português. Pedido do Leonardo em 23/11/2026.
- Se o site da marca não tiver algum dado da ficha, pesquisar em lojas e reviews especializados (Running Warehouse, Fleet Feet, RunRepeat, REI) e anotar a fonte no campo obs. Só deixar "—" se nenhuma fonte confiável trouxer o dado. Pedido do Leonardo em 23/11/2026.
- Cada produto tem página própria no site (#p/marca-modelo-cor), com galeria, cores, tamanhos, descrição e ficha técnica.
- Descrições ficam no painel 02f6af4d, coleção `descricoes` (id = slug de marca + modelo; status pendente/aprovado; aprovado_em, publicado_em).
- Produto novo no site (modelo sem doc em `descricoes`): buscar dados SÓ no site oficial da marca, escrever no padrão (Descrição 2–3 frases, Indicado para, Ficha: Amortecimento, Pisada, Drop, Peso, Entressola, Cabedal, Solado; "—" quando a marca não informa), gravar como "pendente" com fontes, e avisar o Leonardo.
- Botão "Publicar aprovadas no site" (comentário do painel): copiar as aprovadas para `fonte/descricoes.json` (campos do site + aprovado_em), rodar o build, push, gravar publicado_em em cada doc (status continua "aprovado") e remontar o painel.
- Fotos extras: REF_2.jpg, REF_3.jpg... em fotos-padrao entram como galeria na página do produto.
- Padrão das fotos de tênis (desde 23/11/2026, regra do Leonardo em fonte/regra-fotos-catalogo.md): rodar `python3 foto_catalogo.py <original> <saida.jpg>` em cada tênis (recorte rembg isnet-general-use, fundo branco DYUP #F8F7F2, só a sombra da foto original, tênis com 86% da largura, sola a 74% da altura, 1000 px). Instalar uma vez: `python3 -m pip install "rembg[cpu]"`. Bico para a direita: se vier para a esquerda, espelhar. Conferir borda da sola e calcanhar; se sobrar fundo antigo ou faltar pedaço, não corrigir à mão: avisar o Leonardo e deixar a foto de fora. Nunca recorte por cor/contorno próprio nem sombra nova. Roupas e acessórios seguem no fotos.py (fundo branco com sombra). Pendentes em 23/11: HM6803-005 (fundo degradê) e HV8154-100 (mancha no calcanhar) seguem com a foto anterior.
