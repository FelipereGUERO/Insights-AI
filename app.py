import streamlit as st

# ==========================
# Configuração da página
# ==========================

st.set_page_config(
    page_title="Insight AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================
# Sidebar
# ==========================

with st.sidebar:

    st.title("📊 Insight AI")

    st.caption("Transformando dados em decisões inteligentes.")

    st.divider()

    st.page_link("app.py", label="🏠 Dashboard")

    st.page_link("pages/Analises.py", label="📈 Análises")

    st.page_link("pages/Dados.py", label="📂 Dados")

    st.page_link("pages/Relatorios.py", label="📄 Relatórios")

    st.page_link("pages/Agente.py", label="🤖 Insight AI")

    st.page_link("pages/Configuracoes.py", label="⚙ Configurações")

# ==========================
# Página principal
# ==========================

st.title("📊 Dashboard")

st.subheader("Bem-vindo ao Insight AI")

st.write(
    """
Nosso objetivo é transformar dados em decisões inteligentes.

Em breve você poderá:

- Fazer upload de planilhas;
- Conectar APIs do seu ERP;
- Gerar dashboards automaticamente;
- Receber insights da IA;
- Conversar com seus dados.
"""
)

st.info("Sprint 1 - Interface em desenvolvimento 🚀")
