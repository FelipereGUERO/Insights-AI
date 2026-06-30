import streamlit as st
import pandas as pd
import plotly.express as px

from components.sidebar import mostrar_sidebar
from components.style import carregar_css

# ==================================================
# Configuração da página
# ==================================================

st.set_page_config(
    page_title="Insight AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# Carrega o CSS personalizado
# ==================================================

carregar_css()

# ==================================================
# Sidebar
# ==================================================

mostrar_sidebar()

# ==================================================
# Cabeçalho
# ==================================================

st.title("📊 Insight AI")

st.caption("Transformando dados em decisões inteligentes.")

st.divider()

st.header("👋 Bem-vindo!")

st.write(
    """
O **Insight AI** será uma plataforma inteligente capaz de:

- 📈 Analisar vendas
- 📂 Receber planilhas Excel
- 🔗 Conectar APIs do ERP
- 🗄️ Conectar bancos de dados
- 📊 Gerar dashboards automaticamente
- 🤖 Encontrar oportunidades usando IA
- 📄 Criar relatórios inteligentes
- 💬 Conversar com seus dados
"""
)

st.divider()

# ==================================================
# Cards principais
# ==================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Faturamento",
        value="R$ 185.000",
        delta="+12%"
    )

with col2:
    st.metric(
        label="👥 Clientes",
        value="1.245",
        delta="+8"
    )

with col3:
    st.metric(
        label="📦 Produtos",
        value="87",
        delta="+5"
    )

with col4:
    st.metric(
        label="📈 Crescimento",
        value="12%",
        delta="+2%"
    )

st.divider()

# ==================================================
# Dados fictícios
# ==================================================

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

fig.update_layout(
    height=450,
    xaxis_title="",
    yaxis_title="Vendas",
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==================================================
# Central de Insights
# ==================================================

st.subheader("💡 Central de Insights")

st.success("📈 Produto A apresentou crescimento de 18% nesta semana.")

st.warning("⚠ Região Sul apresentou queda de 9% nas vendas.")

st.info("💡 Existe oportunidade para aumentar o estoque do Produto B.")

st.success("🚀 O faturamento está acima da média dos últimos 6 meses.")

st.warning("⚠ Cliente Premium 'Empresa XYZ' está há 35 dias sem comprar.")

st.divider()

# ==================================================
# Próximas funcionalidades
# ==================================================

st.subheader("🚀 Em desenvolvimento")

st.checkbox("Upload de planilhas", value=False, disabled=True)

st.checkbox("Conexão via API", value=False, disabled=True)

st.checkbox("Conexão com Banco de Dados", value=False, disabled=True)

st.checkbox("Insight Engine", value=False, disabled=True)

st.checkbox("Agente de IA", value=False, disabled=True)

st.checkbox("Relatórios Inteligentes", value=False, disabled=True)
