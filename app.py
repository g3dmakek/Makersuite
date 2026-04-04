import streamlit as st
import json
import os

# -------------------------
# STYLE DA PÁGINA
# -------------------------
st.markdown("""
<style>

/* Espaçamento geral */
.block-container {
    padding-top: 2rem;
}

/* Cards de métricas */
div[data-testid="stMetric"] {
    background-color: #1A1F2B;
    border: 1px solid #2D3748;
    padding: 20px;
    border-radius: 14px;
    text-align: center;
}

/* Valor grande */
div[data-testid="stMetric"] > div {
    color: #00C2FF;
    font-size: 22px;
    font-weight: bold;
}

/* Label menor */
div[data-testid="stMetric"] label {
    color: #A0AEC0;
}

</style>
""", unsafe_allow_html=True)
# -------------------------
# CONFIG DA PÁGINA
# -------------------------
st.set_page_config(
    page_title="MakerSuite",
    page_icon="🧮",
    layout="centered"
)

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
# SIDEBAR (CONFIGURAÇÕES)
# -------------------------
st.sidebar.header("⚙️ Configurações")

preco_kg = st.sidebar.number_input("Preço do filamento (R$/kg)", value=100.0)
custo_hora = st.sidebar.number_input("Custo por hora máquina (R$)", value=2.5)
st.sidebar.subheader("⚡ Energia")

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

st.sidebar.subheader("⚙️ Impressora")

impressoras = {
    "Bambu Lab A1": 0.12,
    "Bambu Lab P1P": 0.15,
    "Bambu Lab X1 Carbon": 0.20,
    "Ender 3 V3 KE": 0.12,
    "Ender 3": 0.10,
    "Prusa MK3": 0.13,
    "Outro": None
}

modelo = st.sidebar.selectbox("Selecione sua impressora", list(impressoras.keys()))

if impressoras[modelo] is not None:
    consumo_maquina = impressoras[modelo]
    st.sidebar.info(f"Consumo médio: {consumo_maquina} kW")
else:
    consumo_maquina = st.sidebar.number_input("Consumo da impressora (kW)", value=0.12)


# -------------------------
# DADOS DO PRODUTO
# -------------------------
st.subheader("📦 Dados do Produto")

nome = st.text_input("Nome do produto")
tipo_produto = st.selectbox("Tipo", ["Chaveiro", "Decoração", "Personalizado"])

st.divider()

# -------------------------
# PRODUÇÃO
# -------------------------
st.subheader("⚙️ Produção")

peso = st.number_input("Peso (g)", value=50.0)
tempo = st.number_input("Tempo de impressão (h)", value=2.0)
quantidade = st.number_input(
    "Quantidade total de peças (produção)",
    min_value=1,
    value=10
)

pecas_por_impressao = st.number_input(
    "Peças produzidas por impressão (capacidade da mesa)",
    min_value=1,
    value=1
)

st.caption("💡 Ex: quer produzir 100 peças e sua mesa comporta 20 → serão 5 impressões")

# -------------------------
# CUSTOS (AJUSTADO PARA LOTE)
# -------------------------

# Material (lote → depois divide)
custo_material_total = (peso / 1000) * preco_kg
custo_material_unitario = custo_material_total / pecas_por_impressao

# Custo da impressão inteira (lote)
custo_maquina_total = tempo * custo_hora
custo_energia_total = tempo * custo_kwh * consumo_maquina

# Divisão por peça
custo_maquina_unitario = custo_maquina_total / pecas_por_impressao
custo_energia_unitario = custo_energia_total / pecas_por_impressao

# Custo final por peça
custo_total = custo_material_unitario + custo_maquina_unitario + custo_energia_unitario

# -------------------------
# MARKUP BASEADO NO TEMPO
# -------------------------
if tempo < 1:
    multiplicador = 3.5
elif tempo < 3:
    multiplicador = 3.0
elif tempo < 6:
    multiplicador = 2.5
else:
    multiplicador = 2.2

# -------------------------
# PREÇO E LUCRO (UNITÁRIO)
# -------------------------
preco_venda = custo_total * multiplicador
lucro = preco_venda - custo_total
margem_real = (lucro / preco_venda) * 100 if preco_venda > 0 else 0
lucro_por_hora = lucro / tempo if tempo > 0 else 0

# -------------------------
# SIMULAÇÃO (PRODUÇÃO REAL)
# -------------------------
import math

numero_impressoes = math.ceil(quantidade / pecas_por_impressao)
tempo_total = numero_impressoes * tempo

# 💰 TOTAL REAL (AGORA CORRETO)
custo_total_lote = (
    custo_material_total * numero_impressoes +
    custo_maquina_total * numero_impressoes +
    custo_energia_total * numero_impressoes
)

faturamento_total = preco_venda * quantidade
lucro_total = faturamento_total - custo_total_lote

# 👉 SALVA O CÁLCULO
st.session_state["calculo"] = {
    "nome": nome,
    "peso": peso,
    "tempo": tempo,
    "quantidade": quantidade,
    "pecas_por_impressao": pecas_por_impressao,
    "custo_unitario": custo_total,
    "preco_venda": preco_venda,
    "lucro_unitario": lucro,
    "lucro_total": lucro_total,
    "lucro_por_hora": lucro_por_hora
}

# -------------------------
# RESULTADOS (UNITÁRIO)
# -------------------------
st.subheader("📊 Resultados")

st.metric("🔥 Preço unitário", f"R$ {preco_venda:.2f}")

col1, col2, col3 = st.columns(3)

col1.metric("💰 Custo unitário", f"R$ {custo_total:.2f}")
col2.metric("📈 Lucro unitário", f"R$ {lucro:.2f}")
col3.metric("⏱️ Lucro/hora", f"R$ {lucro_por_hora:.2f}")

col4, col5, col6 = st.columns(3)

col4.metric("⚡ Energia (un)", f"R$ {custo_energia_unitario:.2f}")
col5.metric("📊 Multiplicador", f"{multiplicador:.2f}x")
col6.metric("📊 Margem", f"{margem_real:.1f}%")

st.divider()

# -------------------------
# SIMULAÇÃO DE PRODUÇÃO (TOTAL)
# -------------------------
st.subheader("📦 Simulação de Produção")

col7, col8, col9 = st.columns(3)

col7.metric("📦 Peças", quantidade)
col8.metric("🖨️ Impressões", numero_impressoes)
col9.metric("⏱️ Tempo total (h)", f"{tempo_total:.1f}")

col10, col11, col12 = st.columns(3)

col10.metric("💰 Faturamento", f"R$ {faturamento_total:.2f}")
col11.metric("💸 Custo total", f"R$ {custo_total_lote:.2f}")
col12.metric("📈 Lucro total", f"R$ {lucro_total:.2f}")

# -------------------------
# STATUS DO PRODUTO
# -------------------------
if lucro_por_hora > 5:
  st.success("🟢 Produto Excelente — alta rentabilidade")
elif lucro_por_hora > 2:
  st.warning("🟡 Produto OK — pode melhorar")
else:
  st.error("🔴 Produto Ruim — baixa rentabilidade")

# -------------------------
# BOTÃO DE SALVAR (FORA DO CÁLCULO)
# -------------------------
st.divider()

if "calculo" in st.session_state:
    if st.button("💾 Salvar produto"):
        dados["produtos"].append(st.session_state["calculo"])
        salvar_dados(dados)
        st.success("Produto salvo com sucesso!")

# -------------------------
# LISTAGEM
# -------------------------
st.subheader("📦 Produtos salvos")

if len(dados["produtos"]) == 0:
    st.info("Nenhum produto salvo ainda")
else:
    selecionados = []

    for i, p in enumerate(dados["produtos"]):
        col1, col2 = st.columns([1, 5])

        # CHECKBOX (lado esquerdo)
        with col1:
            if st.checkbox("", key=f"check_{i}"):
                selecionados.append(i)

        # INFORMAÇÕES (lado direito)
        with col2:
            with st.expander(f"{p['nome']}"):
                st.write(f"Peso: {p['peso']} g")
                st.write(f"Tempo: {p['tempo']} h")
                st.write(f"Preço: R$ {p['preco_venda']:.2f}")
                st.write(f"Lucro unitário: R$ {p['lucro_unitario']:.2f}")
                st.write(f"Lucro total: R$ {p['lucro_total']:.2f}")
                st.write(f"Lucro/hora: R$ {p.get('lucro_por_hora', 0):.2f}")

    # BOTÃO DE EXCLUSÃO EM MASSA
    if selecionados:
        if st.button("🗑️ Excluir selecionados"):
            for i in sorted(selecionados, reverse=True):
                dados["produtos"].pop(i)

            salvar_dados(dados)
            st.success("Produtos excluídos!")
            st.rerun()
        
# -------------------------
# RANKING
# -------------------------
st.divider()

st.subheader("🏆 Ranking de Produtos (Mais lucrativos)")

if len(dados["produtos"]) == 0:
    st.info("Nenhum produto para analisar")
else:
    produtos_ordenados = sorted(
        dados["produtos"],
        key=lambda x: x.get("lucro_total", 0),
        reverse=True
    )

    for i, p in enumerate(produtos_ordenados[:5], start=1):
        st.write(f"{i}º - {p['nome']}")
        st.write(f"💰 Lucro/hora: R$ {p.get('lucro_por_hora', 0):.2f}")
        st.write(f"🏷️ Preço: R$ {p['preco_venda']:.2f}")
        st.write("---")
