import streamlit as st
import json
import os

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

tipo_produto = st.sidebar.selectbox(
    "Tipo de produto",
    ["Chaveiro", "Decoração", "Peça Técnica"]
)

margens = {
    "Chaveiro": 4.0,
    "Decoração": 3.0,
    "Peça Técnica": 2.5
}

multiplicador = margens[tipo_produto]

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

st.divider()

# -------------------------
# CUSTOS
# -------------------------
st.subheader("💰 Custos")

preco_kg = st.number_input("Preço do filamento (R$/kg)", value=100.0)
custo_hora = st.number_input("Custo da máquina por hora (R$)", value=2.0)
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

st.divider()

# -------------------------
# CUSTOS
# -------------------------
st.subheader("💰 Custos")

preco_kg = st.number_input("Preço do filamento (R$/kg)", value=100.0)
custo_hora = st.number_input("Custo da máquina por hora (R$)", value=2.0)

# -------------------------
# CÁLCULO
# -------------------------
if st.button("💰 Calcular preço"):

    if nome == "":
        st.warning("Digite um nome para o produto")
    else:
        custo_material = (peso / 1000) * preco_kg
        custo_maquina = tempo * custo_hora
        custo_energia = tempo * custo_kwh * consumo_maquina

        custo_total = custo_material + custo_maquina + custo_energia

        preco_venda = custo_total * multiplicador
        lucro = preco_venda - custo_total
        margem_real = (lucro / preco_venda) * 100 if preco_venda > 0 else 0
        lucro_por_hora = lucro / tempo if tempo > 0 else 0

        faturamento_total = preco_venda * quantidade
        lucro_total = lucro * quantidade
        tempo_total = tempo * quantidade

        # 👉 SALVA O CÁLCULO NA MEMÓRIA
        st.session_state["calculo"] = {
            "nome": nome,
            "peso": peso,
            "tempo": tempo,
            "custo_total": custo_total,
            "preco_venda": preco_venda,
            "lucro": lucro,
            "tipo": tipo_produto,
            "lucro_por_hora": lucro_por_hora
        }

        # -------------------------
        # RESULTADOS
        # -------------------------
        st.subheader("📊 Resultados")

        col1, col2 = st.columns(2)

        col1.metric("Custo Total", f"R$ {custo_total:.2f}")
        col2.metric("Preço Sugerido", f"R$ {preco_venda:.2f}")

        col1.metric("Lucro", f"R$ {lucro:.2f}")
        col2.metric("Margem", f"{margem_real:.1f}%")

        col1.metric("Lucro por hora", f"R$ {lucro_por_hora:.2f}")
        col2.metric("⚡ Energia", f"R$ {custo_energia:.2f}")

        st.divider()

        st.subheader("📦 Simulação de Produção")

        col3, col4 = st.columns(2)

        col3.metric("Faturamento Total", f"R$ {faturamento_total:.2f}")
        col4.metric("Lucro Total", f"R$ {lucro_total:.2f}")

        col3.metric("Tempo Total (h)", f"{tempo_total:.1f}")

        # -------------------------
        # INDICADOR INTELIGENTE
        # -------------------------
        if lucro_por_hora < 2:
            st.error("❌ Baixa rentabilidade — não vale a pena")
        elif lucro_por_hora < 5:
            st.warning("⚠️ Rentabilidade média — pode melhorar")
        else:
            st.success("✅ Alta rentabilidade — ótimo produto")

# -------------------------
# BOTÃO DE SALVAR (FORA DO CÁLCULO)
# -------------------------
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
            with st.expander(f"{p['nome']} ({p['tipo']})"):
                st.write(f"Peso: {p['peso']} g")
                st.write(f"Tempo: {p['tempo']} h")
                st.write(f"Preço: R$ {p['preco_venda']:.2f}")
                st.write(f"Lucro: R$ {p['lucro']:.2f}")
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

st.subheader("🏆 Ranking de Produtos (Mais lucrativos)")

if len(dados["produtos"]) == 0:
    st.info("Nenhum produto para analisar")
else:
    produtos_ordenados = sorted(
        dados["produtos"],
        key=lambda x: x.get("lucro_por_hora", 0),
        reverse=True
    )

    for i, p in enumerate(produtos_ordenados[:5], start=1):
        st.write(f"{i}º - {p['nome']}")
        st.write(f"💰 Lucro/hora: R$ {p.get('lucro_por_hora', 0):.2f}")
        st.write(f"🏷️ Preço: R$ {p['preco_venda']:.2f}")
        st.write("---")
