import streamlit as st

from components.style import carregar_css

from components.data_store import (
    inicializar_estado_dados,
    salvar_dados_upload,
    obter_dados,
    limpar_dados
)

from components.column_config import (
    inicializar_configuracao_colunas,
    obter_configuracao_colunas,
    salvar_configuracao_colunas,
    criar_opcoes_colunas,
    encontrar_indice_opcao,
    aplicar_configuracao_automatica
)


st.set_page_config(
    page_title="Fontes de Dados | Insight AI",
    page_icon="📁",
    layout="wide"
)


carregar_css()
inicializar_estado_dados()
inicializar_configuracao_colunas()


st.title("📁 Fontes de Dados")

st.caption("Carregamento, leitura e identificação automática de planilhas.")

st.write(
    """
    Envie uma planilha Excel ou CSV. O Insight AI tentará identificar automaticamente
    as principais colunas para gerar análises e insights.
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

        aplicar_configuracao_automatica(df, sobrescrever=True)

        st.success("Arquivo carregado com sucesso!")
        st.info("As colunas principais foram identificadas automaticamente.")

    except Exception as erro:
        st.error("Não foi possível ler o arquivo.")
        st.warning(str(erro))


if st.session_state.dados_carregados:
    df = obter_dados()

    st.subheader("Resumo do arquivo")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Linhas", df.shape[0])

    with col2:
        st.metric("Colunas", df.shape[1])

    with col3:
        st.metric("Arquivo", st.session_state.nome_arquivo)

    st.divider()

    st.subheader("Prévia dos dados")

    st.dataframe(df.head(20), use_container_width=True)

    st.divider()

    st.subheader("Identificação automática das colunas")

    config = obter_configuracao_colunas()

    col_auto1, col_auto2, col_auto3, col_auto4 = st.columns(4)

    with col_auto1:
        st.metric(
            "Categoria",
            config.get("coluna_categoria") or "Não detectada"
        )

    with col_auto2:
        st.metric(
            "Valor principal",
            config.get("coluna_valor") or "Não detectado"
        )

    with col_auto3:
        st.metric(
            "Percentual",
            config.get("coluna_percentual") or "Não detectado"
        )

    with col_auto4:
        st.metric(
            "Data",
            config.get("coluna_data") or "Não detectada"
        )

    st.caption(
        "O sistema usa essa identificação para montar gráficos, rankings e insights automaticamente."
    )

    with st.expander("Ajustar colunas manualmente, se necessário"):
        st.write(
            """
            Use esta opção apenas se o Insight AI identificar alguma coluna incorretamente.
            """
        )

        opcoes = criar_opcoes_colunas(df)

        col_config1, col_config2 = st.columns(2)

        with col_config1:
            coluna_categoria = st.selectbox(
                "Coluna de categoria",
                opcoes,
                index=encontrar_indice_opcao(
                    opcoes,
                    config.get("coluna_categoria")
                ),
                help="Exemplo: produto, cliente, filial, região, vendedor ou área."
            )

            coluna_percentual = st.selectbox(
                "Coluna de percentual",
                opcoes,
                index=encontrar_indice_opcao(
                    opcoes,
                    config.get("coluna_percentual")
                ),
                help="Exemplo: participação, margem percentual ou crescimento percentual."
            )

        with col_config2:
            coluna_valor = st.selectbox(
                "Coluna de valor principal",
                opcoes,
                index=encontrar_indice_opcao(
                    opcoes,
                    config.get("coluna_valor")
                ),
                help="Exemplo: faturamento, receita, quantidade, custo ou margem."
            )

            coluna_data = st.selectbox(
                "Coluna de data",
                opcoes,
                index=encontrar_indice_opcao(
                    opcoes,
                    config.get("coluna_data")
                ),
                help="Exemplo: data, mês, ano ou período."
            )

        if st.button("Salvar ajuste manual"):
            salvar_configuracao_colunas(
                coluna_categoria=coluna_categoria,
                coluna_valor=coluna_valor,
                coluna_percentual=coluna_percentual,
                coluna_data=coluna_data,
                modo="manual"
            )

            st.success("Ajuste manual salvo com sucesso.")
            st.rerun()

    st.divider()

    st.subheader("Informações das colunas")

    resumo_colunas = []

    for coluna in df.columns:
        resumo_colunas.append(
            {
                "Coluna": coluna,
                "Tipo": str(df[coluna].dtype),
                "Valores vazios": int(df[coluna].isna().sum()),
                "Valores únicos": int(df[coluna].nunique())
            }
        )

    st.dataframe(resumo_colunas, use_container_width=True)

    st.divider()

    if st.button("Limpar dados carregados"):
        limpar_dados()
        st.success("Dados removidos da sessão.")
        st.rerun()

else:
    st.warning("Nenhuma planilha foi carregada ainda.")
