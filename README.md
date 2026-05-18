# Motor de busca semântico: notícias econômicas

Está é uma solução do desafio técnico para estágio em ciência de dados no FGV IBRE, conforme pedido. Construí um pequeno motor de busca semântico sobre 20 notícias fictícias da economia brasileira.

O pipeline está em três scripts numerados, um para cada etapa do enunciado.


## Como rodar

Precisa de Python 3.10+.

```bash
pip install -r requirements.txt

python etapa1_limpeza.py
python etapa2_embeddings.py
python etapa3_busca.py
```

Na primeira execução da etapa 2, o `sentence-transformers` baixa o modelo (~120MB) do HuggingFace.

Para buscar uma consulta qualquer (em vez das três do enunciado):

```bash
python etapa3_busca.py "câmbio e dólar"
```


## Estrutura

```
.
├── etapa1_limpeza.py        # limpa o campo texto das notícias brutas
├── etapa2_embeddings.py     # gera os vetores
├── etapa3_busca.py          # roda as buscas
├── requirements.txt
└── dados/
    ├── noticias_brutas.json
    └── noticias_limpas.json
```

## Decisões

### Limpeza

Usei `BeautifulSoup` para tirar as tags HTML, escolhi ele em vez de regex porque lida melhor com tags e atributos. Depois `html.unescape` para decodificar as entidades (`&eacute;` → `é`, `&ccedil;` → `ç`, etc.).

Para os timestamps embutidos no texto, dois regex:
- um para o prefixo `Publicado em:`
- outro para a data em si, com hora opcional e qualquer "seção/fonte" que venha depois (cobre `"02/08/2023 às 20h15"`, `"23/08/2023 - 18h45 | Mercados"`, `"30/08/2023 — FGV IBRE"` e o caso da data sozinha)

Confirmei antes que nenhuma notícia tem uma data DD/MM/AAAA legítima no corpo do texto pois todas as ocorrências desse formato são timestamps, então remover é seguro.

Por fim, normalizei os espaços (várias quebras de linha viram uma só).

Mantive a estrutura original dos campos no JSON limpo. A notícia de ID 18 (que tem só `"Selic."` no corpo) sobreviveu propositalmente pois preferi não filtrar nada na limpeza e deixar a busca lidar com isso.


### Modelo de embeddings

Escolhi `paraphrase-multilingual-MiniLM-L12-v2`. Os motivos:

1. **Multilíngue com bom português.** Treinado em 50+ idiomas com pares paralelos, funciona bem em PT-BR.
2. **Leve.** ~118MB, roda confortavelmente em CPU. Importa para reprodutibilidade, onde quem clonar o repo consegue rodar sem GPU.
3. **Boa qualidade em similaridade semântica.** Performance sólida nos benchmarks de STS multilíngue.

Considerei também o `distiluse-base-multilingual-cased-v1`, que é maior (~480MB) com qualidade comparável. Para um corpus pequeno e um projeto pedagógico, o ganho não compensa o tamanho.

Codifico cada notícia como `título + ". " + texto` — o título carrega muita informação semântica nesse domínio. E uso `normalize_embeddings=True` para que a similaridade do cosseno seja só um produto escalar.


### Busca

Direto: codifico a consulta com o mesmo modelo, calculo o produto escalar com todos os documentos, ordeno decrescente, retorno os top-5.


## Avaliação dos resultados

Rodei as três queries do enunciado. Resumindo:

**"mudanças na taxa de juros"**
Os primeiros resultados foram as notícias do Copom (IDs 1, 6 e 11, que falam de manter, cortar e projetar a Selic) e a ID 5 sobre o Fed/Powell. Achei interessante a ID 5 ter aparecido bem ranqueada mesmo sem citar "Selic" explicitamente — é exatamente o tipo de match que justifica usar busca semântica em vez de palavra-chave.

**"mercado de trabalho e desemprego"** 
Os IDs 4 e 14 (taxa de desemprego geral e desemprego juvenil) lideraram com folga. Resultado bem direto, é o que se espera.

**"inflação e preços ao consumidor"**
O ID 2 ficou em primeiro, faz sentido porque IPCA é literalmente "Índice Nacional de Preços ao Consumidor Amplo". Vieram em seguida a ID 9 (inflação ao produtor) e a ID 16 (IGP-M, deflação).

Uma observação: a ID 18 ("Nota curta", corpo só com `"Selic."`) às vezes aparece nos resultados de queries sobre juros com score relativamente alto. É um caso onde algum filtro de comprimento mínimo ajudaria em um cenário real, então deixei sem filtro porque o desafio menciona explicitamente que os casos extremos existem de propósito, e fica mais fácil de auditar o comportamento sem mascarar.
