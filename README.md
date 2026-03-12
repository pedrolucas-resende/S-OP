# mottu-previsao-demanda

## ⚙️ Como rodar o projeto

### Pré-requisitos
- Python 3.13+
- Conta Google Cloud com acesso ao projeto `dm-mottu-aluguel`
- [`gcloud CLI`](https://cloud.google.com/sdk/docs/install) instalado

### 1. Clone o repositório
```bash
git clone https://github.com/pedrolucas-campos/mottu-previsao-demanda.git
cd mottu-previsao-demanda
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Autentique no Google Cloud
```bash
gcloud auth application-default login
```

### 5. Gere seus .csv e abra os notebooks

Para o notebook `02_exploracao.ipynb`:
```bash
python3 tabela-demanda.py
# abra o notebook com o kernel python .venv
```

Para o notebook `03_exploracao_contratos.ipynb`:
```bash
python3 contratos_lugar_produtos.py
# abra o notebook com o kernel python .venv
```

---

## 📊 Visualizações

### Demanda Total
![Demanda Total](data/raw/grafico_demanda_total.png)

### Contratos: Aluguel vs Venda
![Contratos Aluguel vs Venda](data/raw/grafico_contratos_aluguel_venda.png)

### Evolução dos Top 8
![Evolução Top 8](data/raw/grafico_evolucao_top8.png)

### Heatmap de Sazonalidade
![Heatmap Sazonalidade](data/raw/grafico_heatmap_sazonalidade.png)

### Mix por Tipo de Moto
![Mix Tipo de Moto](data/raw/grafico_mix_tipo_moto.png)

### MoM — Contratos
![MoM Contratos](data/raw/grafico_mom_contratos.png)

### MoM — Demanda
![MoM Demanda](data/raw/grafico_mom.png)

### Taxa de Renovação
![Taxa de Renovação](data/raw/grafico_taxa_renovacao.png)

### Distribuição por Tipo de Moto
![Tipo de Moto](data/raw/grafico_tipo_moto.png)

### Top Lugares
![Top Lugares](data/raw/grafico_top_lugares.png)

### Top Regiões
![Top Regiões](data/raw/grafico_top_regioes.png)
