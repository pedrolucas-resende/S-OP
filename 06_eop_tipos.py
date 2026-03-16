# 05_eop.py
from bigquery_client import *
import os

query_validacao = """
WITH tudo_eop AS (
  SELECT
    DATE_ADD(DATE(atualizacaoData), INTERVAL -1 DAY) AS dataValor,
    cf.pais,
    cf.estado,     -- Ajuste aqui se a sua coluna for 'uf' ou 'estado_sigla'
    cf.cidade,     -- Ajuste aqui se a sua coluna for 'cidade_nome' ou similar
    cf.lugar AS filial,
    
    -- 1. Rented Fleet EoP
    SUM(CASE WHEN tipo_situacao = 'Alugada' THEN qtd ELSE 0 END) AS rented_fleet_eop,
    
    -- 5. Inventory
    SUM(CASE WHEN frota_operacional = 'Frota Operacional' THEN qtd ELSE 0 END) AS inventory
    
  FROM `dm-mottu-aluguel.exp_frota.frota_historico_agrupado` t
  LEFT JOIN `dm-mottu-aluguel.exp_atendimentos.cadastro_filiais` cf ON cf.lugar = t.filial
  WHERE DATE(atualizacaoData) = DATE_TRUNC(DATE(atualizacaoData), MONTH)
    AND DATE(atualizacaoData) >= '2025-01-02'
  GROUP BY ALL
),

producao_mes AS (
  SELECT
    LAST_DAY(DATE(criacaoData), MONTH) AS mes,
    lugar_nome AS filial,
    
    -- 6. Production
    COUNT(id) AS qtd_produzidas
  FROM `dm-mottu-aluguel.exp_frota.frota_atual` t
  GROUP BY ALL
),

demanda AS (
  SELECT 
    LAST_DAY(pagamentoData, MONTH) AS mes,
    
    -- 2. Sales 0km
    COUNT(CASE WHEN tipo_moto_km = '0km' THEN locacaoId END) AS sales_0km,
    
    -- 3. Sales Semi
    COUNT(CASE WHEN tipo_moto_km = 'Semi' THEN locacaoId END) AS sales_semi,
    
    -- 4. Sales (Total)
    COUNT(locacaoId) AS sales_total,
    
    lugar AS filial
  FROM `dm-mottu-aluguel.grw_aquisicao.vendas`
  WHERE pagamentoData >= '2025-01-01'
  GROUP BY ALL
),

churn_mes AS (
  SELECT
    LAST_DAY(DATE(fimData), MONTH) AS mes,
    lugar AS filial,
    
    -- 7. Churn
    COUNT(CASE WHEN status_contrato = 'Churn' THEN 1 END) AS qtd_churn
  FROM `dm-mottu-aluguel.grw_contrato.contrato`
  WHERE DATE(fimData) >= '2025-01-01'
  GROUP BY ALL
),

consolidado_filial AS (
  SELECT 
    t.dataValor AS mes,
    t.pais,
    t.estado,
    t.cidade,
    t.filial,
    t.rented_fleet_eop,
    t.inventory,
    COALESCE(d.sales_0km, 0) AS sales_0km,
    COALESCE(d.sales_semi, 0) AS sales_semi,
    COALESCE(d.sales_total, 0) AS sales_total,
    COALESCE(p.qtd_produzidas, 0) AS production,
    COALESCE(c.qtd_churn, 0) AS churn
  FROM tudo_eop t
  LEFT JOIN demanda d      ON d.mes = t.dataValor AND d.filial = t.filial
  LEFT JOIN producao_mes p ON p.mes = t.dataValor AND p.filial = t.filial
  LEFT JOIN churn_mes c    ON c.mes = t.dataValor AND c.filial = t.filial
)

-- AGREGANDO POR REGIÃO FINAL
SELECT 
    mes,
    CASE 
        WHEN pais = 'México' THEN 'México'
        -- Se 'cidade' vier nulo/diferente, podemos usar: WHEN filial LIKE '%São Paulo%' THEN 'São Paulo (Capital)'
        WHEN cidade = 'São Paulo' THEN 'São Paulo (Capital)'
        WHEN estado IN ('SP', 'RJ', 'MG', 'ES') THEN 'Sudeste'
        WHEN estado IN ('PR', 'SC', 'RS') THEN 'Sul'
        WHEN estado IN ('BA', 'PE', 'CE', 'RN', 'PB', 'AL', 'SE', 'MA', 'PI') THEN 'Nordeste'
        WHEN estado IN ('AM', 'PA', 'AC', 'RO', 'RR', 'AP', 'TO') THEN 'Norte'
        WHEN estado IN ('DF', 'GO', 'MT', 'MS') THEN 'Centro-Oeste'
        ELSE 'Outros'
    END AS regiao_consolidada,
    
    SUM(rented_fleet_eop) AS rented_fleet_eop,
    SUM(sales_0km) AS sales_0km,
    SUM(sales_semi) AS sales_semi,
    SUM(sales_total) AS sales_total,
    SUM(inventory) AS inventory,
    SUM(production) AS production,
    
    -- 7. Churn
    SUM(churn) AS churn
    
FROM consolidado_filial
GROUP BY 1, 2
ORDER BY 1 DESC, 
    CASE regiao_consolidada 
        WHEN 'São Paulo (Capital)' THEN 1 
        WHEN 'Sudeste' THEN 2 
        WHEN 'Sul' THEN 3
        WHEN 'Nordeste' THEN 4
        WHEN 'Norte' THEN 5
        WHEN 'Centro-Oeste' THEN 6
        WHEN 'México' THEN 7
        ELSE 8 END;
"""

df = rodar_query(query_validacao)

# Exportação para CSV organizada
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/06_eop_tipos.csv", index=False)

print("✅ Relatório Regional gerado com sucesso!")
print(df.head(10)) # Para você validar os grupos no terminal
