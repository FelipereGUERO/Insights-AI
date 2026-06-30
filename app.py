import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Insight AI",
    page_icon="📊",
    layout="wide"
)

# ----------------------------
# Título
# ----------------------------

st.title("📊 Insight AI")

st.caption("Transformando dados em decisões inteligentes.")

st.divider()

st.header("👋 Bem-vindo!")

st.write(
    """
O Insight AI será uma plataforma capaz de:

- Analisar vendas;
- Gerar dashboards automaticamente;
- Encontrar oportunidades;
- Detectar problemas;
- Criar previsões;
- Conversar com seus dados.
"""
)

st.divider()

# ----------------------------
# Cards
# ----------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Faturamento", "R$ 185.000", "+12%")

col2.metric("👥 Clientes", "1.245", "+8")

col3.metric("📦 Produtos", "87")

col4.metric("📈 Crescimento", "12%")

st.divider()

# ----------------------------
# Dados fictícios
# ----------------------------

dados = pd.DataFrame(
    {
        "Mês": [
            "Jan",
            "Fev",
            "Mar",
            "Abr",
            "Mai",
            "Jun"
        ],
        "Vendas": [
            150,
            180,
            210,
            240,
            260,
            310
        ]
    }
)

fig = px.line(
    dados,
    x="Mês",
    y="Vendas",
    markers=True,
    title="Evolução das vendas"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("💡 Insights encontrados")

st.success("Produto A apresentou crescimento de 18%.")

st.warning("Região Sul teve queda nas vendas.")

st.info("Existe oportunidade para aumentar o estoque do Produto B.")
