# Catálogo DYUP

Catálogo de tênis da DYUP (Rua Cambira, 447 · Maringá · PR), publicado pelo GitHub Pages.

## O que tem aqui

- `index.html`: o catálogo que os clientes abrem.
- `pedido.html`: a página do pedido. O cliente envia o link pelo WhatsApp e a loja abre o pedido com fotos, tamanhos, valores e o botão de PDF.
- `fotos/`: uma foto por referência (`REF.jpg`).
- `img/`: logo, ícone e grafismo da marca.
- `fonte/`: os scripts que geram o site a partir do estoque da Linx.

## Atualização diária

1. Baixe o estoque da Linx (`ExportacaoRegistroInventario.xls`) na pasta `Estoque-Catalogo DYUP`.
2. Peça ao Claude no projeto para atualizar o catálogo.
3. Ele gera o site e envia um commit para cá. O GitHub Pages publica sozinho em cerca de 1 minuto.

Cada atualização fica no histórico de commits, então dá para ver ou voltar qualquer versão anterior.
