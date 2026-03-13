# sandbox.py — rascunho de queries, não sobe pro git
from bigquery_client import *

query_validacao = """
SELECT
  *
  FROM `grw_contrato.contrato`
LIMIT 10
"""

df = rodar_query(query_validacao)

import os
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/output.csv", index=False)
print("💾 Salvo em: data/raw/output.csv")
