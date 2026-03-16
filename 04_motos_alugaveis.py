# sandbox.py — rascunho de queries, não sobe pro git
from bigquery_client import *

query_validacao = """
SELECT
    atualizacaoData,
    filial,
    moto_0km          AS tipo_moto,
    SUM(qtd)          AS motos_alugaveis
FROM
    `dm-mottu-aluguel.exp_frota.frota_historico_agrupado`
WHERE
    pais                   = 'Brasil'
    AND tipo_situacao_detalhe LIKE '05-%'
    AND atualizacaoData     >= DATE_SUB(CURRENT_DATE(), INTERVAL 1095 DAY)
    AND atualizacaoData     < CURRENT_DATE()
GROUP BY
    atualizacaoData,
    filial,
    tipo_moto
ORDER BY
    atualizacaoData,
    motos_alugaveis DESC;
"""

df = rodar_query(query_validacao)

import os
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/04_motos_alugaveis_dia_ultimos_36_meses.csv", index=False)
print("💾 Salvo em: data/raw/04_motos_alugaveis_dia_ultimos_36_meses.csv")
