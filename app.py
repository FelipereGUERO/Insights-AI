import streamlit as st
import plotly.express as px
from datetime import datetime

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


inicializar_estado_dados()
inicializar_configuracao_colunas()


def saudacao():
    hora = datetime.now().hour

    if hora < 12:
        return "Bom dia"
    elif hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"


def exibir_tela_sem_dados():
    st.title("🧠 Insight AI")

    st.subheader("Central de Insights")

    st.write(
        """
        Envie uma planilha Excel ou CSV para que o Insight AI analise os dados,
        identifique padrões e gere recomendações automáticas.
        """
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(
            """
            **1. Envie os dados**  
            Faça upload de uma planilha na página **Dados**.
            """
        )

    with col2:
        st.info(
            """
            **2. O sistema analisa**  
            O Insight AI identifica colunas, rankings, concentração, curva ABC e outliers.
            """
        )

    with col3:
        st.info(
            """
            **3. Receba insights**  
            Veja resumo executivo, alertas e recomendações automáticas.
            """
        )

    st.divider()

    st.warning("Nenhuma planilha foi carregada ainda.")

    st.write("Para começar, acesse a página **Dados** no menu lateral e envie uma planilha.")

    st.divider()

    st.subheader("O que o Insight AI já consegue analisar")

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        st.metric("Ranking", "Ativo")

    with col_b:
        st.metric("Curva ABC", "Ativo")

    with col_c:
        st.metric("Pareto", "Ativo")

    with col_d:
        st.metric("Outliers", "Ativo")


def exibir_card_insight(insight):
    texto = f"**{insight['titulo']}**  \n{insight['texto']}"

    if insight["nivel"] == "success":
        st.success(texto)
    elif insight["nivel"] == "warning":
        st.warning(texto)
    elif insight["nivel"] == "error":
        st.error(texto)
    else:
        st.info(texto)


def gerar_texto_resumo_executivo(metricas, coluna_valor):
    texto = (
        f"{saudacao()}! O Insight AI analisou os dados carregados e encontrou "
        f"**{metricas['quantidade_categorias']} categorias** com total de "
        f"**{formatar_numero(metricas['total'])}** em **{coluna_valor}**. "
        f"A principal categoria é **{metricas['maior_categoria']}**, com participação de "
        f"**{formatar_percentual(metricas['maior_participacao'])}**. "
        f"As três maiores categorias concentram "
        f"**{formatar_percentual(metricas['participacao_top_3'])}** do resultado."
    )

    return texto


def classificar_nivel_atencao(metricas):
    pontos = 0

    if metricas["participacao_top_3"] >= 80:
        pontos += 2
    elif metricas["participacao_top_3"] >= 60:
        pontos += 1

    if metricas["maior_participacao"] >= 40:
        pontos += 2
    elif metricas["maior_participacao"] >= 25:
        pontos += 1

    if metricas["menor_participacao"] < 1:
        pontos += 1

    if not metricas["outliers"]["outliers_superiores"].empty:
        pontos += 1

    if pontos >= 5:
        return "Alto", "🔴"
    elif pontos >= 3:
        return "Médio", "🟠"
    else:
        return "Baixo", "🟢"


def calcular_insight_score(metricas):
    score = 100

    if metricas["participacao_top_3"] >= 80:
        score -= 20
    elif metricas["participacao_top_3"] >= 60:
        score -= 10

    if metricas["maior_participacao"] >= 50:
        score -= 20
    elif metricas["maior_participacao"] >= 40:
        score -= 10

    if metricas["menor_participacao"] < 1:
        score -= 5

    if not metricas["outliers"]["outliers_superiores"].empty:
        score -= 10

    if score < 0:
        score = 0

    return score


st.title("🧠 Central de Insights")

st.write(
    """
    Esta é a página principal do Insight AI. Aqui você vê primeiro os achados mais importantes,
    antes de entrar nos gráficos e dados detalhados.
    """
)

st.divider()


if not st.session_state.dados_carregados:
    exibir_tela_sem_dados()

else:
    df = obter_dados()

    config = obter_configuracao_colunas()

    if config.get("coluna_categoria") is None or config.get("coluna_valor") is None:
        config = aplicar_configuracao_automatica(df, sobrescrever=True)

    coluna_categoria = config.get("coluna_categoria")
    coluna_valor = config.get("coluna_valor")

    if coluna_categoria is None or coluna_valor is None:
        st.warning("Não foi possível identificar automaticamente as colunas principais.")
        st.info("Acesse a página Dados e ajuste as colunas manualmente, se necessário.")

    else:
        resultado = executar_insight_engine(
            df,
            coluna_categoria,
            coluna_valor
        )

        if resultado is None:
            st.warning("Não foi possível gerar insights com a planilha carregada.")

        else:
            df_agrupado = resultado["df_agrupado"]
            metricas = resultado["metricas"]
            insights = resultado["insights"]
            recomendacoes = resultado["recomendacoes"]

            nivel_atencao, icone_atencao = classificar_nivel_atencao(metricas)
            insight_score = calcular_insight_score(metricas)

            st.success(f"Arquivo analisado: {st.session_state.nome_arquivo}")

            st.subheader("Resumo executivo")

            st.info(
                gerar_texto_resumo_executivo(
                    metricas,
                    coluna_valor
                )
            )

            st.divider()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Insight Score™",
                    f"{insight_score}/100"
                )

            with col2:
                st.metric(
                    "Nível de atenção",
                    f"{icone_atencao} {nivel_atencao}"
                )

            with col3:
                st.metric(
                    "Total analisado",
                    formatar_numero(metricas["total"])
                )

            with col4:
                st.metric(
                    "Top 3",
                    formatar_percentual(metricas["participacao_top_3"])
                )

            st.divider()

            col_esq, col_dir = st.columns([1.2, 1])

            with col_esq:
                st.subheader("Principais achados")

                for insight in insights[:4]:
                    exibir_card_insight(insight)

            with col_dir:
                st.subheader("Ranking rápido")

                df_top = df_agrupado.head(5).sort_values(
                    by=coluna_valor,
                    ascending=True
                )

                fig = px.bar(
                    df_top,
                    x=coluna_valor,
                    y=coluna_categoria,
                    orientation="h",
                    text=coluna_valor,
                    color="Classe ABC",
                    title="Top 5 categorias",
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
                    height=420,
                    xaxis_title=coluna_valor,
                    yaxis_title=coluna_categoria
                )

                st.plotly_chart(fig, use_container_width=True)

            st.divider()

            st.subheader("Recomendações prioritárias")

            for i, recomendacao in enumerate(recomendacoes[:5], start=1):
                st.write(f"**{i}.** {recomendacao}")

            st.divider()

            st.subheader("Resumo da classificação ABC")

            classes_abc = metricas["classes_abc"].copy()
            classes_abc["Participacao"] = classes_abc["Participacao"].round(2)

            col_abc1, col_abc2 = st.columns([1, 1])

            with col_abc1:
                st.dataframe(
                    classes_abc,
                    use_container_width=True
                )

            with col_abc2:
                fig_abc = px.bar(
                    classes_abc,
                    x="Classe ABC",
                    y="Participacao",
                    text="Participacao",
                    color="Classe ABC",
                    title="Participação por classe ABC",
                    color_discrete_map={
                        "A": "#2563EB",
                        "B": "#F97316",
                        "C": "#94A3B8"
                    }
                )

                fig_abc.update_traces(
                    texttemplate="%{text:.2f}%",
                    textposition="outside"
                )

                fig_abc.update_layout(
                    height=350,
                    yaxis_title="Participação %",
                    xaxis_title="Classe"
                )

                st.plotly_chart(fig_abc, use_container_width=True)

            st.divider()

            st.subheader("Próximos passos")

            col_p1, col_p2, col_p3 = st.columns(3)

            with col_p1:
                st.info(
                    """
                    **Ver análise completa**  
                    Acesse a página **Análises** para ver Pareto, outliers e ranking detalhado.
                    """
                )

            with col_p2:
                st.info(
                    """
                    **Trocar planilha**  
                    Acesse a página **Dados** para enviar outro arquivo.
                    """
                )

            with col_p3:
                st.info(
                    """
                    **Próxima evolução**  
                    Em breve: análise temporal, tendências e agente de IA.
                    """
                )
