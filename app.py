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
# STYLE DA PÁGINA
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
</style>
""", unsafe_allow_html=True)

# -------------------------
# TÍTULO
# -------------------------
st.title("🧮 MakerSuite")

# -------------------------
# FUNÇÕES
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

margem_desejada = st.sidebar.slider("Margem (%)", 10, 90, 60) / 100
preco_kg = st.sidebar.number_input("Preço filamento", value=115.0)
custo_kwh = 0.92
consumo_maquina = 0.12
custo_hora = 2.0

# -------------------------
# INPUTS
# -------------------------
col1, col2 = st.columns(2)

with col1:
    nome = st.text_input("Nome")

with col2:
    peso = st.number_input("Peso (g)", 50.0)
    tempo = st.number_input("Tempo (h)", 2.0)

quantidade = st.number_input("Quantidade", 1, 10)
pecas_por_impressao = st.number_input("Peças por impressão", 1, 1)

calcular = st.button("Calcular")

# -------------------------
# CÁLCULO
# -------------------------
if calcular:
    import math

    custo_material = (peso/1000)*preco_kg
    custo_maquina = tempo*custo_hora
    custo_energia = tempo*custo_kwh*consumo_maquina

    custo_unitario = (custo_material + custo_maquina + custo_energia)/pecas_por_impressao
    preco = custo_unitario/(1-margem_desejada)

    lucro_unit = preco - custo_unitario

    impressoes = math.ceil(quantidade/pecas_por_impressao)
    tempo_total = impressoes*tempo

    custo_total = impressoes*(custo_material+custo_maquina+custo_energia)
    faturamento = preco*quantidade
    lucro_total = faturamento - custo_total

    lucro_hora = lucro_total/tempo_total if tempo_total>0 else 0

    st.session_state["calculo"] = {
        "nome": nome,
        "custo_unitario": custo_unitario,
        "preco": preco,
        "lucro_unit": lucro_unit,
        "lucro_total": lucro_total,
        "lucro_hora": lucro_hora,
        "energia_unitaria": custo_energia/pecas_por_impressao,
        "quantidade": quantidade,
        "tempo_total": tempo_total,
        "impressoes": impressoes,
        "faturamento": faturamento,
        "custo_total": custo_total
    }

# -------------------------
# DASHBOARD
# -------------------------
if "calculo" in st.session_state:
    c = st.session_state["calculo"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Preço", f"R$ {c['preco']:.2f}")
    col2.metric("Lucro", f"R$ {c['lucro_unit']:.2f}")
    col3.metric("Lucro/h", f"R$ {c['lucro_hora']:.2f}")

    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.metric("Custo", f"R$ {c['custo_unitario']:.2f}")
        st.metric("Energia", f"R$ {c.get('energia_unitaria', 0):.2f}")

    with col_dir:
        st.metric("Lucro total", f"R$ {c['lucro_total']:.2f}")
        st.metric("Qtd", c["quantidade"])

# -------------------------
# SALVAR
# -------------------------
st.divider()

if "calculo" in st.session_state:
    if st.button("Salvar"):
        dados["produtos"].append(st.session_state["calculo"])
        salvar_dados(dados)
        st.success("Salvo!")

# -------------------------
# LISTAGEM
# -------------------------
st.subheader("Produtos")

if len(dados["produtos"]) == 0:
    st.info("Nenhum")
else:
    selecionados = []

    for i, p in enumerate(dados["produtos"]):
        col1, col2 = st.columns([1,5])

        with col1:
            if st.checkbox("", key=f"c{i}"):
                selecionados.append(i)

        with col2:
            with st.expander(p["nome"]):
                st.write(p)

    if selecionados:
        if st.button("Excluir"):
            for i in sorted(selecionados, reverse=True):
                dados["produtos"].pop(i)
            salvar_dados(dados)
            st.rerun()

# -------------------------
# RANKING
# -------------------------
st.divider()
st.subheader("Ranking")

if dados["produtos"]:
    ranking = sorted(dados["produtos"], key=lambda x: x.get("lucro_total",0), reverse=True)

    for i, p in enumerate(ranking[:5],1):
        st.write(f"{i}º - {p['nome']}")
        st.write(f"Lucro: R$ {p.get('lucro_total',0):.2f}")
        st.write("---")
