import streamlit as st
import pandas as pd
import plotly.express as px

from components.sidebar import mostrar_sidebar

# ==========================
# Configuração da página
# ==========================

st.set_page_config(
    page_title="Insight AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
mostrar_sidebar()

# ==========================
# Título
# ==========================

st.title("📊 Insight AI")

st.caption("Transformando dados em decisões inteligentes.")

st.divider()

st.header("👋 Bem-vindo!")

st.write(
    """
O Insight AI será uma plataforma capaz de:

- 📈 Analisar vendas
- 📂 Receber planilhas Excel
- 🔗 Conectar APIs do ERP
- 📊 Gerar dashboards automaticamente
- 🤖 Encontrar oportunidades usando IA
- 📄 Criar relatórios inteligentes
- 💬 Conversar com seus dados
"""
)

st.divider()

# ==========================
# Cards
# ==========================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 Faturamento", "R$ 185.000", "+12%")

with col2:
    st.metric("👥 Clientes", "1.245", "+8")

with col3:
    st.metric("📦 Produtos", "87", "+5")

with col4:
    st.metric("📈 Crescimento", "12%", "+2%")

st.divider()

# ==========================
# Dados fictícios
# ==========================

dados = pd.DataFrame({
    "Mês": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
    "Vendas": [150, 180, 210, 240, 260, 310]
})

fig = px.line(
    dados,
    x="Mês",
    y="Vendas",
    markers=True,
    title="📈 Evolução das vendas"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==========================
# Insights
# ==========================

st.subheader("💡 Insights encontrados")

st.success("📈 Produto A apresentou crescimento de 18%.")

st.warning("⚠ Região Sul teve queda nas vendas.")

st.info("💡 Existe oportunidade para aumentar o estoque do Produto B.")
