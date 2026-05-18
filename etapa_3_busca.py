"""
Etapa 3 - Motor de busca semântico.

Carrega os embeddings, recebe uma consulta em texto livre e retorna os
artigos mais relevantes do corpus.

Quando rodado direto, executa as 3 queries de validação do enunciado.
"""

import json
import sys
import numpy as np
from sentence_transformers import SentenceTransformer


MODELO = "paraphrase-multilingual-MiniLM-L12-v2"

QUERIES_VALIDACAO = [
    "mudanças na taxa de juros",
    "mercado de trabalho e desemprego",
    "inflação e preços ao consumidor",
]


def buscar(query, modelo, noticias, embeddings, top_k=5):
    # mesma codificação dos documentos (e mesma normalização)
    emb_query = modelo.encode([query], normalize_embeddings=True)[0]

    # produto escalar = similaridade do cosseno (vetores já normalizados)
    scores = embeddings @ emb_query

    # pega os índices dos top_k em ordem decrescente
    top = np.argsort(-scores)[:top_k]

    return [(float(scores[i]), noticias[i]) for i in top]


def imprimir(query, resultados):
    print(f'\nConsulta: "{query}"')
    print("-" * 70)
    for score, n in resultados:
        print(f"  [{score:.3f}] ID {n['id']} — {n['titulo']}")


def main():
    with open("dados/noticias_limpas.json", encoding="utf-8") as f:
        noticias = json.load(f)
    embeddings = np.load("dados/embeddings.npy")

    print(f"Carregando modelo {MODELO}...")
    modelo = SentenceTransformer(MODELO)

    # se o usuário passar uma query como argumento, busca só essa; senão, as 3 do enunciado
    if len(sys.argv) > 1:
        queries = [" ".join(sys.argv[1:])]
    else:
        queries = QUERIES_VALIDACAO

    for q in queries:
        resultados = buscar(q, modelo, noticias, embeddings)
        imprimir(q, resultados)


if __name__ == "__main__":
    main()
