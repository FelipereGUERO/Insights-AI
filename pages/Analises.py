import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.data_store import inicializar_estado_dados, obter_dados

from components.column_config import (
    inicializar_configuracao_colunas,
    obter_configuracao_colunas,
    aplicar_configuracao_automatica,
    encontrar_indice_opcao
)

from components.insight_engine import (
    executar_insight_engine,
    formatar_numero,
    formatar_percentual
)


st.set_page_config(
    page_title="Análises | Insight AI",
    page_icon="📊",
    layout="wide"
)


inicializar_estado_dados()
inicializar_configuracao_colunas()


def identificar_colunas(df):
    """
    Separa colunas numéricas e colunas de texto.
    """

    colunas_numericas = df.select_dtypes(include="number").columns.tolist()

    colunas_texto = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    return colunas_texto, colunas_numericas


def exibir_card_insight(insight):
    """
    Exibe insight com visual conforme o nível.
    """

    texto = f"**{insight['titulo']}**  \n{insight['texto']}"

    if insight["nivel"] == "success":
        st.success(texto)
    elif insight["nivel"] == "warning":
        st.warning(texto)
    elif insight["nivel"] == "error":
        st.error(texto)
    else:
        st.info(texto)


def criar_grafico_pareto(df_agrupado, coluna_categoria, coluna_valor):
    """
    Cria gráfico de Pareto com barras e linha acumulada.
    """

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_agrupado[coluna_categoria],
            y=df_agrupado[coluna_valor],
            name=coluna_valor,
            marker_color="#2563EB"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_agrupado[coluna_categoria],
            y=df_agrupado["Participação acumulada %"],
            name="Participação acumulada %",
            yaxis="y2",
            mode="lines+markers",
            marker_color="#F97316"
        )
    )

    fig.add_hline(
        y=80,
        line_dash="dash",
        line_color="red",
        annotation_text="80%",
        annotation_position="top left",
        yref="y2"
    )

    fig.update_layout(
        title="Curva de Pareto",
        xaxis_title=coluna_categoria,
        yaxis=dict(
            title=coluna_valor
        ),
        yaxis2=dict(
            title="Participação acumulada %",
            overlaying="y",
            side="right",
            range=[0, 105]
        ),
        height=550,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


st.title("📊 Análises Avançadas")

st.write(
    """
    O Insight AI analisa automaticamente a planilha carregada, identifica padrões,
    calcula indicadores e gera insights executivos.
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

    colunas_texto, colunas_numericas = identificar_colunas(df)

    coluna_categoria_auto = config.get("coluna_categoria")
    coluna_valor_auto = config.get("coluna_valor")

    st.success(f"Arquivo em análise: {st.session_state.nome_arquivo}")

    col_base1, col_base2, col_base3, col_base4 = st.columns(4)

    with col_base1:
        st.metric("Linhas", df.shape[0])

    with col_base2:
        st.metric("Colunas", df.shape[1])

    with col_base3:
        st.metric("Campos numéricos", len(colunas_numericas))

    with col_base4:
        st.metric("Modo", config.get("modo", "automatico").capitalize())

    st.divider()

    if len(colunas_texto) == 0:
        st.warning("Não encontrei colunas de texto para usar como categoria.")

    elif len(colunas_numericas) == 0:
        st.warning("Não encontrei colunas numéricas para gerar análise.")

    elif coluna_categoria_auto is None or coluna_valor_auto is None:
        st.warning("Não foi possível identificar automaticamente as colunas principais.")
        st.info("Vá até a página Dados e ajuste as colunas manualmente, se necessário.")

    else:
        with st.expander("Colunas usadas na análise"):
            col_config1, col_config2, col_config3 = st.columns(3)

            with col_config1:
                coluna_categoria = st.selectbox(
                    "Categoria",
                    colunas_texto,
                    index=encontrar_indice_opcao(
                        colunas_texto,
                        coluna_categoria_auto
                    )
                )

            with col_config2:
                coluna_valor = st.selectbox(
                    "Valor principal",
                    colunas_numericas,
                    index=encontrar_indice_opcao(
                        colunas_numericas,
                        coluna_valor_auto
                    )
                )

            with col_config3:
                st.write("Configuração automática")
                st.info(
                    f"""
                    Categoria: **{coluna_categoria_auto}**  
                    Valor: **{coluna_valor_auto}**
                    """
                )

        resultado = executar_insight_engine(
            df,
            coluna_categoria,
            coluna_valor
        )

        if resultado is None:
            st.warning("Não foi possível gerar análise com as colunas identificadas.")

        else:
            df_agrupado = resultado["df_agrupado"]
            metricas = resultado["metricas"]
            insights = resultado["insights"]
            recomendacoes = resultado["recomendacoes"]

            st.subheader("Resumo executivo")

            resumo_texto = (
                f"Foram analisadas **{metricas['quantidade_categorias']} categorias**, "
                f"com total de **{formatar_numero(metricas['total'])}** em **{coluna_valor}**. "
                f"A principal categoria é **{metricas['maior_categoria']}**, representando "
                f"**{formatar_percentual(metricas['maior_participacao'])}** do total. "
                f"As três maiores categorias concentram "
                f"**{formatar_percentual(metricas['participacao_top_3'])}** do resultado."
            )

            st.info(resumo_texto)

            col_ind1, col_ind2, col_ind3, col_ind4 = st.columns(4)

            with col_ind1:
                st.metric(
                    "Total analisado",
                    formatar_numero(metricas["total"])
                )

            with col_ind2:
                st.metric(
                    "Maior categoria",
                    str(metricas["maior_categoria"]),
                    formatar_numero(metricas["maior_valor"])
                )

            with col_ind3:
                st.metric(
                    "Top 3",
                    formatar_percentual(metricas["participacao_top_3"])
                )

            with col_ind4:
                st.metric(
                    "Categorias",
                    metricas["quantidade_categorias"]
                )

            st.divider()

            aba1, aba2, aba3, aba4, aba5 = st.tabs(
                [
                    "Visão Geral",
                    "Curva ABC / Pareto",
                    "Outliers",
                    "Insights",
                    "Dados"
                ]
            )

            with aba1:
                st.subheader("Ranking principal")

                quantidade_categorias = len(df_agrupado)

                if quantidade_categorias <= 3:
                    top_n = quantidade_categorias
                else:
                    top_n = st.slider(
                        "Quantidade de categorias no gráfico:",
                        min_value=3,
                        max_value=min(30, quantidade_categorias),
                        value=min(10, quantidade_categorias)
                    )

                df_top = df_agrupado.head(top_n)

                df_top_horizontal = df_top.sort_values(
                    by=coluna_valor,
                    ascending=True
                )

                fig_barra = px.bar(
                    df_top_horizontal,
                    x=coluna_valor,
                    y=coluna_categoria,
                    orientation="h",
                    text=coluna_valor,
                    color="Classe ABC",
                    title=f"Ranking de {coluna_categoria} por {coluna_valor}",
                    color_discrete_map={
                        "A": "#2563EB",
                        "B": "#F97316",
                        "C": "#94A3B8"
                    }
                )

                fig_barra.update_traces(
                    texttemplate="%{text:,.2f}",
                    textposition="outside"
                )

                fig_barra.update_layout(
                    height=550,
                    xaxis_title=coluna_valor,
                    yaxis_title=coluna_categoria
                )

                st.plotly_chart(fig_barra, use_container_width=True)

                col_g1, col_g2 = st.columns(2)

                with col_g1:
                    fig_pizza = px.pie(
                        df_top,
                        names=coluna_categoria,
                        values=coluna_valor,
                        title="Participação das principais categorias"
                    )

                    fig_pizza.update_layout(height=450)

                    st.plotly_chart(fig_pizza, use_container_width=True)

                with col_g2:
                    fig_treemap = px.treemap(
                        df_top,
                        path=[coluna_categoria],
                        values=coluna_valor,
                        color="Participação %",
                        title="Mapa de contribuição",
                        color_continuous_scale="Blues"
                    )

                    fig_treemap.update_layout(height=450)

                    st.plotly_chart(fig_treemap, use_container_width=True)

            with aba2:
                st.subheader("Curva ABC e Pareto")

                fig_pareto = criar_grafico_pareto(
                    df_agrupado,
                    coluna_categoria,
                    coluna_valor
                )

                st.plotly_chart(fig_pareto, use_container_width=True)

                st.subheader("Resumo por classe ABC")

                classes_abc = metricas["classes_abc"].copy()

                classes_abc["Participacao"] = classes_abc["Participacao"].round(2)

                st.dataframe(
                    classes_abc,
                    use_container_width=True
                )

                st.info(
                    """
                    A Curva ABC ajuda a identificar quais categorias merecem maior atenção.
                    Normalmente, itens Classe A concentram a maior parte do resultado e devem ser priorizados.
                    """
                )

            with aba3:
                st.subheader("Análise de outliers")

                outliers_superiores = metricas["outliers"]["outliers_superiores"]
                outliers_inferiores = metricas["outliers"]["outliers_inferiores"]

                fig_box = px.box(
                    df_agrupado,
                    y=coluna_valor,
                    points="all",
                    title=f"Distribuição e possíveis outliers de {coluna_valor}"
                )

                fig_box.update_layout(height=500)

                st.plotly_chart(fig_box, use_container_width=True)

                col_out1, col_out2 = st.columns(2)

                with col_out1:
                    st.write("Categorias muito acima do padrão")

                    if outliers_superiores.empty:
                        st.success("Nenhum outlier superior relevante identificado.")
                    else:
                        st.warning("Foram encontrados valores muito acima do padrão.")
                        st.dataframe(outliers_superiores, use_container_width=True)

                with col_out2:
                    st.write("Categorias muito abaixo do padrão")

                    if outliers_inferiores.empty:
                        st.success("Nenhum outlier inferior relevante identificado.")
                    else:
                        st.warning("Foram encontrados valores muito abaixo do padrão.")
                        st.dataframe(outliers_inferiores, use_container_width=True)

            with aba4:
                st.subheader("Insights automáticos")

                for insight in insights:
                    exibir_card_insight(insight)

                st.divider()

                st.subheader("Recomendações automáticas")

                for i, recomendacao in enumerate(recomendacoes, start=1):
                    st.write(f"**{i}.** {recomendacao}")

            with aba5:
                st.subheader("Ranking detalhado")

                df_exibicao = df_agrupado.copy()

                df_exibicao["Participação %"] = df_exibicao["Participação %"].round(2)
                df_exibicao["Participação acumulada %"] = (
                    df_exibicao["Participação acumulada %"].round(2)
                )

                colunas_ordenadas = [
                    "Ranking",
                    coluna_categoria,
                    coluna_valor,
                    "Participação %",
                    "Participação acumulada %",
                    "Classe ABC"
                ]

                st.dataframe(
                    df_exibicao[colunas_ordenadas],
                    use_container_width=True
                )

                st.divider()

                st.subheader("Prévia da base original")

                st.dataframe(
                    df.head(30),
                    use_container_width=True
                )
