import streamlit as st
import pandas as pd
import plotly.express as px

from components.data_store import inicializar_estado_dados, obter_dados
from components.column_config import (
    inicializar_configuracao_colunas,
    obter_configuracao_colunas,
    aplicar_configuracao_automatica,
    encontrar_indice_opcao
)


st.set_page_config(
    page_title="Análises | Insight AI",
    page_icon="📊",
    layout="wide"
)


inicializar_estado_dados()
inicializar_configuracao_colunas()


def formatar_numero(valor):
    """
    Formata números no padrão brasileiro.
    """

    try:
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor


def remover_linhas_totais(df, coluna_categoria):
    """
    Remove linhas como Total Geral, Total, Grand Total e Subtotal.
    """

    if coluna_categoria is None:
        return df

    termos_total = [
        "total",
        "total geral",
        "grand total",
        "subtotal"
    ]

    df_temp = df.copy()

    coluna_texto = df_temp[coluna_categoria].astype(str).str.strip().str.lower()

    mascara_total = coluna_texto.isin(termos_total)

    return df_temp[~mascara_total]


def identificar_colunas(df):
    """
    Separa colunas numéricas e colunas de texto.
    """

    colunas_numericas = df.select_dtypes(include="number").columns.tolist()

    colunas_texto = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    return colunas_texto, colunas_numericas


def gerar_resumo_automatico(df, coluna_categoria, coluna_valor):
    """
    Gera indicadores básicos da análise.
    """

    if coluna_categoria is None or coluna_valor is None:
        return None

    df_analise = remover_linhas_totais(df, coluna_categoria)

    df_analise = df_analise[[coluna_categoria, coluna_valor]].dropna()

    if df_analise.empty:
        return None

    df_agrupado = (
        df_analise
        .groupby(coluna_categoria, as_index=False)[coluna_valor]
        .sum()
        .sort_values(by=coluna_valor, ascending=False)
    )

    total = df_agrupado[coluna_valor].sum()

    if df_agrupado.empty:
        return None

    maior_linha = df_agrupado.iloc[0]
    menor_linha = df_agrupado.iloc[-1]

    maior_categoria = maior_linha[coluna_categoria]
    maior_valor = maior_linha[coluna_valor]

    menor_categoria = menor_linha[coluna_categoria]
    menor_valor = menor_linha[coluna_valor]

    participacao_maior = 0

    if total != 0:
        participacao_maior = maior_valor / total * 100

    resumo = {
        "df_agrupado": df_agrupado,
        "total": total,
        "maior_categoria": maior_categoria,
        "maior_valor": maior_valor,
        "menor_categoria": menor_categoria,
        "menor_valor": menor_valor,
        "participacao_maior": participacao_maior,
        "quantidade_categorias": df_agrupado[coluna_categoria].nunique()
    }

    return resumo


st.title("📊 Análises")

st.write(
    """
    O Insight AI analisa automaticamente a planilha carregada e gera indicadores,
    gráficos e rankings com base nas colunas identificadas.
    """
)

st.divider()


if not st.session_state.dados_carregados:
    st.warning("Nenhuma planilha foi carregada ainda.")
    st.info("Vá até a página Dados e envie um arquivo Excel ou CSV.")

else:
    df = obter_dados()

    config = obter_configuracao_colunas()

    if config.get("coluna_categoria") is None or config.get("coluna_valor") is None:
        config = aplicar_configuracao_automatica(df, sobrescrever=True)

    st.success(f"Arquivo em análise: {st.session_state.nome_arquivo}")

    st.subheader("Resumo da base de dados")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Linhas", df.shape[0])

    with col2:
        st.metric("Colunas", df.shape[1])

    with col3:
        st.metric(
            "Campos numéricos",
            len(df.select_dtypes(include="number").columns)
        )

    with col4:
        st.metric(
            "Modo",
            config.get("modo", "automatico").capitalize()
        )

    st.divider()

    st.subheader("Colunas usadas na análise")

    col_auto1, col_auto2, col_auto3 = st.columns(3)

    with col_auto1:
        st.info(f"Categoria: **{config.get('coluna_categoria') or 'Não detectada'}**")

    with col_auto2:
        st.info(f"Valor principal: **{config.get('coluna_valor') or 'Não detectado'}**")

    with col_auto3:
        st.info(f"Percentual: **{config.get('coluna_percentual') or 'Não detectado'}**")

    st.divider()

    colunas_texto, colunas_numericas = identificar_colunas(df)

    coluna_categoria_auto = config.get("coluna_categoria")
    coluna_valor_auto = config.get("coluna_valor")

    if len(colunas_texto) == 0:
        st.warning("Não encontrei colunas de texto para usar como categoria.")

    elif len(colunas_numericas) == 0:
        st.warning("Não encontrei colunas numéricas para gerar gráficos.")

    elif coluna_categoria_auto is None or coluna_valor_auto is None:
        st.warning("Não foi possível identificar automaticamente as colunas principais.")
        st.info("Vá até a página Dados e ajuste as colunas manualmente, se necessário.")

    else:
        with st.expander("Alterar colunas desta análise"):
            col_config1, col_config2 = st.columns(2)

            with col_config1:
                coluna_categoria = st.selectbox(
                    "Escolha a coluna de categoria:",
                    colunas_texto,
                    index=encontrar_indice_opcao(
                        colunas_texto,
                        coluna_categoria_auto
                    )
                )

            with col_config2:
                coluna_valor = st.selectbox(
                    "Escolha a coluna de valor:",
                    colunas_numericas,
                    index=encontrar_indice_opcao(
                        colunas_numericas,
                        coluna_valor_auto
                    )
                )

        # Fora do expander, usa automaticamente as colunas detectadas/selecionadas
        if "coluna_categoria" not in locals():
            coluna_categoria = coluna_categoria_auto

        if "coluna_valor" not in locals():
            coluna_valor = coluna_valor_auto

        resumo = gerar_resumo_automatico(
            df,
            coluna_categoria,
            coluna_valor
        )

        if resumo is None:
            st.warning("Não foi possível gerar análise com as colunas identificadas.")

        else:
            df_agrupado = resumo["df_agrupado"]

            st.subheader("Indicadores principais")

            col_ind1, col_ind2, col_ind3, col_ind4 = st.columns(4)

            with col_ind1:
                st.metric(
                    "Total",
                    formatar_numero(resumo["total"])
                )

            with col_ind2:
                st.metric(
                    "Maior categoria",
                    str(resumo["maior_categoria"]),
                    formatar_numero(resumo["maior_valor"])
                )

            with col_ind3:
                st.metric(
                    "Participação da maior",
                    f"{resumo['participacao_maior']:.2f}%"
                )

            with col_ind4:
                st.metric(
                    "Categorias",
                    resumo["quantidade_categorias"]
                )

            st.divider()

            st.subheader("Gráfico automático")

            tipo_grafico = st.radio(
                "Tipo de visualização:",
                [
                    "Barras horizontais",
                    "Barras - ranking",
                    "Pizza - participação"
                ],
                horizontal=True
            )

            top_n = st.slider(
                "Quantidade de categorias no gráfico:",
                min_value=3,
                max_value=min(30, len(df_agrupado)),
                value=min(10, len(df_agrupado))
            )

            df_top = df_agrupado.head(top_n)

            if tipo_grafico == "Barras horizontais":
                df_top_horizontal = df_top.sort_values(
                    by=coluna_valor,
                    ascending=True
                )

                fig = px.bar(
                    df_top_horizontal,
                    x=coluna_valor,
                    y=coluna_categoria,
                    orientation="h",
                    text=coluna_valor,
                    title=f"Ranking de {coluna_categoria} por {coluna_valor}"
                )

                fig.update_traces(
                    texttemplate="%{text:,.2f}",
                    textposition="outside"
                )

                fig.update_layout(
                    xaxis_title=coluna_valor,
                    yaxis_title=coluna_categoria,
                    height=550
                )

            elif tipo_grafico == "Barras - ranking":
                fig = px.bar(
                    df_top,
                    x=coluna_categoria,
                    y=coluna_valor,
                    text=coluna_valor,
                    title=f"Ranking de {coluna_categoria} por {coluna_valor}"
                )

                fig.update_traces(
                    texttemplate="%{text:,.2f}",
                    textposition="outside"
                )

                fig.update_layout(
                    xaxis_title=coluna_categoria,
                    yaxis_title=coluna_valor,
                    height=550
                )

            else:
                fig = px.pie(
                    df_top,
                    names=coluna_categoria,
                    values=coluna_valor,
                    title=f"Participação por {coluna_categoria}"
                )

                fig.update_layout(
                    height=550
                )

            st.plotly_chart(fig, use_container_width=True)

            st.divider()

            st.subheader("Ranking detalhado")

            df_ranking = df_agrupado.copy()

            if resumo["total"] != 0:
                df_ranking["Participação %"] = (
                    df_ranking[coluna_valor] / resumo["total"] * 100
                )
            else:
                df_ranking["Participação %"] = 0

            df_ranking["Participação %"] = df_ranking["Participação %"].round(2)

            st.dataframe(
                df_ranking,
                use_container_width=True
            )

            st.divider()

            st.subheader("Insights automáticos")

            st.success(
                f"A maior categoria é **{resumo['maior_categoria']}**, "
                f"com **{formatar_numero(resumo['maior_valor'])}**."
            )

            st.info(
                f"A categoria **{resumo['maior_categoria']}** representa "
                f"**{resumo['participacao_maior']:.2f}%** do total analisado."
            )

            st.warning(
                f"A menor categoria é **{resumo['menor_categoria']}**, "
                f"com **{formatar_numero(resumo['menor_valor'])}**."
            )

    st.divider()

    st.subheader("Prévia dos dados")

    st.dataframe(df.head(20), use_container_width=True)
