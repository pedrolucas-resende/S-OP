# 05_eop.py
from bigquery_client import *
import os

query_validacao = """
WITH tudo_eop AS (
  SELECT
    DATE_ADD(DATE(atualizacaoData), INTERVAL -1 DAY) AS dataValor,
    cf.pais,
    cf.estado,   -- ← NOVO
    cf.cidade,   -- ← NOVO
    cf.lugar AS filial,
    cf.populacao_cidade,

    SUM(CASE WHEN tipo_situacao = 'Alugada' THEN qtd ELSE 0 END) AS alugadas_total,
    SUM(CASE WHEN tipo_situacao = 'Alugada' AND categoria_branch_config_tipo_moto = '0km' THEN qtd ELSE 0 END) AS alugadas_0km,
    SUM(CASE WHEN tipo_situacao = 'Alugada' AND categoria_branch_config_tipo_moto = 'Semi' THEN qtd ELSE 0 END) AS alugadas_semi,
    SUM(CASE WHEN tipo_situacao = 'Alugada' AND categoria_branch_config_tipo_moto = 'Usada' THEN qtd ELSE 0 END) AS alugadas_usada,

    SUM(CASE WHEN frota_operacional = 'Frota Operacional' THEN qtd ELSE 0 END) AS frota_op_total,
    SUM(CASE WHEN frota_operacional = 'Frota Operacional' AND moto_0km = '0km' AND tipo_situacao != 'Alugada' THEN qtd ELSE 0 END) AS frota_op_0km,
    SUM(CASE WHEN frota_operacional = 'Frota Operacional' AND moto_0km = 'Semi' AND tipo_situacao != 'Alugada' THEN qtd ELSE 0 END) AS frota_op_semi,
    SUM(CASE WHEN frota_operacional = 'Frota Operacional' AND moto_0km = 'Usada' AND tipo_situacao != 'Alugada' THEN qtd ELSE 0 END) AS frota_op_usada,

    SUM(CASE WHEN tipo_situacao = 'Pronta para Aluguel' THEN qtd ELSE 0 END) AS pronta_total,
    SUM(CASE WHEN tipo_situacao = 'Pronta para Aluguel' AND moto_0km = '0km' THEN qtd ELSE 0 END) AS pronta_0km,
    SUM(CASE WHEN tipo_situacao = 'Pronta para Aluguel' AND moto_0km = 'Semi' THEN qtd ELSE 0 END) AS pronta_semi,
    SUM(CASE WHEN tipo_situacao = 'Pronta para Aluguel' AND moto_0km = 'Usada' THEN qtd ELSE 0 END) AS pronta_usada,

    SUM(CASE WHEN descricao_situacao = 'Em manutencao' THEN qtd ELSE 0 END) AS manutencao_total,
    SUM(CASE WHEN descricao_situacao = 'Em manutencao' AND moto_0km = '0km' THEN qtd ELSE 0 END) AS manutencao_0km,
    SUM(CASE WHEN descricao_situacao = 'Em manutencao' AND moto_0km = 'Semi' THEN qtd ELSE 0 END) AS manutencao_semi,
    SUM(CASE WHEN descricao_situacao = 'Em manutencao' AND moto_0km = 'Usada' THEN qtd ELSE 0 END) AS manutencao_usada,

    SUM(CASE WHEN descricao_situacao = 'Em transito 0km' THEN qtd ELSE 0 END) AS transito_0km_total,
    SUM(CASE WHEN tipo_situacao = 'Motos 0km' THEN qtd ELSE 0 END) AS fabrica_0km_total,
    SUM(CASE WHEN tipo_situacao = 'Administrativo' THEN qtd ELSE 0 END) AS administrativo_total,

    SUM(CASE WHEN tipo_situacao = 'Venda' THEN qtd ELSE 0 END) AS venda_total,
    SUM(CASE WHEN tipo_situacao = 'Venda' AND descricao_situacao IN ('Vendida Minha Mottu', 'Em Transferência Minha Mottu') THEN qtd ELSE 0 END) AS venda_mm,
    SUM(CASE WHEN tipo_situacao = 'Venda' AND descricao_situacao NOT IN ('Vendida Minha Mottu', 'Em Transferência Minha Mottu', 'Pronta no Leilão') THEN qtd ELSE 0 END) AS venda_direta_doacao,
    SUM(CASE WHEN tipo_situacao = 'Venda' AND descricao_situacao IN ('Pronta no Leilão') THEN qtd ELSE 0 END) AS venda_ag_leilao,

    SUM(CASE WHEN tipo_situacao = 'Perda Total' THEN qtd ELSE 0 END) AS perda_total,
    SUM(CASE WHEN tipo_situacao = 'Perdida/Roubo' THEN qtd ELSE 0 END) AS roubada_total,

    SUM(CASE WHEN tipo_situacao = 'Indisponível' AND descricao_situacao IN ('Transito entre agencias', 'Na rua recolhida') THEN qtd ELSE 0 END) AS transito_entre_ag_total,
    SUM(CASE WHEN tipo_situacao = 'Indisponível' AND descricao_situacao NOT IN ('Em manutencao', 'Em transito 0km', 'Recebida 0km', 'Transito entre agencias') THEN qtd ELSE 0 END) AS indisponivel_total,
    SUM(CASE WHEN tipo_situacao = 'Indisponível' AND descricao_situacao = 'Apreendida/Patio' THEN qtd ELSE 0 END) AS apreendida_total,
    SUM(CASE WHEN tipo_situacao = 'Indisponível' AND descricao_situacao = 'Apropriacao Indebita' THEN qtd ELSE 0 END) AS apropriacao_total,
    SUM(CASE WHEN tipo_situacao = 'Indisponível' AND descricao_situacao NOT IN ('Em manutencao', 'Em transito 0km', 'Recebida 0km', 'Transito entre agencias', 'Na rua recolhida', 'Apropriacao Indebita', 'Apreendida/Patio') THEN qtd ELSE 0 END) AS indisponiveis_regulatorio_total,
    SUM(CASE WHEN descricao_situacao = 'Recebida 0km' THEN qtd ELSE 0 END) AS recebida_0km,
    SUM(CASE WHEN tipo_situacao = 'Em transito 0km' THEN qtd ELSE 0 END) AS transito_0km

  FROM `dm-mottu-aluguel.exp_frota.frota_historico_agrupado` t
  LEFT JOIN `dm-mottu-aluguel.exp_atendimentos.cadastro_filiais` cf ON cf.lugar = t.filial
  WHERE DATE(atualizacaoData) = DATE_TRUNC(DATE(atualizacaoData), MONTH)
    AND DATE(atualizacaoData) >= '2025-01-02'
  GROUP BY ALL
),

intra_mes AS (
  SELECT 
    LAST_DAY(DATE(data_movimentacao), MONTH) AS dataValor,
    filial_resultante AS filial,
    COUNT(DISTINCT veiculoId) AS qtd_faturada_mes
  FROM `dm-mottu-aluguel.exp_frota.veiculo_movimentacao_situacao`
  WHERE situacao_anterior_id = 0
  GROUP BY ALL
),

producao_mes AS (
  SELECT
    LAST_DAY(DATE(criacaoData), MONTH) AS mes,
    lugar_nome AS filial,
    pais_filial,
    COUNT(id) AS qtd_produzidas
  FROM `dm-mottu-aluguel.exp_frota.frota_atual` t
  LEFT JOIN `dm-mottu-aluguel.exp_atendimentos.cadastro_filiais` cf ON cf.lugar = t.lugar_nome
  WHERE pais = 'Brasil'
  GROUP BY ALL
),

producao AS (
  WITH mecanicos AS (
    SELECT
      filial,
      LAST_DAY(DATE(data_valor), MONTH) AS mes,
      AVG(qtd_mecanicos_rampa_total)       AS mec_total,
      AVG(qtd_mecanicos_que_bateram_ponto) AS mec_presentes,
      AVG(qtd_mecanicos_na_rampa)          AS mec_na_rampa
    FROM `dm-mottu-aluguel.exp_frota.indicadores_diarios_filiais`
    WHERE data_valor > '2026-01-01'
    GROUP BY ALL
  ),
  manu AS (
    SELECT
      LAST_DAY(DATE(data_finalizacao), MONTH) AS mes,
      COUNT(CASE WHEN tipo_manutencao = 'Interno' THEN manutencao_id END)  AS qtd_internas,
      COUNT(CASE WHEN tipo_manutencao != 'Interno' THEN manutencao_id END) AS qtd_cliente,
      filial
    FROM `dm-mottu-aluguel.man_operacao.manutencoes_agrupadas`
    WHERE DATE(data_finalizacao) > DATE '2025-01-01'
    GROUP BY ALL
  )
  SELECT m.*, mec.mec_total, mec.mec_na_rampa, mec.mec_presentes
  FROM manu m
  LEFT JOIN mecanicos mec ON mec.mes = m.mes AND mec.filial = m.filial
),

demanda AS (
  SELECT 
    LAST_DAY(pagamentoData, MONTH) AS mes,
    COUNT(CASE WHEN tipo_moto_km = '0km'  THEN locacaoId END) AS qtd_vendas_0km,
    COUNT(CASE WHEN tipo_moto_km = 'Semi' THEN locacaoId END) AS qtd_vendas_semi,
    COUNT(CASE WHEN tipo_moto_km = 'Usada' THEN locacaoId END) AS qtd_vendas_usada,
    lugar AS filial
  FROM `dm-mottu-aluguel.grw_aquisicao.vendas`
  WHERE pagamentoData >= '2025-01-01'
  GROUP BY ALL
),

-- ← NOVO: churn vem do 06_eop_tipos
churn_mes AS (
  SELECT
    LAST_DAY(DATE(fimData), MONTH) AS mes,
    lugar AS filial,
    COUNT(CASE WHEN status_contrato = 'Churn' THEN 1 END) AS churn
  FROM `dm-mottu-aluguel.grw_contrato.contrato`
  WHERE DATE(fimData) >= '2025-01-01'
  GROUP BY ALL
)

SELECT 
  t.dataValor,
  t.pais,
  t.filial, -- antigo lugar
  t.alugadas_total, t.alugadas_0km, t.alugadas_semi, t.alugadas_usada,
  t.frota_op_total, t.frota_op_0km, t.frota_op_semi, t.frota_op_usada,
  t.pronta_total, t.pronta_0km, t.pronta_semi, t.pronta_usada,
  t.manutencao_total, t.manutencao_0km, t.manutencao_semi, t.manutencao_usada,
  t.transito_0km_total, t.fabrica_0km_total, t.administrativo_total,
  t.venda_total, t.venda_mm, t.venda_direta_doacao, t.venda_ag_leilao,
  t.perda_total, t.roubada_total, t.transito_entre_ag_total,
  t.indisponivel_total, t.apreendida_total, t.apropriacao_total,
  t.indisponiveis_regulatorio_total, t.recebida_0km, t.transito_0km,
  i.qtd_faturada_mes,
  p.qtd_produzidas,
  d.qtd_vendas_0km, d.qtd_vendas_semi, d.qtd_vendas_usada,
  prod.qtd_internas, prod.qtd_cliente,
  prod.mec_total, prod.mec_presentes, prod.mec_na_rampa,
  t.estado,   -- ← NOVO
  t.cidade,   -- ← NOVO
  t.populacao_cidade,
  -- Região derivada igual ao 06_eop_tipos  ← NOVO
  CASE 
    WHEN t.pais = 'México'            THEN 'México'
    WHEN t.cidade = 'São Paulo'       THEN 'São Paulo (Capital)'
    WHEN t.cidade = 'Rio de Janeiro'  THEN 'Rio de Janeiro (Capital)'
    WHEN t.estado IN ('SP','RJ','MG','ES')                          THEN 'Sudeste'
    WHEN t.estado IN ('PR','SC','RS')                               THEN 'Sul'
    WHEN t.estado IN ('BA','PE','CE','RN','PB','AL','SE','MA','PI') THEN 'Nordeste'
    WHEN t.estado IN ('AM','PA','AC','RO','RR','AP','TO')           THEN 'Norte'
    WHEN t.estado IN ('DF','GO','MT','MS')                         THEN 'Centro-Oeste'
    ELSE 'Outros'
  END AS regiao_consolidada,
  COALESCE(c.churn, 0) AS churn   -- ← NOVO
FROM tudo_eop t
LEFT JOIN intra_mes i    ON i.dataValor = t.dataValor AND i.filial = t.filial
LEFT JOIN producao_mes p ON p.mes       = t.dataValor AND p.filial = t.filial
LEFT JOIN demanda d      ON d.mes       = t.dataValor AND d.filial = t.filial
LEFT JOIN producao prod  ON prod.mes    = t.dataValor AND prod.filial = t.filial
LEFT JOIN churn_mes c    ON c.mes       = t.dataValor AND c.filial = t.filial  -- ← NOVO
ORDER BY t.dataValor DESC, t.filial;
"""

df = rodar_query(query_validacao)

# Exportação para CSV organizada
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/07_eop_total.csv", index=False)

print("✅ Relatório Regional gerado com sucesso!")
print(df.head(10)) # Para você validar os grupos no terminal
