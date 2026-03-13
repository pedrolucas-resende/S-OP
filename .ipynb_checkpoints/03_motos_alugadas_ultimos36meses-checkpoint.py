# sandbox.py — rascunho de queries, não sobe pro git
from bigquery_client import *

query_validacao = """
WITH base AS (
SELECT
    DATE_TRUNC(inicioData, MONTH) AS mes_ano,
    COUNT(*) AS soma_contratos,
    SUM(CASE 
        WHEN status_contrato = 'Churn' THEN 1 
        ELSE 0 
    END) AS soma_churn
FROM `grw_contrato.contrato`
WHERE inicioData >= DATE_SUB(CURRENT_DATE(), INTERVAL 36 MONTH)
AND inicioData < DATE_TRUNC(CURRENT_DATE(), MONTH)
GROUP BY mes_ano
)

SELECT
    mes_ano,
    SUM(soma_contratos - soma_churn) 
        OVER (ORDER BY mes_ano) AS motos_alugadas
FROM base
ORDER BY mes_ano, motos_alugadas DESC
"""

df = rodar_query(query_validacao)

import os
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/03_motos_alugadas.csv", index=False)
print("💾 Salvo em: data/raw/03_motos_alugadas.csv")
