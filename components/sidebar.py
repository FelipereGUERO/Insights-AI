import streamlit as st

def mostrar_sidebar():

    with st.sidebar:

        st.title("📊 Insight AI")

        st.caption("Transformando dados em decisões inteligentes")

        st.divider()

        st.page_link("app.py", label="🏠 Dashboard")

        st.page_link("pages/Analises.py", label="📈 Análises")

        st.page_link("pages/Dados.py", label="📂 Dados")

        st.page_link("pages/Relatorios.py", label="📄 Relatórios")

        st.page_link("pages/Agente.py", label="🤖 Insight AI")

        st.page_link("pages/Configuracoes.py", label="⚙ Configurações")
