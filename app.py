import streamlit as st
import json
import os
import math

# -------------------------
# CONFIG DA PÁGINA
# -------------------------
st.set_page_config(
    page_title="Calculadora Maker",
    page_icon="🧮",
    layout="wide"
)

# -------------------------
# STYLE
# -------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}
.main { max-width: 100%; }
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
</style>
""", unsafe_allow_html=True)

# -------------------------
# TÍTULO
# -------------------------
st.title("🧮 MakerSuite")
st.caption("Calcule custo, preço e lucro das suas peças")

# -------------------------
# DADOS
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
    "Margem de lucro (%)", 10, 90, 60
) / 100

preco_kg = st.sidebar.number_input("Preço do filamento", value=115.0)
custo_kwh = 0.92

valor_maquina = st.sidebar.number_input("Valor impressora", value=3500.0)
vida_util = st.sidebar.number_input("Vida útil (h)", value=4000)
manutencao_hora = st.sidebar.number_input("Manutenção (R$/h)", value=1.0)
consumo_maquina = st.sidebar.number_input("Consumo (kW)", value=0.12)

custo_hora = (valor_maquina / vida_util) + manutencao_hora

# -------------------------
# INPUTS
# -------------------------
col1, col2 = st.columns(2)

with col1:
    nome = st.text_input("Nome")
    tipo = st.selectbox("Tipo", ["Chaveiro", "Decoração", "Personalizado"])

with col2:
    peso = st.number_input("Peso (g)", value=50.0)
    tempo = st.number_input("Tempo (h)", value=2.0)

col3, col4 = st.columns(2)

with col3:
    quantidade = st.number_input("Quantidade", 1, value=10)

with col4:
    pecas_por_impressao = st.number_input("Peças por impressão", 1, value=1)

# -------------------------
# BOTÃO
# -------------------------
if st.button("💰 Calcular"):

    custo_material = (peso / 1000) * preco_kg
    custo_maquina = tempo * custo_hora
    custo_energia = tempo * custo_kwh * consumo_maquina

    custo_unitario = (
        custo_material +
        custo_maquina +
        custo_energia
    ) / pecas_por_impressao

    preco_venda = custo_unitario / (1 - margem_desejada)

    lucro_unitario = preco_venda - custo_unitario
    margem_real = (lucro_unitario / preco_venda) * 100

    numero_impressoes = math.ceil(quantidade / pecas_por_impressao)
    tempo_total = numero_impressoes * tempo

    custo_total_lote = numero_impressoes * (
        custo_material + custo_maquina + custo_energia
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
        "margem": margem_real,
        "quantidade": quantidade,
        "tempo_total": tempo_total,
        "numero_impressoes": numero_impressoes,
        "faturamento_total": faturamento_total,
        "custo_total_lote": custo_total_lote
    }

# -------------------------
# DASHBOARD
# -------------------------
if "calculo" not in st.session_state:
    st.info("Faça um cálculo para ver os resultados")
    st.stop()

c = st.session_state["calculo"]

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Preço", f"R$ {c['preco_venda']:.2f}")
col2.metric("Lucro", f"R$ {c['lucro_unitario']:.2f}")
col3.metric("Margem", f"{c['margem']:.1f}%")
col4.metric("Lucro/h", f"R$ {c['lucro_por_hora']:.2f}")

st.divider()

# COLUNAS PRINCIPAIS
col_esq, col_dir = st.columns(2)

# ESQUERDA
with col_esq:
    st.subheader("📊 Por Peça")
    st.metric("Custo", f"R$ {c['custo_unitario']:.2f}")
    st.metric("Preço", f"R$ {c['preco_venda']:.2f}")
    st.metric("Lucro", f"R$ {c['lucro_unitario']:.2f}")

# DIREITA
with col_dir:
    st.subheader("📦 Produção")
    st.metric("Peças", c["quantidade"])
    st.metric("Tempo total", f"{c['tempo_total']:.1f}h")
    st.metric("Lucro total", f"R$ {c['lucro_total']:.2f}")

st.divider()

# SALVAR
if st.button("💾 Salvar produto"):
    dados["produtos"].append(c)
    salvar_dados(dados)
    st.success("Salvo!")

# LISTA
st.subheader("📦 Produtos")

for p in dados["produtos"]:
    st.write(f"**{p['nome']}** - R$ {p['preco_venda']:.2f}")
