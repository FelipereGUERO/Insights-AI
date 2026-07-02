import pandas as pd
import numpy as np


def formatar_numero(valor):
    """
    Formata número no padrão brasileiro.
    """

    try:
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(valor)


def formatar_percentual(valor):
    """
    Formata percentual.
    """

    try:
        return f"{valor:.2f}%".replace(".", ",")
    except Exception:
        return str(valor)


def remover_linhas_totais(df, coluna_categoria):
    """
    Remove linhas de totalização.
    """

    if coluna_categoria is None or coluna_categoria not in df.columns:
        return df

    termos_total = [
        "total",
        "total geral",
        "grand total",
        "subtotal",
        "soma",
        "geral"
    ]

    df_temp = df.copy()

    texto = (
        df_temp[coluna_categoria]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    mascara_total = texto.isin(termos_total)

    return df_temp[~mascara_total]


def classificar_abc(participacao_acumulada):
    """
    Classificação ABC:
    A até 80%, B até 95%, C acima de 95%.
    """

    if participacao_acumulada <= 80:
        return "A"

    if participacao_acumulada <= 95:
        return "B"

    return "C"


def preparar_base_analise(df, coluna_categoria, coluna_valor):
    """
    Prepara base agregada da análise.
    """

    if df is None or df.empty:
        return None

    if coluna_categoria is None or coluna_valor is None:
        return None

    if coluna_categoria not in df.columns or coluna_valor not in df.columns:
        return None

    if not pd.api.types.is_numeric_dtype(df[coluna_valor]):
        return None

    df_temp = remover_linhas_totais(df, coluna_categoria)

    df_temp = df_temp[[coluna_categoria, coluna_valor]].copy()

    df_temp = df_temp.dropna(subset=[coluna_categoria, coluna_valor])

    if df_temp.empty:
        return None

    df_temp[coluna_categoria] = df_temp[coluna_categoria].astype(str).str.strip()

    df_temp = df_temp[df_temp[coluna_categoria] != ""]

    if df_temp.empty:
        return None

    df_agrupado = (
        df_temp
        .groupby(coluna_categoria, as_index=False)[coluna_valor]
        .sum()
        .sort_values(by=coluna_valor, ascending=False)
        .reset_index(drop=True)
    )

    if df_agrupado.empty:
        return None

    total = df_agrupado[coluna_valor].sum()

    if total == 0:
        df_agrupado["Participação %"] = 0
        df_agrupado["Participação acumulada %"] = 0
    else:
        df_agrupado["Participação %"] = (
            df_agrupado[coluna_valor] / total * 100
        )

        df_agrupado["Participação acumulada %"] = (
            df_agrupado["Participação %"].cumsum()
        )

    df_agrupado["Classe ABC"] = df_agrupado["Participação acumulada %"].apply(
        classificar_abc
    )

    df_agrupado["Ranking"] = range(1, len(df_agrupado) + 1)

    return df_agrupado


def calcular_outliers(df_agrupado, coluna_valor):
    """
    Calcula outliers usando IQR.
    """

    resultado_vazio = {
        "outliers_superiores": pd.DataFrame(),
        "outliers_inferiores": pd.DataFrame(),
        "limite_superior": None,
        "limite_inferior": None
    }

    if df_agrupado is None or df_agrupado.empty:
        return resultado_vazio

    valores = df_agrupado[coluna_valor].dropna()

    if len(valores) < 4:
        return resultado_vazio

    q1 = valores.quantile(0.25)
    q3 = valores.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        return resultado_vazio

    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    outliers_superiores = df_agrupado[
        df_agrupado[coluna_valor] > limite_superior
    ]

    outliers_inferiores = df_agrupado[
        df_agrupado[coluna_valor] < limite_inferior
    ]

    return {
        "outliers_superiores": outliers_superiores,
        "outliers_inferiores": outliers_inferiores,
        "limite_superior": limite_superior,
        "limite_inferior": limite_inferior
    }


def calcular_metricas_avancadas(df_agrupado, coluna_categoria, coluna_valor):
    """
    Calcula métricas principais.
    """

    if df_agrupado is None or df_agrupado.empty:
        return None

    total = df_agrupado[coluna_valor].sum()
    quantidade_categorias = df_agrupado[coluna_categoria].nunique()

    maior_linha = df_agrupado.iloc[0]
    menor_linha = df_agrupado.iloc[-1]

    maior_categoria = maior_linha[coluna_categoria]
    maior_valor = maior_linha[coluna_valor]
    maior_participacao = maior_linha["Participação %"]

    menor_categoria = menor_linha[coluna_categoria]
    menor_valor = menor_linha[coluna_valor]
    menor_participacao = menor_linha["Participação %"]

    top_3 = df_agrupado.head(3)
    top_5 = df_agrupado.head(5)

    participacao_top_3 = top_3["Participação %"].sum()
    participacao_top_5 = top_5["Participação %"].sum()

    media = df_agrupado[coluna_valor].mean()
    mediana = df_agrupado[coluna_valor].median()

    if len(df_agrupado) >= 2:
        segunda_linha = df_agrupado.iloc[1]
        segunda_categoria = segunda_linha[coluna_categoria]
        segunda_valor = segunda_linha[coluna_valor]

        diferenca_lider_segundo = maior_valor - segunda_valor

        if segunda_valor != 0:
            lider_vs_segundo_percentual = (
                diferenca_lider_segundo / segunda_valor * 100
            )
        else:
            lider_vs_segundo_percentual = 0
    else:
        segunda_categoria = None
        segunda_valor = 0
        diferenca_lider_segundo = 0
        lider_vs_segundo_percentual = 0

    classes_abc = (
        df_agrupado
        .groupby("Classe ABC")
        .agg(
            Quantidade=(coluna_categoria, "count"),
            Valor=(coluna_valor, "sum"),
            Participacao=("Participação %", "sum")
        )
        .reset_index()
    )

    outliers = calcular_outliers(df_agrupado, coluna_valor)

    return {
        "total": total,
        "quantidade_categorias": quantidade_categorias,
        "maior_categoria": maior_categoria,
        "maior_valor": maior_valor,
        "maior_participacao": maior_participacao,
        "menor_categoria": menor_categoria,
        "menor_valor": menor_valor,
        "menor_participacao": menor_participacao,
        "participacao_top_3": participacao_top_3,
        "participacao_top_5": participacao_top_5,
        "media": media,
        "mediana": mediana,
        "segunda_categoria": segunda_categoria,
        "segunda_valor": segunda_valor,
        "diferenca_lider_segundo": diferenca_lider_segundo,
        "lider_vs_segundo_percentual": lider_vs_segundo_percentual,
        "classes_abc": classes_abc,
        "outliers": outliers
    }


def avaliar_concentracao(participacao_top_3):
    """
    Avalia concentração.
    """

    if participacao_top_3 >= 80:
        return "Alta"

    if participacao_top_3 >= 60:
        return "Média"

    return "Baixa"


def gerar_insights_avancados(df_agrupado, metricas, coluna_categoria, coluna_valor):
    """
    Gera insights automáticos.
    """

    if metricas is None:
        return []

    insights = []

    concentracao = avaliar_concentracao(metricas["participacao_top_3"])

    insights.append(
        {
            "tipo": "Resumo",
            "nivel": "info",
            "titulo": "Resumo executivo",
            "texto": (
                f"Foram analisadas {metricas['quantidade_categorias']} categorias, "
                f"com total de {formatar_numero(metricas['total'])} em {coluna_valor}."
            )
        }
    )

    insights.append(
        {
            "tipo": "Liderança",
            "nivel": "success",
            "titulo": "Principal categoria",
            "texto": (
                f"A categoria líder é {metricas['maior_categoria']}, com "
                f"{formatar_numero(metricas['maior_valor'])}, representando "
                f"{formatar_percentual(metricas['maior_participacao'])} do total."
            )
        }
    )

    if metricas["segunda_categoria"] is not None:
        insights.append(
            {
                "tipo": "Comparação",
                "nivel": "info",
                "titulo": "Comparativo entre 1º e 2º colocado",
                "texto": (
                    f"A categoria {metricas['maior_categoria']} está "
                    f"{formatar_percentual(metricas['lider_vs_segundo_percentual'])} "
                    f"acima da segunda colocada, {metricas['segunda_categoria']}."
                )
            }
        )

    if concentracao == "Alta":
        nivel = "warning"
        texto = (
            f"As 3 maiores categorias concentram "
            f"{formatar_percentual(metricas['participacao_top_3'])} do total. "
            f"Isso indica alta dependência de poucos grupos."
        )
    elif concentracao == "Média":
        nivel = "info"
        texto = (
            f"As 3 maiores categorias concentram "
            f"{formatar_percentual(metricas['participacao_top_3'])} do total. "
            f"A concentração é moderada e deve ser acompanhada."
        )
    else:
        nivel = "success"
        texto = (
            f"As 3 maiores categorias concentram "
            f"{formatar_percentual(metricas['participacao_top_3'])} do total. "
            f"O resultado está relativamente distribuído."
        )

    insights.append(
        {
            "tipo": "Concentração",
            "nivel": nivel,
            "titulo": f"Concentração {concentracao}",
            "texto": texto
        }
    )

    classes_abc = metricas["classes_abc"]

    classe_a = classes_abc[classes_abc["Classe ABC"] == "A"]

    if not classe_a.empty:
        qtd_a = int(classe_a.iloc[0]["Quantidade"])
        part_a = classe_a.iloc[0]["Participacao"]

        insights.append(
            {
                "tipo": "Curva ABC",
                "nivel": "info",
                "titulo": "Curva ABC",
                "texto": (
                    f"A Classe A possui {qtd_a} categoria(s), que juntas representam "
                    f"{formatar_percentual(part_a)} do total. "
                    f"Essas categorias devem receber prioridade gerencial."
                )
            }
        )

    outliers_superiores = metricas["outliers"]["outliers_superiores"]

    if not outliers_superiores.empty:
        lista = ", ".join(
            outliers_superiores[coluna_categoria].astype(str).head(3).tolist()
        )

        insights.append(
            {
                "tipo": "Outlier",
                "nivel": "warning",
                "titulo": "Valores fora do padrão",
                "texto": (
                    f"Foram identificadas categorias com valores muito acima do padrão: "
                    f"{lista}."
                )
            }
        )

    if metricas["menor_participacao"] < 1:
        insights.append(
            {
                "tipo": "Baixa participação",
                "nivel": "warning",
                "titulo": "Categoria com baixa representatividade",
                "texto": (
                    f"A categoria {metricas['menor_categoria']} possui apenas "
                    f"{formatar_percentual(metricas['menor_participacao'])} "
                    f"de participação."
                )
            }
        )

    return insights


def gerar_recomendacoes(metricas):
    """
    Gera recomendações automáticas.
    """

    if metricas is None:
        return []

    recomendacoes = []

    concentracao = avaliar_concentracao(metricas["participacao_top_3"])

    if concentracao == "Alta":
        recomendacoes.append(
            "Investigar a dependência das principais categorias e avaliar formas de diversificar o resultado."
        )

        recomendacoes.append(
            "Acompanhar de perto as categorias líderes, pois qualquer queda nelas pode impactar fortemente o total."
        )

    if metricas["maior_participacao"] >= 40:
        recomendacoes.append(
            f"Analisar em profundidade a categoria {metricas['maior_categoria']}, pois ela representa uma parcela muito relevante do total."
        )

    if metricas["menor_participacao"] < 1:
        recomendacoes.append(
            f"Avaliar a categoria {metricas['menor_categoria']} para entender se há oportunidade de crescimento ou baixa performance."
        )

    if not metricas["outliers"]["outliers_superiores"].empty:
        recomendacoes.append(
            "Validar valores muito acima do padrão para confirmar se representam oportunidade, sazonalidade ou distorção nos dados."
        )

    if len(recomendacoes) == 0:
        recomendacoes.append(
            "Manter acompanhamento periódico dos principais indicadores e comparar os resultados com períodos anteriores."
        )

    return recomendacoes


def executar_insight_engine(df, coluna_categoria, coluna_valor):
    """
    Executa o motor de insights completo.
    """

    df_agrupado = preparar_base_analise(
        df,
        coluna_categoria,
        coluna_valor
    )

    if df_agrupado is None or df_agrupado.empty:
        return None

    metricas = calcular_metricas_avancadas(
        df_agrupado,
        coluna_categoria,
        coluna_valor
    )

    if metricas is None:
        return None

    insights = gerar_insights_avancados(
        df_agrupado,
        metricas,
        coluna_categoria,
        coluna_valor
    )

    recomendacoes = gerar_recomendacoes(metricas)

    return {
        "df_agrupado": df_agrupado,
        "metricas": metricas,
        "insights": insights,
        "recomendacoes": recomendacoes
    }
