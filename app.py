import streamlit as st
import json
import os
import math

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(
    page_title="Calculadora Maker",
    page_icon="🧮",
    layout="wide"
)

# -------------------------
# MENU
# -------------------------
pagina = st.radio(
    "Menu",
    ["🧮 Calculadora", "📋 Produção"],
    horizontal=True
)

# -------------------------
# CARREGAMENTO DE DADOS
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
# SIDEBAR (CONFIG)
# -------------------------
st.sidebar.header("⚙️ Configurações")

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

distribuidora = st.sidebar.selectbox("Distribuidora", list(distribuidoras.keys()))

if distribuidoras[distribuidora] is not None:
    custo_kwh = distribuidoras[distribuidora]
else:
    custo_kwh = st.sidebar.number_input("Custo energia (R$/kWh)", value=0.80)

# -------------------------
# IMPRESSORA
# -------------------------
st.sidebar.subheader("🖨️ Impressora")

impressoras = {
    "Bambu Lab A1": {"valor": 3500, "vida_util": 4000, "consumo": 0.12},
    "Bambu Lab P1P": {"valor": 6000, "vida_util": 5000, "consumo": 0.15},
    "Bambu Lab X1 Carbon": {"valor": 9000, "vida_util": 6000, "consumo": 0.20},
    "Ender 3 V3 KE": {"valor": 2500, "vida_util": 3000, "consumo": 0.12},
    "Ender 3": {"valor": 1500, "vida_util": 2500, "consumo": 0.10},
    "Outro": {"valor": None, "vida_util": None, "consumo": None}
}

modelo = st.sidebar.selectbox("Modelo", list(impressoras.keys()))

dados_impressora = impressoras[modelo]

valor_maquina = st.sidebar.number_input(
    "Valor da impressora",
    value=float(dados_impressora["valor"] or 3000.0)
)

vida_util = st.sidebar.number_input(
    "Vida útil (h)",
    value=int(dados_impressora["vida_util"] or 3000)
)

manutencao_hora = st.sidebar.number_input("Manutenção (R$/h)", value=1.0)

consumo_maquina = st.sidebar.number_input(
    "Consumo (kW)",
    value=float(dados_impressora["consumo"] or 0.12)
)

if vida_util > 0:
    custo_hora = (valor_maquina / vida_util) + manutencao_hora
else:
    custo_hora = manutencao_hora

st.sidebar.info(f"💰 Custo: R$ {custo_hora:.2f}/h")

# -------------------------
# PÁGINA: CALCULADORA
# -------------------------
if pagina == "🧮 Calculadora":

    st.title("🧮 Calculadora")

    col1, col2 = st.columns(2)

    with col1:
        nome = st.text_input("Nome do produto")

        peso = st.number_input("Peso (g)", value=50.0)
        tempo = st.number_input("Tempo (h)", value=2.0)

    with col2:
        quantidade = st.number_input("Quantidade", value=10)
        pecas_por_impressao = st.number_input("Peças por impressão", value=1)

    calcular = st.button("💰 Calcular")

    if calcular:

        custo_material_total = (peso / 1000) * preco_kg
        custo_material_unitario = custo_material_total / pecas_por_impressao

        custo_maquina_total = tempo * custo_hora
        custo_energia_total = tempo * custo_kwh * consumo_maquina

        custo_total = (
            custo_material_unitario +
            custo_maquina_total / pecas_por_impressao +
            custo_energia_total / pecas_por_impressao
        )

        if tempo < 1:
            multiplicador = 3.5
        elif tempo < 3:
            multiplicador = 3.0
        elif tempo < 6:
            multiplicador = 2.5
        else:
            multiplicador = 2.2

        preco_venda = custo_total * multiplicador
        lucro = preco_venda - custo_total
        margem = (lucro / preco_venda) * 100 if preco_venda > 0 else 0
        lucro_hora = lucro / tempo if tempo > 0 else 0

        numero_impressoes = math.ceil(quantidade / pecas_por_impressao)

        st.session_state["calculo"] = {
            "nome": nome,
            "peso": peso,
            "tempo": tempo,
            "quantidade": quantidade,
            "pecas_por_impressao": pecas_por_impressao,
            "preco_venda": preco_venda,
            "lucro_unitario": lucro,
            "lucro_por_hora": lucro_hora,
            "margem": margem,
            "numero_impressoes": numero_impressoes,
            "status": "Pedidos"
        }

    if "calculo" in st.session_state:
        st.success("Cálculo realizado!")

# -------------------------
# PÁGINA: PRODUÇÃO
# -------------------------
elif pagina == "📋 Produção":

    st.title("📋 Kanban")

    if "calculo" in st.session_state:

        c = st.session_state["calculo"]

        st.write(f"Produto: {c['nome']}")

        status = st.selectbox(
            "Status",
            ["Pedidos", "Produção", "Finalização", "Pronto", "Entregue"],
            index=["Pedidos", "Produção", "Finalização", "Pronto", "Entregue"].index(c["status"])
        )

        st.session_state["calculo"]["status"] = status

# -------------------------
# BOTÃO SALVAR
# -------------------------
st.divider()

if "calculo" in st.session_state:
    if st.button("💾 Salvar produto"):
        dados["produtos"].append(st.session_state["calculo"])
        salvar_dados(dados)
        st.success("Salvo com sucesso!")
