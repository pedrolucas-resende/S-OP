# 05_eop.py
from bigquery_client import *
import os

query_validacao = """
WITH tudo_eop AS (
  SELECT
    DATE_ADD(DATE(atualizacaoData), INTERVAL -1 DAY) AS dataValor,
    cf.pais,
    cf.regiao_ibge,
    cf.cidade,
    cf.lugar AS filial,
    -- Status de Frota
    SUM(CASE WHEN tipo_situacao = 'Alugada' THEN qtd ELSE 0 END) AS alugadas_total,
    SUM(CASE WHEN frota_operacional = 'Frota Operacional' THEN qtd ELSE 0 END) AS frota_op_total,
    SUM(CASE WHEN tipo_situacao = 'Pronta para Aluguel' THEN qtd ELSE 0 END) AS pronta_total
  FROM `dm-mottu-aluguel.exp_frota.frota_historico_agrupado` t
  LEFT JOIN `dm-mottu-aluguel.exp_atendimentos.cadastro_filiais` cf ON cf.lugar = t.filial
  WHERE DATE(atualizacaoData) = DATE_TRUNC(DATE(atualizacaoData), MONTH)
    AND DATE(atualizacaoData) >= '2025-01-01'
  GROUP BY ALL
),

demanda AS (
  SELECT 
    LAST_DAY(pagamentoData, MONTH) AS mes,
    lugar AS filial,
    COUNT(locacaoId) AS qtd_vendas
  FROM `dm-mottu-aluguel.grw_aquisicao.vendas`
  WHERE pagamentoData >= '2025-01-01'
  GROUP BY ALL
),

consolidado_filial AS (
    SELECT 
        t.dataValor,
        t.pais,
        t.regiao_ibge,
        t.cidade,
        t.filial,
        t.alugadas_total,
        t.frota_op_total,
        d.qtd_vendas
    FROM tudo_eop t
    LEFT JOIN demanda d ON d.mes = t.dataValor AND d.filial = t.filial
)

SELECT 
    dataValor,
    -- LÓGICA DE REGIONALIZAÇÃO SOLICITADA
    CASE 
        WHEN pais = 'México' THEN 'México'
        WHEN cidade = 'São Paulo' THEN 'São Paulo (Capital)'
        WHEN cidade = 'Rio de Janeiro' THEN 'Rio de Janeiro (Capital)'
        WHEN regiao_ibge = 'Sudeste' THEN 'Sudeste' -- Como o SP Capital já foi pego acima, aqui sobra o resto do SE
        WHEN regiao_ibge = 'Sul' THEN 'Sul'
        WHEN regiao_ibge = 'Norte' THEN 'Norte'
        WHEN regiao_ibge = 'Nordeste' THEN 'Nordeste'
        WHEN regiao_ibge = 'Centro-Oeste' THEN 'Centro-Oeste'
        ELSE 'Outros'
    END AS regiao_ibge_consolidada,
    SUM(alugadas_total) AS alugadas,
    SUM(frota_op_total) AS frota_operacional,
    SUM(qtd_vendas) AS vendas
FROM consolidado_filial
GROUP BY 1, 2
ORDER BY 1 DESC, 
    CASE regiao_ibge_consolidada 
        WHEN 'São Paulo (Capital)' THEN 1 
        WHEN 'Rio de Janeiro (Capital)' THEN 2
        WHEN 'Sudeste' THEN 3 
        WHEN 'Sul' THEN 4
        WHEN 'Nordeste' THEN 5
        WHEN 'Norte' THEN 6
        WHEN 'Centro-Oeste' THEN 7
        WHEN 'México' THEN 8
        ELSE 9 END
"""

df = rodar_query(query_validacao)

# Exportação para CSV organizada
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/05_eop_regiao_rio.csv", index=False)

print("✅ Relatório Regional gerado com sucesso!")
print(df.head(10)) # Para você validar os grupos no terminal
