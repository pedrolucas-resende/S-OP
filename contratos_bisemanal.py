# sandbox.py — rascunho de queries, não sobe pro git
from bigquery_client import *

query_validacao = """
SELECT
    CONCAT(
        FORMAT_DATE('%Y-%m', c.inicioData),
        '-W',
        LPAD(
            CAST(DIV(EXTRACT(DAYOFYEAR FROM c.inicioData) - 1, 14) + 1 AS STRING),
            2,
            '0'
        )
    ) AS periodo_bisemanal,
    c.lugar,
    c.lugarId,
    f.longitude_lugar,
    f.latitude_lugar,
    SUM(COALESCE(c.retirada, 0)) AS contratos_novos,
    CASE
        WHEN c.produto LIKE '%0km%'       THEN 'Nova'
        WHEN c.produto LIKE '%Seminova%'  THEN 'Semi-nova'
        WHEN c.produto LIKE '%Usada%'     THEN 'Usada'
        ELSE 'Outros'
    END AS tipo_moto
  FROM `grw_contrato.contrato` c
  LEFT JOIN `exp_atendimentos.cadastro_filiais` f
    ON c.lugarId = f.lugarId
  WHERE c.inicioData >= DATE '2024-01-01'
  GROUP BY 1, 2, 3, 4, 5, tipo_moto
"""

df = rodar_query(query_validacao)

import os
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/contratos_por_lugar_produto.csv", index=False)
print("💾 Salvo em: data/raw/contratos_por_lugar_produto.csv")
