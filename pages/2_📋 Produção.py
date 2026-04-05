import streamlit as st
import json
import os

st.set_page_config(page_title="Produção", layout="wide")

st.title("📋 Controle de Produção")

# -------------------------
# CARREGAR DADOS
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
# STATUS FLOW
# -------------------------
def avancar(status):
    fluxo = ["Pedidos", "Produção", "Finalização", "Pronto", "Entregue"]
    idx = fluxo.index(status)
    return fluxo[min(idx + 1, len(fluxo)-1)]

def voltar(status):
    fluxo = ["Pedidos", "Produção", "Finalização", "Pronto", "Entregue"]
    idx = fluxo.index(status)
    return fluxo[max(idx - 1, 0)]

# -------------------------
# COLUNAS (KANBAN)
# -------------------------
col1, col2, col3, col4, col5 = st.columns(5)

colunas = {
    "Pedidos": col1,
    "Produção": col2,
    "Finalização": col3,
    "Pronto": col4,
    "Entregue": col5
}

# -------------------------
# CARDS
# -------------------------
for i, p in enumerate(dados["produtos"]):

    status = p.get("status", "Pedidos")

    with colunas[status]:

        with st.container(border=True):
            st.markdown(f"### {p.get('nome', 'Sem nome')}")

            st.write(f"💰 R$ {p.get('preco_venda', 0):.2f}")

            # STATUS
            st.caption(f"📌 {status}")

            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("⬅️", key=f"back_{i}"):
                    dados["produtos"][i]["status"] = voltar(status)
                    salvar_dados(dados)
                    st.rerun()

            with col_b:
                if st.button("➡️", key=f"next_{i}"):
                    dados["produtos"][i]["status"] = avancar(status)
                    salvar_dados(dados)
                    st.rerun()

# -------------------------
# RESUMO
# -------------------------
st.divider()

st.subheader("📊 Resumo")

total = len(dados["produtos"])

pedidos = len([p for p in dados["produtos"] if p.get("status") == "Pedidos"])
producao = len([p for p in dados["produtos"] if p.get("status") == "Produção"])
finalizado = len([p for p in dados["produtos"] if p.get("status") == "Finalização"])
pronto = len([p for p in dados["produtos"] if p.get("status") == "Pronto"])
entregue = len([p for p in dados["produtos"] if p.get("status") == "Entregue"])

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("📦 Pedidos", pedidos)
col2.metric("🏭 Produção", producao)
col3.metric("🔧 Finalização", finalizado)
col4.metric("✅ Pronto", pronto)
col5.metric("🚚 Entregue", entregue)
