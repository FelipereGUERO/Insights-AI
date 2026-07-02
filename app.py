import streamlit as st
import plotly.express as px

from components.style import carregar_css

from components.data_store import (
    inicializar_estado_dados,
    obter_dados
)

from components.column_config import (
    inicializar_configuracao_colunas,
    obter_configuracao_colunas,
    aplicar_configuracao_automatica
)

from components.insight_engine import (
    executar_insight_engine,
    formatar_numero,
    formatar_percentual
)


st.set_page_config(
    page_title="Insight AI | Central de Insights",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


carregar_css()
inicializar_estado_dados()
inicializar_configuracao_colunas()


def identificar_colunas(df):
    """
    Identifica colunas de texto e numéricas.
    """

    colunas_texto = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    colunas_numericas = df.select_dtypes(
        include="number"
    ).columns.tolist()

    return colunas_texto, colunas_numericas


def garantir_configuracao_valida(df):
    """
    Garante que categoria e valor existem e são válidos.
    """

    config = obter_configuracao_colunas()

    coluna_categoria = config.get("coluna_categoria")
    coluna_valor = config.get("coluna_valor")

    precisa_recalcular = False

    if coluna_categoria is None or coluna_valor is None:
        precisa_recalcular = True

    elif coluna_categoria not in df.columns or coluna_valor not in df.columns:
        precisa_recalcular = True

    elif coluna_valor not in df.select_dtypes(include="number").columns.tolist():
        precisa_recalcular = True

    if precisa_recalcular:
        config = aplicar_configuracao_automatica(df, sobrescrever=True)

    return config


def exibir_insight(insight):
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


def exibir_estado_sem_dados():
    """
    Tela sem planilha carregada.
    """

    st.title("🧠 Insight AI")

    st.caption("Transformando dados em decisões inteligentes.")

    st.divider()

    st.header("Central de Insights")

    st.write(
        """
        Bem-vindo ao **Insight AI**.

        Esta é a tela principal do sistema. Aqui o usuário verá primeiro os principais
        achados da análise, antes mesmo de olhar gráficos ou tabelas.
        """
    )

    st.info(
        """
        Para começar, vá até a página **Dados** e envie uma planilha Excel ou CSV.
        Depois volte para esta tela para visualizar o resumo executivo automático.
        """
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Status", "Aguardando dados")

    with col2:
        st.metric("Upload", "Pendente")

    with col3:
        st.metric("Insight Engine", "Pronto")

    st.divider()

    st.subheader("Como funciona")

    passo1, passo2, passo3 = st.columns(3)

    with passo1:
        st.markdown(
            """
            ### 1. Envie os dados
            Faça upload de uma planilha Excel ou CSV na página **Dados**.
            """
        )

    with passo2:
        st.markdown(
            """
            ### 2. O sistema analisa
            O Data Engine identifica colunas, valores, categorias e padrões.
            """
        )

    with passo3:
        st.markdown(
            """
            ### 3. Receba insights
            A Central de Insights mostra alertas, recomendações e resumo executivo.
            """
        )


def exibir_central_com_dados(df):
    """
    Tela principal com planilha carregada.
    """

    st.title("🧠 Central de Insights")

    st.caption("Resumo executivo automático da análise carregada.")

    st.divider()

    if df is None or df.empty:
        st.warning("A planilha carregada está vazia.")
        st.info("Vá até a página Dados e envie uma nova planilha.")
        return

    config = garantir_configuracao_valida(df)

    coluna_categoria = config.get("coluna_categoria")
    coluna_valor = config.get("coluna_valor")

    colunas_texto, colunas_numericas = identificar_colunas(df)

    st.success(f"Arquivo atual: {st.session_state.nome_arquivo}")

    col_base1, col_base2, col_base3, col_base4 = st.columns(4)

    with col_base1:
        st.metric("Linhas", df.shape[0])

    with col_base2:
        st.metric("Colunas", df.shape[1])

    with col_base3:
        st.metric("Colunas numéricas", len(colunas_numericas))

    with col_base4:
        st.metric("Modo", config.get("modo", "automatico").capitalize())

    st.divider()

    if coluna_categoria is None or coluna_valor is None:
        st.warning("Ainda não foi possível identificar automaticamente as colunas principais.")
        st.info("Vá até a página Dados e ajuste as colunas manualmente, se necessário.")

        with st.expander("Diagnóstico da planilha"):
            st.write("Colunas encontradas:")
            st.write(df.columns.tolist())

            st.write("Tipos das colunas:")
            st.write(df.dtypes.astype(str).to_dict())

        return

    resultado = executar_insight_engine(
        df,
        coluna_categoria,
        coluna_valor
    )

    if resultado is None:
        st.warning("Não foi possível gerar insights com a planilha atual.")
        st.info(
            """
            A planilha precisa ter pelo menos uma coluna de categoria e uma coluna numérica.
            Tente limpar os dados carregados e enviar a planilha novamente.
            """
        )

        with st.expander("Diagnóstico da análise"):
            st.write(f"Coluna de categoria detectada: {coluna_categoria}")
            st.write(f"Coluna de valor detectada: {coluna_valor}")

            st.write("Colunas disponíveis:")
            st.write(df.columns.tolist())

            st.write("Tipos das colunas:")
            st.write(df.dtypes.astype(str).to_dict())

            st.write("Prévia dos dados:")
            st.dataframe(df.head(20), use_container_width=True)

        return

    df_agrupado = resultado["df_agrupado"]
    metricas = resultado["metricas"]
    insights = resultado["insights"]
    recomendacoes = resultado["recomendacoes"]

    st.subheader("Resumo executivo")

    resumo = (
        f"Foram analisadas **{metricas['quantidade_categorias']} categorias**, "
        f"com total de **{formatar_numero(metricas['total'])}** em **{coluna_valor}**. "
        f"A principal categoria é **{metricas['maior_categoria']}**, com "
        f"**{formatar_numero(metricas['maior_valor'])}**, representando "
        f"**{formatar_percentual(metricas['maior_participacao'])}** do total. "
        f"As três maiores categorias concentram "
        f"**{formatar_percentual(metricas['participacao_top_3'])}** do resultado."
    )

    st.info(resumo)

    st.divider()

    st.subheader("Indicadores principais")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total analisado",
            formatar_numero(metricas["total"])
        )

    with col2:
        st.metric(
            "Categoria líder",
            str(metricas["maior_categoria"]),
            formatar_numero(metricas["maior_valor"])
        )

    with col3:
        st.metric(
            "Concentração Top 3",
            formatar_percentual(metricas["participacao_top_3"])
        )

    with col4:
        st.metric(
            "Categorias",
            metricas["quantidade_categorias"]
        )

    st.divider()

    col_esq, col_dir = st.columns([1.2, 1])

    with col_esq:
        st.subheader("Principais categorias")

        top_n = min(10, len(df_agrupado))

        df_top = df_agrupado.head(top_n).sort_values(
            by=coluna_valor,
            ascending=True
        )

        fig = px.bar(
            df_top,
            x=coluna_valor,
            y=coluna_categoria,
            orientation="h",
            color="Classe ABC",
            text=coluna_valor,
            title=f"Top {top_n} por {coluna_valor}",
            color_discrete_map={
                "A": "#2563EB",
                "B": "#F97316",
                "C": "#94A3B8"
            }
        )

        fig.update_traces(
            texttemplate="%{text:,.2f}",
            textposition="outside"
        )

        fig.update_layout(
            height=500,
            xaxis_title=coluna_valor,
            yaxis_title=coluna_categoria,
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_dir:
        st.subheader("Mapa de participação")

        df_pizza = df_agrupado.head(min(8, len(df_agrupado)))

        fig_pizza = px.pie(
            df_pizza,
            names=coluna_categoria,
            values=coluna_valor,
            title="Participação dos principais grupos"
        )

        fig_pizza.update_layout(
            height=500,
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF"
        )

        st.plotly_chart(fig_pizza, use_container_width=True)

    st.divider()

    st.subheader("Alertas e descobertas")

    if len(insights) == 0:
        st.success("Nenhum alerta relevante encontrado nesta análise.")
    else:
        for insight in insights:
            exibir_insight(insight)

    st.divider()

    st.subheader("Recomendações automáticas")

    for i, recomendacao in enumerate(recomendacoes, start=1):
        st.write(f"**{i}.** {recomendacao}")

    st.divider()

    with st.expander("Ver configuração usada nesta análise"):
        st.write(f"**Coluna de categoria:** {coluna_categoria}")
        st.write(f"**Coluna de valor principal:** {coluna_valor}")
        st.write(f"**Coluna percentual:** {config.get('coluna_percentual')}")
        st.write(f"**Coluna de data:** {config.get('coluna_data')}")

    with st.expander("Prévia dos dados analisados"):
        st.dataframe(df.head(30), use_container_width=True)


if not st.session_state.dados_carregados:
    exibir_estado_sem_dados()
else:
    df = obter_dados()
    exibir_central_com_dados(df)
