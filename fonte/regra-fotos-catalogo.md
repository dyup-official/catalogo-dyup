# Regra · Fotos de produto do catálogo DYUP

## Padrão
- Fundo Branco Performance, #F8F7F2.
- Foto quadrada, 1000 × 1000 px.
- Enquadramento igual em todas as fotos, feito pelo script. O produto ocupa 86% da largura, centralizado, com a base da sola sempre na mesma altura. Não ajustar à mão.
- Sombra só a da própria foto. Nunca criar sombra nova.

## Ordem das fotos (24/11/2026)
Seja qual for o nome do arquivo salvo na pasta, a ordem no site é:
1. Capa: bico para a direita.
2. Bico para a esquerda.
3. Solado.
4. Traseira, se tiver.

## Como fazer
1. Usar a foto original da marca, do jeito que foi baixada. Não editar antes.
2. Na primeira vez, instalar o recortador: `pip install "rembg[cpu]"`.
3. Rodar o script `foto_catalogo.py` em cada foto: `python foto_catalogo.py entrada.jpg saida.jpg`.
4. Conferir a borda da sola e do calcanhar ampliando a imagem. Se sobrar contorno do fundo antigo ou faltar pedaço do produto, não corrigir à mão. Avisar o Leonardo e deixar a foto de fora até resolver.

## O que nunca fazer
- Recortar por código próprio (seleção por cor, contorno, varinha). O tênis tem partes da mesma cor do fundo, e esse recorte sai serrilhado.
- Reduzir a foto para menos de 1000 px.
- Adicionar sombra, reflexo ou efeito.
