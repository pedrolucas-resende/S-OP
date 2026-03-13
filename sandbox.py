# sandbox.py — rascunho de queries, não sobe pro git
from bigquery_client import *

query_validacao = """
WITH base AS (
SELECT
    lugarId,
    lugar,
    DATE_TRUNC(inicioData, MONTH) AS mes_ano,
    COUNT(*) AS soma_contratos,
    SUM(CASE 
        WHEN status_contrato = 'Churn' THEN 1 
        ELSE 0 
    END) AS soma_churn
FROM `grw_contrato.contrato`
WHERE inicioData >= DATE_SUB(CURRENT_DATE(), INTERVAL 36 MONTH)
GROUP BY lugarId, lugar, mes_ano
)

SELECT
    lugarId,
    lugar,
    mes_ano,
    soma_contratos - soma_churn AS motos_alugadas
FROM base
ORDER BY mes_ano, motos_alugadas DESC
"""

df = rodar_query(query_validacao)

import os
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/motos_alugadas_ultimos_36_meses.csv", index=False)
print("💾 Salvo em: data/raw/motos_alugadas_ultimos_36_meses.csv")
