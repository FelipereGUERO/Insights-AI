import streamlit as st
import plotly.express as px

from components.data_store import inicializar_estado_dados, obter_dados


st.set_page_config(
    page_title="Análises | Insight AI",
    page_icon="📊",
    layout="wide"
)


inicializar_estado_dados()


st.title("📊 Análises")

st.write(
    """
    Aqui o Insight AI começará a gerar análises automáticas com base na planilha carregada.
    """
)

st.divider()


if not st.session_state.dados_carregados:
    st.warning("Nenhuma planilha foi carregada ainda.")
    st.info("Vá até a página Fontes de Dados e envie um arquivo Excel ou CSV.")

else:
    df = obter_dados()

    st.success(f"Analisando o arquivo: {st.session_state.nome_arquivo}")

    st.subheader("Resumo da base de dados")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Linhas", df.shape[0])

    with col2:
        st.metric("Colunas", df.shape[1])

    with col3:
        st.metric("Campos numéricos", len(df.select_dtypes(include="number").columns))

    st.divider()

    st.subheader("Prévia dos dados")
    st.dataframe(df.head(20), use_container_width=True)

    st.divider()

    st.subheader("Gráfico automático")

    colunas_numericas = df.select_dtypes(include="number").columns.tolist()

    if len(colunas_numericas) == 0:
        st.warning("A planilha não possui colunas numéricas para gerar gráficos automaticamente.")

    else:
        coluna_escolhida = st.selectbox(
            "Escolha uma coluna numérica para visualizar:",
            colunas_numericas
        )

        fig = px.histogram(
            df,
            x=coluna_escolhida,
            title=f"Distribuição de {coluna_escolhida}"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Informações das colunas")

    resumo_colunas = []

    for coluna in df.columns:
        resumo_colunas.append(
            {
                "Coluna": coluna,
                "Tipo": str(df[coluna].dtype),
                "Valores vazios": df[coluna].isna().sum(),
                "Valores únicos": df[coluna].nunique()
            }
        )

    st.dataframe(resumo_colunas, use_container_width=True)
