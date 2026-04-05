import streamlit as st
import json
import os
import math
import streamlit.components.v1 as components

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="column"] {
    padding: 0 6px;
}
</style>
""", unsafe_allow_html=True)

def card(titulo, valor):
    return f"""
    <div style="
        background: linear-gradient(180deg, #111827, #0B1220);
        padding: 18px 16px;
        border-radius: 18px;
        height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        color: white;

        /* ESSENCIAL PRA MOSTRAR O RADIUS */
        margin: 8px 4px;
        
        /* BORDA INTERNA (truque visual) */
        box-shadow: 
            0 0 0 1px rgba(255,255,255,0.08),
            0 8px 25px rgba(0,0,0,0.45);

        transition: all 0.2s ease;
    "
    onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 0 0 1px rgba(0,194,255,0.5), 0 12px 30px rgba(0,0,0,0.6)';"
    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 0 0 1px rgba(255,255,255,0.08), 0 8px 25px rgba(0,0,0,0.45)';"
    >

        <!-- Título -->
        <div style="
            font-size: 12px;
            color: rgba(255,255,255,0.7);
            margin-bottom: 6px;
        ">
            {titulo}
        </div>

        <!-- Valor -->
        <div style="
            font-size: 24px;
            font-weight: 700;
            color: #FFFFFF;
        ">
            {valor}
        </div>

    </div>
    """
    
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

    st.title("🧮 Calculadora Maker")

    col1, col2 = st.columns(2)

    with col1:
        nome = st.text_input("Nome do produto", key="nome_produto")
        peso = st.number_input("Peso (g)", value=50.0, key="peso_produto")
        tempo = st.number_input("Tempo (h)", value=2.0, key="tempo_produto")

    with col2:
        quantidade = st.number_input("Quantidade", value=10, key="quantidade_produto")
        pecas_por_impressao = st.number_input("Peças por impressão", value=1, key="pecas_produto")

    calcular = st.button("💰 Calcular", use_container_width=True)

    # -------------------------
    # RESULTADO DO CÁLCULO
    # -------------------------
    if calcular:

        custo_material_total = (peso / 1000) * preco_kg
        custo_material_unitario = custo_material_total / pecas_por_impressao

        custo_maquina_total = tempo * custo_hora
        custo_energia_total = tempo * custo_kwh * consumo_maquina

        custo_maquina_unitario = custo_maquina_total / pecas_por_impressao
        custo_energia_unitario = custo_energia_total / pecas_por_impressao

        custo_total = custo_material_unitario + custo_maquina_unitario + custo_energia_unitario

        # MARKUP
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
        tempo_total = numero_impressoes * tempo

        custo_total_lote = (
            custo_material_total * numero_impressoes +
            custo_maquina_total * numero_impressoes +
            custo_energia_total * numero_impressoes
        )

        faturamento_total = preco_venda * quantidade
        lucro_total = faturamento_total - custo_total_lote

        # SALVAR NO STATE
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
            "tempo_total": tempo_total,

            "faturamento_total": faturamento_total,
            "custo_total_lote": custo_total_lote,
            "lucro_total": lucro_total,

            "custo_material_total": custo_material_total,
            "custo_maquina_total": custo_maquina_total,
            "custo_energia_total": custo_energia_total,

            "status": "Pedidos"
        }
        
    # -------------------------
    # DASHBOARD
    # -------------------------
    if "calculo" in st.session_state:

        c = st.session_state["calculo"]

        st.divider()

        col_top1, col_top2, col_top3, col_top4 = st.columns(4)

        with col_top1:
            components.html(card("💰 Preço", f"R$ {c['preco_venda']:.2f}"), height=120)

        with col_top2:
            components.html(card("📈 Lucro", f"R$ {c['lucro_unitario']:.2f}"), height=120)

        with col_top3:
            components.html(card("📊 Margem", f"{c['margem']:.1f}%"), height=120)

        with col_top4:
            components.html(card("⚡ Lucro/h", f"R$ {c['lucro_por_hora']:.2f}"), height=120)

        st.divider()

        # UNITÁRIO E PRODUÇÃO (AGORA DENTRO DO IF)
        col_esq, col_dir = st.columns(2)

        with col_esq:
            st.subheader("📊 Unitário")

            col1, col2 = st.columns(2)

            with col1:
                components.html(
                    card("💰 Custo", f"R$ {(c['preco_venda'] - c['lucro_unitario']):.2f}"),
                    height=120
                )

            with col2:
                components.html(
                    card("📈 Lucro", f"R$ {c['lucro_unitario']:.2f}"),
                    height=120
                )

        with col_dir:
            st.subheader("📦 Produção")

            col3, col4, col5 = st.columns(3)

            with col3:
                components.html(card("📦 Peças", c["quantidade"]), height=120)

            with col4:
                components.html(card("🖨️ Impressões", c["numero_impressoes"]), height=120)

            with col5:
                components.html(card("⏱️ Tempo", f"{c['tempo_total']:.1f}h"), height=120)

            col6, col7, col8 = st.columns(3)

            with col6:
                components.html(card("💰 Faturamento", f"R$ {c['faturamento_total']:.2f}"), height=120)

            with col7:
                components.html(card("💸 Custo total", f"R$ {c['custo_total_lote']:.2f}"), height=120)

            with col8:
                components.html(card("📈 Lucro total", f"R$ {c['lucro_total']:.2f}"), height=120)

        st.divider()

        with st.expander("🔍 Ver detalhes completos"):
            st.write(f"💰 Custo material total: R$ {c['custo_material_total']:.2f}")
            st.write(f"⚙️ Custo máquina total: R$ {c['custo_maquina_total']:.2f}")
            st.write(f"⚡ Custo energia total: R$ {c['custo_energia_total']:.2f}")

        if c["lucro_por_hora"] > 5:
            st.success("🟢 Produto Excelente")
        elif c["lucro_por_hora"] > 2:
            st.warning("🟡 Produto OK")
        else:
            st.error("🔴 Produto Ruim")
            
# -------------------------
# BOTÃO SALVAR
# -------------------------
st.divider()

if "calculo" in st.session_state:
    if st.button("💾 Salvar produto"):
        dados["produtos"].append(st.session_state["calculo"])
        salvar_dados(dados)
        st.success("Salvo com sucesso!")
