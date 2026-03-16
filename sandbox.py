# sandbox.py — rascunho de queries, não sobe pro git
from bigquery_client import *

query_validacao = """
    -- Exemplo de query para validação, pode ser qualquer coisa que você queira testar:w
"""

df = rodar_query(query_validacao)

import os
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/sandbox.csv", index=False)
print("💾 Salvo em: data/raw/sandbox.csv")
