import streamlit as st
import json
import os
from supabase import create_client, Client

# -------------------------
# CONFIG DA PÁGINA (PRIMEIRO SEMPRE)
# -------------------------
st.set_page_config(
    page_title="Calculadora Maker",
    page_icon="🧮",
    layout="wide"
)

# -------------------------
# CONEXÃO SUPABASE
# -------------------------
SUPABASE_URL = "https://zrpojfuajjckyfetvnpt.supabase.co"
SUPABASE_KEY = "sb_publishable_ISGY11gncdHD2WRhFnmREg_EGdcWQZv"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# SESSION STATE (ÚNICO E LIMPO)
# -------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if "session" not in st.session_state:
    st.session_state.session = None

if "show_login" not in st.session_state:
    st.session_state.show_login = False

if "show_menu" not in st.session_state:
    st.session_state.show_menu = False


# -------------------------
# RESTAURAR SESSÃO (VERSÃO ESTÁVEL REAL)
# -------------------------

def load_session():
    try:
        res = supabase.auth.get_session()

        # 🔥 padrão mais confiável
        if res and hasattr(res, "session") and res.session:
            st.session_state.session = res.session
            st.session_state.user = res.session.user

            supabase.auth.set_session(
                res.session.access_token,
                res.session.refresh_token
            )

        # ❗ NÃO sobrescreve user se já estiver logado
        elif st.session_state.get("user") is None:
            st.session_state.user = None
            st.session_state.session = None

    except Exception:
        pass


# 🔥 executa sempre
load_session()

# -------------------------
# LOGIN (CORRIGIDO)
# -------------------------

def login(email, senha):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": senha
        })

        if res.session:
            st.session_state.user = res.user
            st.session_state.session = res.session

            supabase.auth.set_session(
                res.session.access_token,
                res.session.refresh_token
            )

            return True

        return False

    except Exception as e:
        st.error(f"Erro no login: {e}")
        return False


# -------------------------
# SIGNUP
# -------------------------

def signup(email, senha):
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": senha
        })

        return bool(res.user)

    except Exception as e:
        st.error(f"Erro no cadastro: {e}")
        return False


# -------------------------
# LOGOUT
# -------------------------

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.session = None
    st.rerun()

# -------------------------
# LOGIN UI
# -------------------------
if st.session_state.show_login and st.session_state.user is None:

    st.markdown("### 🔐 Login")

    tab1, tab2 = st.tabs(["Entrar", "Criar conta"])

    # -------------------------
    # TAB LOGIN
    # -------------------------
    with tab1:
        email = st.text_input("Email", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")

        colA, colB = st.columns(2)

        with colA:
            if st.button("Entrar"):
                if login(email, senha):
                    st.session_state.show_login = False
                    st.success("Login realizado!")
                    st.rerun()
                else:
                    st.error("Email ou senha inválidos")

        with colB:
            if st.button("Fechar"):
                st.session_state.show_login = False
                st.rerun()

    # -------------------------
    # TAB CADASTRO
    # -------------------------
    with tab2:
        new_email = st.text_input("Email", key="signup_email")
        new_senha = st.text_input("Senha", type="password", key="signup_senha")

        if st.button("Criar conta"):
            if signup(new_email, new_senha):
                st.success("Conta criada! Faça login agora.")
            else:
                st.error("Erro ao criar conta")

    st.stop()
    
# -------------------------
# ESPAÇAMENTO PARA NÃO FICAR SOB HEADER
# -------------------------

st.markdown("""
<style>
/* empurra todo o conteúdo pra baixo da header */
.block-container {
    padding-top: 5rem !important;
}
</style>
""", unsafe_allow_html=True)
    
# -------------------------
# BOTÃO LOGIN
# -------------------------
col1, col2 = st.columns([7, 2])

with col2:
    user = st.session_state.get("user")

    if user:
        # 🔥 proteção contra user sem email (evita crash)
        email = getattr(user, "email", None)

        if email:
            nome_user = email.split("@")[0].capitalize()
        else:
            nome_user = "Usuário"

        if st.button(f"👤 {nome_user}", use_container_width=True):
            st.session_state.show_menu = not st.session_state.get("show_menu", False)

    else:
        if st.button("🔐 Login", use_container_width=True):
            st.session_state.show_login = True
    

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
# CAPTURA ORÇAMENTO DA URL
# -------------------------
params = st.query_params
orcamento_id = params.get("orcamento")

# -------------------------
# TELA DO CLIENTE (ORÇAMENTO)
# -------------------------
if orcamento_id:

    st.title("📄 Orçamento")

    # 🔍 busca orçamento
    orc = supabase.table("orcamentos") \
        .select("*") \
        .eq("id", orcamento_id) \
        .single() \
        .execute()

    if not orc.data:
        st.error("Orçamento não encontrado")
        st.stop()

    # 🔍 busca itens
    itens = supabase.table("orcamento_itens") \
        .select("*") \
        .eq("orcamento_id", orcamento_id) \
        .execute()

    total = 0
    selecionados_cliente = []

    for i, item in enumerate(itens.data):

        col1, col2 = st.columns([1, 5])

        with col1:
            marcado = st.checkbox("", key=f"cliente_item_{i}", value=True)

        with col2:
            subtotal = item["preco"] * item["quantidade"]

            st.write(f"**{item['nome']}**")
            st.write(f"{item['quantidade']}x - R$ {item['preco']:.2f}")
            st.write(f"Subtotal: R$ {subtotal:.2f}")

        # 🔥 soma só os selecionados
        if marcado:
            total += subtotal
            selecionados_cliente.append(item)

        st.divider()

    # 🔥 TOTAL FORA DO LOOP (CORRETO)
    st.subheader(f"💰 Total selecionado: R$ {total:.2f}")

    # -------------------------
    # BOTÃO DE APROVAÇÃO 
    # -------------------------
    st.divider()

    if orc.data["status"] == "pendente":

        if st.button("✅ Aprovar orçamento", use_container_width=True):

            try:
                supabase.table("orcamentos") \
                    .update({"status": "aprovado"}) \
                    .eq("id", orcamento_id) \
                    .execute()

                import requests

                token = "8742024229:AAHgXkal4aE9gnJmzkBeJZ0yqkDGcPVRWVk"
                chat_id = "8047086065"

                itens_msg = ""
                for item in selecionados_cliente:
                    itens_msg += f"\n• {item['nome']} ({item['quantidade']}x)"

                cliente_nome = orc.data.get("cliente", "Não informado")

                link = f"https://SEU_APP.streamlit.app/?orcamento={orcamento_id}"

                msg = f"""
🚀 *NOVO PEDIDO APROVADO!*

👤 *Cliente:* {cliente_nome}
💰 *Total:* R$ {total:.2f}

📦 *Itens selecionados:*{itens_msg}

🔗 Ver orçamento:
{link}
"""

                url = f"https://api.telegram.org/bot{token}/sendMessage"

                requests.post(url, json={
                    "chat_id": chat_id,
                    "text": msg,
                })

                st.success("Orçamento aprovado com sucesso!")
                st.rerun()

            except Exception as e:
                st.error("Erro ao aprovar orçamento:")
                st.write(e)

    else:
        st.success(f"Status do orçamento: {orc.data['status']}")

    st.stop()
    
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

# -------------------------
# CARREGAR PRODUTOS DO BANCO (NOVO PADRÃO)
# -------------------------

user = st.session_state.get("user")

if user:
    response = supabase.table("produtos") \
        .select("*") \
        .eq("user_id", user.id) \
        .execute()

    produtos = response.data
else:
    produtos = []

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

preco_kg = st.sidebar.number_input("Preço do filamento (R$/kg)", value=115.0)

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
        "Quantidade de Peças",
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
# 📊 DASHBOARD
# -------------------------

if "calculo" in st.session_state:

    c = st.session_state["calculo"]

    # 📊 LAYOUT EM DUAS COLUNAS
    col_esq, col_dir = st.columns(2)

    # -------------------------
    # 📊 POR PEÇA (ESQUERDA)
    # -------------------------
    with col_esq:
        st.subheader("📊 Por Peça")

        col1, col2 = st.columns(2)
        col1.metric("💰 Custo unitário", f"R$ {c['custo_unitario']:.2f}")
        col2.metric("⚡ Energia", f"R$ {c['energia_unitaria']:.2f}")

        col3, col4 = st.columns(2)
        col3.metric("💲 Preço unitário", f"R$ {c['preco_venda']:.2f}")
        col4.metric("📈 Lucro unitário", f"R$ {c['lucro_unitario']:.2f}")

        st.caption(f"Multiplicador: {c['multiplicador']:.2f}x")

        with st.expander("🔍 Ver detalhes dos custos"):
            st.write(f"💰 Custo material total: R$ {c['custo_material_total']:.2f}")
            st.write(f"⚙️ Custo máquina total: R$ {c['custo_maquina_total']:.2f}")
            st.write(f"⚡ Custo energia total: R$ {c['custo_energia_total']:.2f}")

    # -------------------------
    # 📦 PRODUÇÃO (FORNADA)
    # -------------------------
    with col_dir:
        st.subheader("📦 Produção (Fornada)")

        pecas_dia = (24 / c["tempo"]) * c["pecas_por_impressao"] if c["tempo"] > 0 else 0
        lucro_por_impressao = c["lucro_total"] / c["numero_impressoes"] if c["numero_impressoes"] > 0 else 0

        col5, col6, col7 = st.columns(3)
        col5.metric("📦 Peças", c["quantidade"])
        col6.metric("🖨️ Impressões", c["numero_impressoes"])
        col7.metric("⏱️ Tempo total", f"{c['tempo_total']:.1f}h")

        col8, col9, col10 = st.columns(3)
        col8.metric("💰 Faturamento", f"R$ {c['faturamento_total']:.2f}")
        col9.metric("💸 Custo total", f"R$ {c['custo_total_lote']:.2f}")
        col10.metric("📈 Lucro total", f"R$ {c['lucro_total']:.2f}")

        col11, col12 = st.columns(2)
        col11.metric("📆 Peças/dia", f"{pecas_dia:.1f}")
        col12.metric("🖨️ Lucro/Impressão", f"R$ {lucro_por_impressao:.2f}")


# -------------------------
# BOTÃO DE SALVAR (FORA DO CÁLCULO)
# -------------------------
st.divider()

if "calculo" in st.session_state:
    if st.button("💾 Salvar produto"):

        user = st.session_state.get("user")

        if user:
            c = st.session_state["calculo"]

            try:
                supabase.table("produtos").insert({
                    "user_id": user.id,

                    "nome": c["nome"],
                    "peso": c["peso"],
                    "tempo": c["tempo"],
                    "quantidade": c["quantidade"],
                    "pecas_por_impressao": c["pecas_por_impressao"],

                    "custo_unitario": c["custo_unitario"],
                    "preco_venda": c["preco_venda"],
                    "lucro_unitario": c["lucro_unitario"],
                    "lucro_total": c["lucro_total"],
                    "lucro_por_hora": c["lucro_por_hora"],

                    "margem": c["margem"],
                    "multiplicador": c["multiplicador"],

                    "energia_unitaria": c["energia_unitaria"],

                    "tempo_total": c["tempo_total"],
                    "numero_impressoes": c["numero_impressoes"],

                    "faturamento_total": c["faturamento_total"],
                    "custo_total_lote": c["custo_total_lote"],

                    "custo_material_total": c["custo_material_total"],
                    "custo_maquina_total": c["custo_maquina_total"],
                    "custo_energia_total": c["custo_energia_total"],
                }).execute()

                st.success("Produto salvo com sucesso!")

            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

        else:
            st.error("Usuário não autenticado. Faça login novamente.")
            
# -------------------------
# LISTAGEM
# -------------------------
st.subheader("📦 Produtos salvos")

selecionados = []  # 🔥 DEFINE ANTES DE TUDO

if len(produtos) == 0:
    st.info("Faça login para salvar seus produtos!")
else:

    for i, p in enumerate(produtos):
        col1, col2 = st.columns([1, 5])

        # CHECKBOX (lado esquerdo)
        with col1:
            if st.checkbox("", key=f"check_{i}"):
                selecionados.append(i)

        # INFORMAÇÕES (lado direito)
        with col2:
            with st.expander(f"{p['nome']}"):
                st.write(f"faturamento total: R$ {p['faturamento_total']:.2f}")
                st.write(f"Peso: {p['peso']} g")
                st.write(f"Tempo: {p['tempo']} h")
                st.write(f"Preço: R$ {p['preco_venda']:.2f}")
                st.write(f"Lucro unitário: R$ {p['lucro_unitario']:.2f}")
                st.write(f"Lucro total: R$ {p['lucro_total']:.2f}")
                st.write(f"Lucro/hora: R$ {p.get('lucro_por_hora', 0):.2f}")

   # BOTÃO DE EXCLUSÃO EM MASSA (SUPABASE)
if selecionados:
    if st.button("🗑️ Excluir selecionados"):

        user = st.session_state.get("user")

        if not user:
            st.error("Você precisa estar logado")
        else:
            try:
                for i in selecionados:
                    p = produtos[i]

                    supabase.table("produtos") \
                        .delete() \
                        .eq("id", p["id"]) \
                        .eq("user_id", user.id) \
                        .execute()

                st.success("Produtos excluídos com sucesso!")
                st.rerun()

            except Exception as e:
                st.error("Erro ao excluir produtos:")
                st.write("DETALHE:", getattr(e, "args", None))
                st.write("RAW:", e)

# -------------------------
# GERAR ORÇAMENTO
# -------------------------
if selecionados:

    # 🔥 campo do cliente (fica sempre visível)
    cliente = st.text_input("👤 Nome do cliente / empresa")

    if st.button("📄 Gerar orçamento"):

        user = st.session_state.get("user")

        if not user:
            st.error("Você precisa estar logado")

        elif not cliente.strip():
            st.error("Informe o nome do cliente antes de gerar o orçamento")

        else:
            try:
                # -------------------------
                # CRIA ORÇAMENTO (COM CLIENTE)
                # -------------------------
                res = supabase.table("orcamentos").insert({
                    "user_id": user.id,
                    "status": "pendente",
                    "cliente": cliente.strip()
                }).execute()

                # 🔥 pega ID real do banco
                if not res.data:
                    st.error("Erro: orçamento não retornou dados")
                    st.stop()

                orcamento_id = res.data[0]["id"]

            except Exception as e:
                st.error("Erro ao criar orçamento:")
                st.write("DETALHE:", getattr(e, "args", None))
                st.write("RAW:", e)
                st.stop()
            # -------------------------
            # INSERE ITENS
            # -------------------------
            for i in selecionados:
                p = produtos[i]

                try:
                    supabase.table("orcamento_itens").insert({
                        "orcamento_id": orcamento_id,
                        "produto_id": p["id"],
                        "nome": p["nome"],
                        "preco": float(p["preco_venda"]),
                        "quantidade": int(p["quantidade"])
                    }).execute()

                except Exception as e:
                    st.error("Erro ao criar item do orçamento:")
                    st.write("PRODUTO:", p)
                    st.write("DETALHE:", getattr(e, "args", None))
                    st.write("RAW:", e)
                    st.stop()

            # -------------------------
            # LINK FINAL
            # -------------------------
            link = f"?orcamento={orcamento_id}"

            st.success("Orçamento criado com sucesso!")

            url = f"?orcamento={orcamento_id}"

            st.markdown(f"[👉 Abrir orçamento]({url})")
        
# -------------------------
# RANKING
# -------------------------
st.divider()

st.subheader("🏆 Ranking de Produtos (Mais lucrativos)")

if len(produtos) == 0:
    st.info("Faça login para ver os seus produtos mais lucrativos!")
else:
    produtos_ordenados = sorted(
        produtos,
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
