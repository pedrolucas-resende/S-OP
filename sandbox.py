# sandbox.py — rascunho de queries, não sobe pro git
from bigquery_client import *

query = f"""
SELECT 
    -- Agrupa de 2 em 2 semanas a partir de uma data base
    DATE_ADD(
        DATE_TRUNC(DATE(inicioData), ISOWEEK), 
        INTERVAL (CAST(FLOOR(DATE_DIFF(DATE(inicioData), DATE('2021-01-04'), WEEK) / 2) AS INT64) * 2) WEEK
    ) AS quinzena_inicio,
    lugar AS filial,
    COUNT(DISTINCT usuarioId) AS qtd_vendas
FROM `dm-mottu-aluguel.grw_contrato.contrato_dia`
WHERE 
    inicioData IS NOT NULL
    -- Filtrando para garantir que pegamos o registro de "venda" (início do contrato)
    AND dia = DATE(inicioData) 
GROUP BY 1, 2
ORDER BY quinzena_inicio DESC, qtd_vendas DESC;
"""
df = rodar_query(query)
file_out = "output.csv"

import os
os.makedirs("data/raw", exist_ok=True)
df.to_csv(f"data/raw/{file_out}", index=False)
print(f"💾 Salvo em: data/raw/{file_out}")
