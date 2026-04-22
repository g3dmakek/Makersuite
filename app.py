import streamlit as st
import json
import os

# -------------------------

# CONFIG DA PÁGINA (PRIMEIRO SEMPRE)

# -------------------------

st.set_page_config(
page_title="Calculadora Maker",
page_icon="🧮",
layout="wide"
)

# -------------------------

# STYLE DA PÁGINA (PROFISSIONAL)

# -------------------------

st.markdown("""

<style>
.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}
.main {
    max-width: 100%;
}
div[data-testid="stMetric"] {
    background-color: #1A1F2B;
    border: 1px solid #2D3748;
    padding: 14px;
    border-radius: 12px;
    text-align: center;
}
div[data-testid="stMetric"] > div {
    color: #00C2FF;
    font-size: 20px;
    font-weight: bold;
}
div[data-testid="stMetric"] label {
    color: #A0AEC0;
    font-size: 12px;
}
div[data-testid="stVerticalBlock"] > div {
    gap: 0.6rem;
}
[data-testid="column"] {
    padding: 0.2rem;
}
</style>

""", unsafe_allow_html=True)

# -------------------------

# TÍTULO

# -------------------------

st.title("🧮 MakerSuite")
st.markdown("### Sistema de Precificação para Makers")
st.caption("Calcule custo, preço e lucro das suas peças")

# -------------------------

# FUNÇÕES DE DADOS

# -------------------------

def carregar_dados():
if not os.path.exists("dados.json"):
return {"produtos": []}
with open("dados.json", "r") as f:
return json.load(f)

def salvar_dados(dados):
with open("dados.json", "w") as f:
json.dump(dados, f, indent=4)

dados = carregar_dados()

# -------------------------

# SIDEBAR

# -------------------------

st.sidebar.header("⚙️ Configurações")

margem_desejada = st.sidebar.slider(
"Margem de lucro (%)",
min_value=10,
max_value=90,
value=60
) / 100

preco_kg = st.sidebar.number_input("Preço do filamento (R$/kg)", value=115.0)

distribuidoras = {
"Neoenergia Cosern (RN)": 0.92,
"Enel SP": 0.95,
"Enel RJ": 1.05,
"Cemig (MG)": 0.85,
"CPFL (SP)": 0.90,
"Equatorial (MA/PA)": 0.88,
"Outra": None
}

distribuidora = st.sidebar.selectbox("Distribuidora de energia", list(distribuidoras.keys()))

if distribuidoras[distribuidora] is not None:
custo_kwh = distribuidoras[distribuidora]
st.sidebar.info(f"Tarifa média: R$ {custo_kwh}/kWh")
else:
custo_kwh = st.sidebar.number_input("Custo energia (R$/kWh)", value=0.80)

# -------------------------

# IMPRESSORA

# -------------------------

st.sidebar.subheader("🖨️ Impressora")

impressoras = {
"Bambu Lab A1": {"valor": 3500, "vida_util": 4000, "consumo": 0.12},
"Outro": {"valor": None, "vida_util": None, "consumo": None}
}

modelo = st.sidebar.selectbox("Selecione sua impressora", list(impressoras.keys()))
dados_impressora = impressoras[modelo]

valor_maquina = st.sidebar.number_input(
"Valor da impressora (R$)",
value=float(dados_impressora["valor"]) if dados_impressora["valor"] else 3000.0
)

vida_util = st.sidebar.number_input(
"Vida útil estimada (horas)",
value=int(dados_impressora["vida_util"]) if dados_impressora["vida_util"] else 3000
)

manutencao_hora = st.sidebar.number_input("Manutenção (R$/h)", value=1.0)
consumo_maquina = st.sidebar.number_input(
"Consumo da impressora (kW)",
value=float(dados_impressora["consumo"]) if dados_impressora["consumo"] else 0.12
)

custo_hora = (valor_maquina / vida_util) + manutencao_hora if vida_util > 0 else manutencao_hora

# -------------------------

# INPUTS

# -------------------------

col1, col2 = st.columns(2)

with col1:
nome = st.text_input("Nome do produto")

with col2:
peso = st.number_input("Peso (g)", value=50.0)
tempo = st.number_input("Tempo (h)", value=2.0)

quantidade = st.number_input("Quantidade total", min_value=1, value=10)
pecas_por_impressao = st.number_input("Peças por impressão", min_value=1, value=1)

calcular = st.button("💰 Calcular")

# -------------------------

# CÁLCULO

# -------------------------

if calcular:
import math

```
custo_material_total = (peso / 1000) * preco_kg
custo_maquina_total = tempo * custo_hora
custo_energia_total = tempo * custo_kwh * consumo_maquina

custo_unitario = (
    (custo_material_total + custo_maquina_total + custo_energia_total)
    / pecas_por_impressao
)

preco_venda = custo_unitario / (1 - margem_desejada)
lucro_unitario = preco_venda - custo_unitario

numero_impressoes = math.ceil(quantidade / pecas_por_impressao)
tempo_total = numero_impressoes * tempo

custo_total_lote = numero_impressoes * (
    custo_material_total + custo_maquina_total + custo_energia_total
)

faturamento_total = preco_venda * quantidade
lucro_total = faturamento_total - custo_total_lote

lucro_por_hora = lucro_total / tempo_total if tempo_total > 0 else 0

st.session_state["calculo"] = {
    "nome": nome,
    "custo_unitario": custo_unitario,
    "preco_venda": preco_venda,
    "lucro_unitario": lucro_unitario,
    "lucro_total": lucro_total,
    "lucro_por_hora": lucro_por_hora,
    "energia_unitaria": custo_energia_total / pecas_por_impressao,
    "tempo_total": tempo_total,
    "numero_impressoes": numero_impressoes,
    "faturamento_total": faturamento_total,
    "custo_total_lote": custo_total_lote
}
```

# -------------------------

# DASHBOARD

# -------------------------

if "calculo" in st.session_state:
c = st.session_state["calculo"]

```
col_esq, col_dir = st.columns(2)

with col_esq:
    st.metric("💰 Custo", f"R$ {c['custo_unitario']:.2f}")
    st.metric("⚡ Energia", f"R$ {c.get('energia_unitaria', 0):.2f}")

with col_dir:
    st.metric("📈 Lucro", f"R$ {c['lucro_total']:.2f}")
```
