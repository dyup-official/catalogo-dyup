"""
Foto de produto do catálogo DYUP no Branco Performance.

Uso:
    pip install "rembg[cpu]"
    python foto_catalogo.py entrada.jpg saida.jpg

O que faz:
1. Recorta o produto com o modelo isnet-general-use (rembg).
2. Coloca o produto no Branco Performance (#F8F7F2).
3. Mantém a sombra da foto original, sem inventar sombra nova.
4. Padroniza o enquadramento: o produto ocupa 86% da largura, centralizado,
   com a base da sola sempre na mesma altura (74% da foto).
5. Salva em 1000 x 1000 px.

Funciona melhor com foto de fundo liso (cinza ou branco), como as fotos oficiais das marcas.
"""
import sys
import numpy as np
from PIL import Image
from rembg import remove, new_session

BRANCO_PERFORMANCE = np.array([248, 247, 242], dtype=float)
TAMANHO = 1000
LARGURA_PRODUTO = 0.86
BASE_SOLA = 0.74


def quadrado(img, cor):
    w, h = img.size
    lado = max(w, h)
    base = Image.new("RGB", (lado, lado), cor)
    base.paste(img, ((lado - w) // 2, (lado - h) // 2))
    return base


def main(entrada, saida):
    foto = Image.open(entrada).convert("RGB")
    # cor do fundo original, lida nos cantos
    arr0 = np.array(foto).astype(float)
    cantos = np.concatenate([arr0[:10, :10].reshape(-1, 3), arr0[:10, -10:].reshape(-1, 3),
                             arr0[-10:, :10].reshape(-1, 3), arr0[-10:, -10:].reshape(-1, 3)])
    fundo = cantos.mean(0)
    foto = quadrado(foto, tuple(int(v) for v in fundo))
    if foto.size[0] != TAMANHO:
        foto = foto.resize((TAMANHO, TAMANHO), Image.LANCZOS)

    recorte = remove(foto, session=new_session("isnet-general-use"))
    alfa = (np.array(recorte.split()[3]).astype(float) / 255)[..., None]

    original = np.array(foto).astype(float)
    # sombra: quanto a foto escurece em relação ao fundo original
    sombra = np.clip(original.mean(2, keepdims=True) / fundo.mean(), 0, 1)
    novo_fundo = BRANCO_PERFORMANCE * sombra

    final = original * alfa + novo_fundo * (1 - alfa)
    composta = Image.fromarray(final.clip(0, 255).astype("uint8"))

    # enquadramento padrão, medido pelo contorno do produto
    ys, xs = np.where(alfa[..., 0] > 0.5)
    x0, x1, y1 = xs.min(), xs.max(), ys.max()
    if x0 <= 2 or x1 >= TAMANHO - 3 or ys.min() <= 2 or y1 >= TAMANHO - 3:
        print(f"ATENÇÃO {entrada}: o produto encosta na borda da foto original e pode estar cortado. Procure outra foto.")
    escala = (LARGURA_PRODUTO * TAMANHO) / (x1 - x0)
    nova = composta.resize((round(TAMANHO * escala), round(TAMANHO * escala)), Image.LANCZOS)
    cx = (x0 + x1) / 2 * escala
    dx = round(TAMANHO / 2 - cx)
    dy = round(BASE_SOLA * TAMANHO - y1 * escala)
    tela = Image.new("RGB", (TAMANHO, TAMANHO), tuple(int(v) for v in BRANCO_PERFORMANCE))
    tela.paste(nova, (dx, dy))
    tela.save(saida, quality=92)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
