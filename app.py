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

/* Reduz margem lateral e topo */
.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}

/* Remove limite de largura central */
.main {
    max-width: 100%;
}

/* Cards de métricas */
div[data-testid="stMetric"] {
    background-color: #1A1F2B;
    border: 1px solid #2D3748;
    padding: 14px;
    border-radius: 12px;
    text-align: center;
}

/* Valor grande */
div[data-testid="stMetric"] > div {
    color: #00C2FF;
    font-size: 20px;
    font-weight: bold;
}

/* Label menor */
div[data-testid="stMetric"] label {
    color: #A0AEC0;
    font-size: 12px;
}

/* Reduz espaço entre blocos */
div[data-testid="stVerticalBlock"] > div {
    gap: 0.6rem;
}

/* Ajusta colunas para não “quebrar” */
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
# SIDEBAR (CONFIGURAÇÕES)
# -------------------------
st.sidebar.header("⚙️ Configurações")

# MARGEM ALVO
margem_desejada = st.sidebar.slider(
"Margem de lucro (%)",
min_value=10,
max_value=90,
value=60
) / 100

preco_kg = st.sidebar.number_input("Preço do filamento (R$/kg)", value=100.0)

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
# IMPRESSORA (CORRIGIDO)
# -------------------------
st.sidebar.subheader("🖨️ Impressora")

impressoras = {
    "Bambu Lab A1": {"valor": 3500, "vida_util": 4000, "consumo": 0.12},
    "Bambu Lab P1P": {"valor": 6000, "vida_util": 5000, "consumo": 0.15},
    "Bambu Lab X1 Carbon": {"valor": 9000, "vida_util": 6000, "consumo": 0.20},
    "Ender 3 V3 KE": {"valor": 2500, "vida_util": 3000, "consumo": 0.12},
    "Ender 3": {"valor": 1500, "vida_util": 2500, "consumo": 0.10},
    "Prusa MK3": {"valor": 5000, "vida_util": 5000, "consumo": 0.13},
    "Outro": {"valor": None, "vida_util": None, "consumo": None}
}

modelo = st.sidebar.selectbox(
    "Selecione sua impressora",
    list(impressoras.keys()),
    key="modelo_impressora"
)

dados_impressora = impressoras[modelo]

# 🔥 DETECTA MUDANÇA DE MODELO
if "modelo_anterior" not in st.session_state:
    st.session_state.modelo_anterior = modelo

if modelo != st.session_state.modelo_anterior:
    st.session_state["valor_maquina_input"] = dados_impressora["valor"] or 3000.0
    st.session_state["vida_util_input"] = dados_impressora["vida_util"] or 3000
    st.session_state["consumo_input"] = dados_impressora["consumo"] or 0.12

    st.session_state.modelo_anterior = modelo

# VALOR
valor_maquina = st.sidebar.number_input(
    "Valor da impressora (R$)",
    value=float(dados_impressora["valor"]) if dados_impressora["valor"] else 3000.0,
    key="valor_maquina_input"
)

# VIDA ÚTIL
vida_util = st.sidebar.number_input(
    "Vida útil estimada (horas)",
    value=int(dados_impressora["vida_util"]) if dados_impressora["vida_util"] else 3000,
    key="vida_util_input"
)

# MANUTENÇÃO (⚠️ nome de key único)
manutencao_hora = st.sidebar.number_input(
    "Manutenção (R$/h)",
    value=1.0,
    key="manutencao_input"
)

# CONSUMO
consumo_maquina = st.sidebar.number_input(
    "Consumo da impressora (kW)",
    value=float(dados_impressora["consumo"]) if dados_impressora["consumo"] else 0.12,
    key="consumo_input"
)

# CUSTO HORA
if vida_util > 0:
    custo_hora = (valor_maquina / vida_util) + manutencao_hora
else:
    custo_hora = manutencao_hora

st.sidebar.info(f"💰 Custo real: R$ {custo_hora:.2f}/h")
st.sidebar.caption("💡 Valores automáticos — você pode ajustar")

# -------------------------
# INPUTS EM GRID (PROFISSIONAL)
# -------------------------

col1, col2 = st.columns(2)

# 📦 DADOS DO PRODUTO
with col1:
    st.subheader("📦 Produto")

    nome = st.text_input("Nome do produto")
    tipo_produto = st.selectbox("Tipo", ["Chaveiro", "Decoração", "Personalizado"])

# 🏭 PRODUÇÃO (PRINCIPAL)
with col2:
    st.subheader("🏭 Produção")

    peso = st.number_input("Peso (g)", value=50.0)
    tempo = st.number_input("Tempo (h)", value=2.0)

# 🔽 SEGUNDA LINHA (PRODUÇÃO AVANÇADA)
col3, col4 = st.columns(2)

with col3:
    quantidade = st.number_input(
        "Quantidade total",
        min_value=1,
        value=10
    )

with col4:
    pecas_por_impressao = st.number_input(
        "Peças por impressão",
        min_value=1,
        value=1
    )

st.caption("💡 Ex: 100 peças com capacidade de 20 → 5 impressões")

# -------------------------
# BOTÃO DE CÁLCULO
# -------------------------
calcular = st.button("💰 Calcular", use_container_width=True)

# -------------------------
# EXECUÇÃO DO CÁLCULO
# -------------------------
if calcular:

    import math

    # -------------------------
    # CUSTOS BASE (1 IMPRESSÃO)
    # -------------------------
    custo_material_total = (peso / 1000) * preco_kg
    custo_maquina_total = tempo * custo_hora
    custo_energia_total = tempo * custo_kwh * consumo_maquina

    # custo por peça
    custo_material_unitario = custo_material_total / pecas_por_impressao
    custo_maquina_unitario = custo_maquina_total / pecas_por_impressao
    custo_energia_unitario = custo_energia_total / pecas_por_impressao

    custo_unitario = (
        custo_material_unitario +
        custo_maquina_unitario +
        custo_energia_unitario
    )

    # -------------------------
    # PREÇO (BASEADO EM MARGEM)
    # -------------------------
    preco_venda = custo_unitario / (1 - margem_desejada)

    lucro_unitario = preco_venda - custo_unitario
    margem_real = (lucro_unitario / preco_venda) * 100 if preco_venda > 0 else 0

    multiplicador = preco_venda / custo_unitario if custo_unitario > 0 else 0

    # -------------------------
    # SIMULAÇÃO DE PRODUÇÃO
    # -------------------------
    numero_impressoes = math.ceil(quantidade / pecas_por_impressao)
    tempo_total = numero_impressoes * tempo

    custo_total_lote = numero_impressoes * (
        custo_material_total +
        custo_maquina_total +
        custo_energia_total
    )

    faturamento_total = preco_venda * quantidade
    lucro_total = faturamento_total - custo_total_lote

    # 🔥 CORREÇÃO PRINCIPAL
    lucro_por_hora = lucro_total / tempo_total if tempo_total > 0 else 0

    # -------------------------
    # SALVAR
    # -------------------------
    st.session_state["calculo"] = {
        "nome": nome,
        "peso": peso,
        "tempo": tempo,
        "quantidade": quantidade,
        "pecas_por_impressao": pecas_por_impressao,

        "custo_unitario": custo_unitario,
        "preco_venda": preco_venda,

        "lucro_unitario": lucro_unitario,
        "lucro_total": lucro_total,
        "lucro_por_hora": lucro_por_hora,

        "margem": margem_real,
        "multiplicador": multiplicador,

        "energia_unitaria": custo_energia_unitario,

        "tempo_total": tempo_total,
        "numero_impressoes": numero_impressoes,

        "faturamento_total": faturamento_total,
        "custo_total_lote": custo_total_lote,

        "custo_material_total": custo_material_total,
        "custo_maquina_total": custo_maquina_total,
        "custo_energia_total": custo_energia_total,
    }
    
# -------------------------
# DASHBOARD PRINCIPAL (NOVA UI)
# -------------------------

if "calculo" in st.session_state:
    c = st.session_state["calculo"]

    # 🔥 KPIs NO TOPO (FOCO EM DECISÃO)
    col_top1, col_top2, col_top3, col_top4 = st.columns(4)

    col_top1.metric("💰 Preço", f"R$ {c['preco_venda']:.2f}")
    col_top2.metric("📈 Lucro", f"R$ {c['lucro_unitario']:.2f}")
    col_top3.metric("📊 Margem", f"{c['margem']:.1f}%")
    col_top4.metric("⚡ Lucro/h", f"R$ {c['lucro_por_hora']:.2f}")

    # 🧠 STATUS INTELIGENTE (NOVO)
    if c["lucro_por_hora"] >= 20:
        st.success("🚀 Produto Excelente — alta escala e rentabilidade")
    elif c["lucro_por_hora"] >= 10:
        st.success("🟢 Produto Bom — saudável para produção")
    elif c["lucro_por_hora"] >= 5:
        st.warning("🟡 Produto OK — margem apertada")
    else:
        st.error("🔴 Produto Ruim — não compensa produzir")

    st.divider()
    
    # 📊 LAYOUT EM DUAS COLUNAS
    col_esq, col_dir = st.columns(2)
    
   # -------------------------
# 📊 POR PEÇA (ESQUERDA)
# -------------------------
with col_esq:
    st.subheader("📊 Por Peça")

    if "calculo" in st.session_state:
        c = st.session_state["calculo"]

        col1, col2 = st.columns(2)
        col1.metric("💰 Custo unitário", f"R$ {c['custo_unitario']:.2f}")
        col2.metric("⚡ Energia", f"R$ {c['energia_unitaria']:.2f}")

        col3, col4 = st.columns(2)
        col3.metric("💲 Preço unitário", f"R$ {c['preco_venda']:.2f}")
        col4.metric("📈 Lucro unitário", f"R$ {c['lucro_unitario']:.2f}")

        # (opcional - menos importante visualmente)
        st.caption(f"Multiplicador: {c['multiplicador']:.2f}x")


# -------------------------
# 📦 PRODUÇÃO (FORNADA)
# -------------------------
with col_dir:
    st.subheader("📦 Produção (Fornada)")

    if "calculo" in st.session_state:
        c = st.session_state["calculo"]

        # 🔥 Capacidade produtiva REAL
        pecas_dia = (24 / c["tempo"]) * c["pecas_por_impressao"] if c["tempo"] > 0 else 0

        lucro_por_impressao = c["lucro_total"] / c["numero_impressoes"] if c["numero_impressoes"] > 0 else 0

        # 📦 Volume
        col5, col6, col7 = st.columns(3)
        col5.metric("📦 Peças", c["quantidade"])
        col6.metric("🖨️ Impressões", c["numero_impressoes"])
        col7.metric("⏱️ Tempo total", f"{c['tempo_total']:.1f}h")

        # 💰 Financeiro (AGORA COMPLETO)
        col8, col9, col10 = st.columns(3)
        col8.metric("💰 Faturamento", f"R$ {c['faturamento_total']:.2f}")
        col9.metric("💸 Custo total", f"R$ {c['custo_total_lote']:.2f}")
        col10.metric("📈 Lucro total", f"R$ {c['lucro_total']:.2f}")

        # 🚀 Produtividade (NOVO BLOCO)
        col11, col12 = st.columns(2)
        col11.metric("📆 Peças/dia", f"{pecas_dia:.1f}")
        col12.metric("🖨️ Lucro/Impressão", f"R$ {lucro_por_impressao:.2f}")
    
    st.divider()
    
    # 🔍 DETALHES (ESCONDIDOS)
    with st.expander("🔍 Ver detalhes completos"):
        if "calculo" in st.session_state:
            c = st.session_state["calculo"]
    
            st.write(f"💰 Custo material total: R$ {c['custo_material_total']:.2f}")
            st.write(f"⚙️ Custo máquina total: R$ {c['custo_maquina_total']:.2f}")
            st.write(f"⚡ Custo energia total: R$ {c['custo_energia_total']:.2f}")

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
        st.write(f"**{i}º - {p['nome']}**")
        
        col1, col2, col3 = st.columns(3)
        
        col1.metric("📈 Lucro total", f"R$ {p.get('lucro_total', 0):.2f}")
        col2.metric("💰 Lucro/hora", f"R$ {p.get('lucro_por_hora', 0):.2f}")
        col3.metric("🏷️ Preço", f"R$ {p.get('preco_venda', 0):.2f}")
        
        st.divider()
