WITH
  base AS (
    -- aqui você pode referenciar a query anterior como CTE, ou (melhor) materializar o CSV/uma tabela.
    SELECT
      DATE_TRUNC(dataValor, MONTH) AS dataValor,
      pais,
      cidade,
      estado,
      regiao_ibge AS regiao,
      alugadas_total AS rented_fleet_eop,
      qtd_vendas_0km AS sales_0km,
      qtd_vendas_semi AS sales_semi,
      (qtd_vendas_0km + qtd_vendas_semi + qtd_vendas_usada) AS sales,
      qtd_produzidas AS production,
      frota_op_total AS inventory,
      churn
    FROM `z_ren_homologacao.input_o`
  ),
  final AS (
    SELECT
      dataValor AS mes,
      estado,
      SUM(rented_fleet_eop) AS rented_fleet_eop,
      SUM(sales_0km) AS sales_0km,
      SUM(sales_semi) AS sales_semi,
      SUM(sales) AS sales,
      SUM(inventory) AS inventory,
      SUM(production) AS production,
      SUM(churn) AS churn
    FROM base
    GROUP BY 1, 2
    ORDER BY 1 DESC, 2
  )
SELECT * FROM final WHERE final.estado IS NOT NULL
