import streamlit as st

from components.data_store import (
    inicializar_estado_dados,
    salvar_dados_upload,
    obter_dados,
    limpar_dados
)


st.set_page_config(
    page_title="Fontes de Dados | Insight AI",
    page_icon="📁",
    layout="wide"
)


inicializar_estado_dados()


st.title("📁 Fontes de Dados")

st.write(
    """
    Nesta área você pode enviar uma planilha Excel ou CSV para o Insight AI analisar.
    """
)

st.divider()


arquivo = st.file_uploader(
    "Envie sua planilha",
    type=["xlsx", "xls", "csv"]
)


if arquivo is not None:
    try:
        df = salvar_dados_upload(arquivo)

        st.success("Arquivo carregado com sucesso!")

        st.info(f"Arquivo atual: {st.session_state.nome_arquivo}")
        st.info(f"Upload realizado em: {st.session_state.data_upload}")

        st.subheader("Prévia dos dados")
        st.dataframe(df.head(20), use_container_width=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Linhas", df.shape[0])

        with col2:
            st.metric("Colunas", df.shape[1])

        with col3:
            st.metric("Arquivo", st.session_state.nome_arquivo)

    except Exception as erro:
        st.error("Não foi possível ler o arquivo.")
        st.warning(str(erro))


elif st.session_state.dados_carregados:
    df = obter_dados()

    st.success("Já existe uma planilha carregada nesta sessão.")

    st.info(f"Arquivo atual: {st.session_state.nome_arquivo}")
    st.info(f"Upload realizado em: {st.session_state.data_upload}")

    st.subheader("Prévia dos dados")
    st.dataframe(df.head(20), use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Linhas", df.shape[0])

    with col2:
        st.metric("Colunas", df.shape[1])

    with col3:
        st.metric("Arquivo", st.session_state.nome_arquivo)


else:
    st.warning("Nenhuma planilha foi carregada ainda.")


st.divider()


if st.session_state.dados_carregados:
    if st.button("Limpar dados carregados"):
        limpar_dados()
        st.success("Dados removidos da sessão.")
        st.rerun()
