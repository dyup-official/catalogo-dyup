# Rotina de atualização do catálogo DYUP

Pastas no computador da loja (C:\Users\User\Desktop\Estoque-Catalogo DYUP):
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
4. Fotos: copie as novas para uma pasta vazia e rode `python3 fotos.py <pasta> /mnt/project-files/catalogo/fotos-padrao raw.json`.
   Saída: ok / sem_ref (nome não bate com referência: não publica e avisa) / falha. Confira as fotos geradas olhando a imagem.
   Grave a lista de refs publicadas (sem o _2) num json para o passo 6. Envie as fotos geradas para `fotos-padrao\` no computador.
5. `SITE=.. python3 build.py DD/MM/AAAA` (data do cabeçalho da planilha do Linx); `rm -f raw.json`. Compare o ITENS antes e depois.
6. `python3 revisao.py atualizar "<revisao.xlsx>" <saida.xlsx> ../index.html <refs_publicadas.json>` e grave a saída de volta em
   REVISAO DE PRODUTOS.xlsx com expectedMtimeMs da cópia lida (se rejeitar porque a pessoa mexeu ou está com o arquivo aberto, avise).
7. Commit (dyup-official) e push; copie os arquivos da fonte alterados para /mnt/project-files/catalogo/; atualize os três json de controle
   (o mtime da revisão é o do arquivo depois de gravado).
8. Responda em português, em poucas linhas: data do estoque, o que entrou/saiu/mudou, fotos publicadas, pendências.
