"""
Etapa 1 - Limpeza dos textos.

Lê dados/noticias_brutas.json, limpa o campo `texto` e salva em
dados/noticias_limpas.json mantendo a mesma estrutura.
"""

import json
import html
import re
from bs4 import BeautifulSoup


def limpar(texto):
    # tira as tags HTML (BS4 lida bem com tags aninhadas e atributos)
    texto = BeautifulSoup(texto, "html.parser").get_text(separator=" ")

    # decodifica entidades: &eacute; -> é, &ccedil; -> ç, &nbsp; -> espaço, etc.
    texto = html.unescape(texto)

    # remove timestamps do tipo "Publicado em: ..."
    texto = re.sub(r"Publicado em:?\s*", "", texto, flags=re.IGNORECASE)

    # remove a data (com hora opcional e qualquer "seção/fonte" depois)
    # cobre os formatos: "02/08/2023 às 20h15", "23/08/2023 - 18h45 | Mercados",
    # "30/08/2023 — FGV IBRE", "07/08/2023" sozinho
    texto = re.sub(
        r"\d{1,2}/\d{1,2}/\d{2,4}"
        r"(\s*(?:às|as)\s*\d{1,2}h\d{0,2})?"
        r"(\s*[-–—|]\s*[\wÀ-ú ]{0,30})*",
        "",
        texto,
        flags=re.IGNORECASE,
    )

    # normaliza espaços (várias quebras de linha e espaços viram um só)
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def main():
    with open("dados/noticias_brutas.json", encoding="utf-8") as f:
        noticias = json.load(f)

    for n in noticias:
        n["texto"] = limpar(n["texto"])

    with open("dados/noticias_limpas.json", "w", encoding="utf-8") as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)

    print(f"{len(noticias)} notícias limpas. Salvo em dados/noticias_limpas.json")


if __name__ == "__main__":
    main()
