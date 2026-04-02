import streamlit as st
import json
import os

# -------------------------
# CONFIG DA PÁGINA
# -------------------------

st.title("🧮 Precificação de Impressão 3D")
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
custo_fixo = st.sidebar.number_input("Custo fixo por peça (R$)", value=2.0)

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
# TÍTULO
# -------------------------
st.title("🧮 Precificação de Impressão 3D")
st.caption("Calcule custo, preço e lucro das suas peças")

# -------------------------
# INPUTS
# -------------------------
st.subheader("📥 Dados da peça")

nome = st.text_input("Nome do produto")
peso = st.number_input("Peso (g)", min_value=0.0, value=50.0)
tempo = st.number_input("Tempo de impressão (horas)", min_value=0.0, value=2.0)

# -------------------------
# CÁLCULO
# -------------------------
if st.button("💰 Calcular preço"):

    if nome == "":
        st.warning("Digite um nome para o produto")
    else:
        custo_material = (peso / 1000) * preco_kg
        custo_maquina = tempo * custo_hora
        custo_total = custo_material + custo_maquina + custo_fixo

        preco_venda = custo_total * multiplicador
        lucro = preco_venda - custo_total
        margem_real = (lucro / preco_venda) * 100 if preco_venda > 0 else 0
        lucro_por_hora = lucro / tempo if tempo > 0 else 0

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

        st.divider()

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
        # SALVAR PRODUTO
        # -------------------------
        if st.button("💾 Salvar produto"):
            novo_produto = {
                "nome": nome,
                "peso": peso,
                "tempo": tempo,
                "custo_total": custo_total,
                "preco_venda": preco_venda,
                "lucro": lucro,
                "tipo": tipo_produto
            }

            dados["produtos"].append(novo_produto)
            salvar_dados(dados)

            st.success("Produto salvo com sucesso!")

# -------------------------
# LISTAGEM
# -------------------------
st.subheader("📦 Produtos salvos")

if len(dados["produtos"]) == 0:
    st.info("Nenhum produto salvo ainda")
else:
    for p in dados["produtos"]:
        with st.expander(f"{p['nome']} ({p['tipo']})"):
            st.write(f"Peso: {p['peso']} g")
            st.write(f"Tempo: {p['tempo']} h")
            st.write(f"Preço: R$ {p['preco_venda']:.2f}")
            st.write(f"Lucro: R$ {p['lucro']:.2f}")
