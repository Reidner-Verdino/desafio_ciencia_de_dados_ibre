"""
Etapa 2 - Gera os embeddings das notícias limpas.

Lê dados/noticias_limpas.json, codifica cada notícia (título + texto) com
o modelo paraphrase-multilingual-MiniLM-L12-v2 e salva os vetores em
dados/embeddings.npy.
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer


MODELO = "paraphrase-multilingual-MiniLM-L12-v2"


def main():
    with open("dados/noticias_limpas.json", encoding="utf-8") as f:
        noticias = json.load(f)

    # juntar título e texto - o título carrega muita informação em notícia econômica
    textos = [n["titulo"] + ". " + n["texto"] for n in noticias]

    print(f"Carregando modelo {MODELO}...")
    modelo = SentenceTransformer(MODELO)

    print(f"Gerando embeddings para {len(textos)} notícias...")
    # normalize_embeddings=True: assim a similaridade do cosseno = produto escalar
    embeddings = modelo.encode(textos, normalize_embeddings=True)

    np.save("dados/embeddings.npy", embeddings)
    print(f"Salvo em dados/embeddings.npy (shape {embeddings.shape})")


if __name__ == "__main__":
    main()
