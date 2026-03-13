# sandbox.py — rascunho de queries, não sobe pro git
from bigquery_client import *

query_validacao = """
select date_trunc(inicioData, month) as date, sum(retirada) as vendas
from `grw_contrato.contrato`
where
inicioData >= DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 36 MONTH), MONTH)
and
inicioData < date_trunc(current_date(), month)
group by 1
order by 1, 2 desc
"""

df = rodar_query(query_validacao)

import os
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/02_vendas_3anos.csv", index=False)
print("💾 Salvo em: data/raw/02_vendas_3anos.csv")
