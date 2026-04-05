import streamlit as st
import json
import os

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

st.title("📋 Controle de Produção")

# -------------------------
# FUNÇÕES DE STATUS
# -------------------------
def avancar_status(status):
    fluxo = ["Pedidos", "Produção", "Finalização", "Pronto", "Entregue"]
    idx = fluxo.index(status)
    return fluxo[min(idx + 1, len(fluxo)-1)]

def voltar_status(status):
    fluxo = ["Pedidos", "Produção", "Finalização", "Pronto", "Entregue"]
    idx = fluxo.index(status)
    return fluxo[max(idx - 1, 0)]

# -------------------------
# KANBAN
# -------------------------
col1, col2, col3, col4, col5 = st.columns(5)

status_lista = {
    "Pedidos": col1,
    "Produção": col2,
    "Finalização": col3,
    "Pronto": col4,
    "Entregue": col5
}

for i, p in enumerate(dados["produtos"]):

    status = p.get("status", "Pedidos")

    with status_lista[status]:

        with st.container(border=True):
            st.write(f"**{p['nome']}**")
            st.write(f"💰 R$ {p.get('preco_venda', 0):.2f}")

            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("⬅️", key=f"voltar_{i}"):
                    dados["produtos"][i]["status"] = voltar_status(status)
                    salvar_dados(dados)
                    st.rerun()

            with col_b:
                if st.button("➡️", key=f"avancar_{i}"):
                    dados["produtos"][i]["status"] = avancar_status(status)
                    salvar_dados(dados)
                    st.rerun()
