import streamlit as st
import pandas as pd

from engines.data_engine import ler_arquivo, resumo_dados, limpar_dados


st.set_page_config(
    page_title="Fontes de Dados | Insight AI",
    page_icon="📊",
    layout="wide"
)


st.title("📊 Fontes de Dados")

st.write(
    """
    Envie uma planilha Excel ou CSV para que o Insight AI leia os dados,
    organize as informações e prepare a base para gerar gráficos, indicadores
    e insights inteligentes.
    """
)

st.divider()


arquivo = st.file_uploader(
    "Envie sua planilha",
    type=["xlsx", "xls", "csv"]
)


if arquivo is not None:
    try:
        df_original = ler_arquivo(arquivo)
        df = limpar_dados(df_original)

        st.session_state["dados"] = df
        st.session_state["nome_arquivo"] = arquivo.name

        resumo = resumo_dados(df)

        st.success("Arquivo carregado com sucesso!")

        st.subheader("Resumo da planilha")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Linhas", resumo["total_linhas"])

        with col2:
            st.metric("Colunas", resumo["total_colunas"])

        with col3:
            st.metric("Colunas numéricas", len(resumo["colunas_numericas"]))

        st.divider()

        st.subheader("Colunas encontradas")

        st.write(resumo["colunas"])

        st.divider()

        st.subheader("Prévia dos dados")

        st.dataframe(df.head(50), use_container_width=True)

        st.divider()

        st.subheader("Informações automáticas")

        colunas_numericas = resumo["colunas_numericas"]
        colunas_texto = resumo["colunas_texto"]

        if colunas_numericas:
            st.write("**Colunas numéricas identificadas:**")
            st.write(colunas_numericas)
        else:
            st.warning("Nenhuma coluna numérica foi identificada.")

        if colunas_texto:
            st.write("**Colunas de texto identificadas:**")
            st.write(colunas_texto)

        st.info(
            "Próximo passo: usar esses dados para gerar gráficos automáticos na página de Análises."
        )

    except Exception as erro:
        st.error("Não foi possível ler o arquivo.")
        st.write(f"Detalhe do erro: {erro}")

else:
    st.info("Envie um arquivo Excel ou CSV para começar.")
