import streamlit as st
import pandas as pd


def inicializar_configuracao_colunas():
    """
    Inicializa a configuração das colunas no session_state.
    """

    if "configuracao_colunas" not in st.session_state:
        st.session_state.configuracao_colunas = {
            "coluna_categoria": None,
            "coluna_valor": None,
            "coluna_percentual": None,
            "coluna_data": None,
            "modo": "automatico"
        }


def obter_configuracao_colunas():
    """
    Retorna a configuração atual das colunas.
    """

    inicializar_configuracao_colunas()
    return st.session_state.configuracao_colunas


def salvar_configuracao_colunas(
    coluna_categoria=None,
    coluna_valor=None,
    coluna_percentual=None,
    coluna_data=None,
    modo="manual"
):
    """
    Salva a configuração das colunas.
    """

    st.session_state.configuracao_colunas = {
        "coluna_categoria": tratar_nenhuma(coluna_categoria),
        "coluna_valor": tratar_nenhuma(coluna_valor),
        "coluna_percentual": tratar_nenhuma(coluna_percentual),
        "coluna_data": tratar_nenhuma(coluna_data),
        "modo": modo
    }


def tratar_nenhuma(valor):
    """
    Converte a opção 'Nenhuma' em None.
    """

    if valor == "Nenhuma":
        return None

    return valor


def criar_opcoes_colunas(df):
    """
    Cria lista de opções para selectbox, incluindo Nenhuma.
    """

    return ["Nenhuma"] + df.columns.tolist()


def encontrar_indice_opcao(opcoes, valor):
    """
    Encontra o índice de uma opção dentro da lista.
    """

    if valor in opcoes:
        return opcoes.index(valor)

    return 0


def detectar_coluna_data(df):
    """
    Detecta automaticamente uma coluna de data.
    """

    colunas_datetime = df.select_dtypes(
        include=["datetime", "datetimetz"]
    ).columns.tolist()

    if len(colunas_datetime) > 0:
        return colunas_datetime[0]

    palavras_data = [
        "data",
        "date",
        "dia",
        "mês",
        "mes",
        "month",
        "ano",
        "year",
        "periodo",
        "período"
    ]

    for coluna in df.columns:
        nome = str(coluna).lower()

        if any(palavra in nome for palavra in palavras_data):
            return coluna

    return None


def detectar_coluna_percentual(df):
    """
    Detecta automaticamente uma coluna percentual.
    """

    colunas_numericas = df.select_dtypes(include="number").columns.tolist()

    palavras_percentual = [
        "%",
        "percentual",
        "participacao",
        "participação",
        "share",
        "perc",
        "representatividade"
    ]

    # Primeiro tenta pelo nome da coluna
    for coluna in df.columns:
        nome = str(coluna).lower()

        if any(palavra in nome for palavra in palavras_percentual):
            if coluna in colunas_numericas:
                return coluna

    # Depois tenta pelo comportamento dos dados
    for coluna in colunas_numericas:
        serie = df[coluna].dropna()

        if len(serie) == 0:
            continue

        menor = serie.min()
        maior = serie.max()
        soma = serie.sum()

        # Percentual em formato decimal: 0.10, 0.25, 1.00
        if menor >= 0 and maior <= 1.05 and 0.80 <= soma <= 1.20:
            return coluna

        # Percentual em formato 0 a 100
        if menor >= 0 and maior <= 100 and 80 <= soma <= 120:
            return coluna

    return None


def detectar_coluna_categoria(df):
    """
    Detecta automaticamente a melhor coluna de categoria.
    """

    colunas_texto = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    if len(colunas_texto) == 0:
        return None

    melhor_coluna = None
    melhor_pontuacao = -1

    total_linhas = len(df)

    for coluna in colunas_texto:
        serie = df[coluna].dropna().astype(str).str.strip()

        if len(serie) == 0:
            continue

        valores_unicos = serie.nunique()
        taxa_unicidade = valores_unicos / max(total_linhas, 1)

        nome = str(coluna).lower()

        pontuacao = 0

        # Nomes comuns de categoria
        palavras_categoria = [
            "produto",
            "cliente",
            "categoria",
            "filial",
            "unidade",
            "empresa",
            "regiao",
            "região",
            "vendedor",
            "area",
            "área",
            "linha",
            "grupo",
            "departamento"
        ]

        if any(palavra in nome for palavra in palavras_categoria):
            pontuacao += 5

        # Boa coluna categórica tem alguns valores únicos,
        # mas não deve ser texto totalmente livre.
        if valores_unicos >= 2:
            pontuacao += 2

        if taxa_unicidade <= 0.90:
            pontuacao += 2

        if taxa_unicidade <= 0.50:
            pontuacao += 1

        # Evita escolher colunas com textos muito longos
        tamanho_medio = serie.str.len().mean()

        if tamanho_medio <= 40:
            pontuacao += 1

        if pontuacao > melhor_pontuacao:
            melhor_pontuacao = pontuacao
            melhor_coluna = coluna

    return melhor_coluna


def detectar_coluna_valor(df, coluna_percentual=None):
    """
    Detecta automaticamente a principal coluna numérica de valor.
    """

    colunas_numericas = df.select_dtypes(include="number").columns.tolist()

    if len(colunas_numericas) == 0:
        return None

    palavras_valor = [
        "valor",
        "faturamento",
        "receita",
        "venda",
        "vendas",
        "total",
        "custo",
        "lucro",
        "margem",
        "quantidade",
        "qtd",
        "volume"
    ]

    melhor_coluna = None
    melhor_pontuacao = -1

    for coluna in colunas_numericas:
        if coluna == coluna_percentual:
            continue

        serie = df[coluna].dropna()

        if len(serie) == 0:
            continue

        nome = str(coluna).lower()

        pontuacao = 0

        if any(palavra in nome for palavra in palavras_valor):
            pontuacao += 5

        soma_abs = serie.abs().sum()
        media_abs = serie.abs().mean()
        maior_abs = serie.abs().max()

        # Colunas de valor geralmente têm soma e magnitude maiores
        if soma_abs > 0:
            pontuacao += 2

        if media_abs > 1:
            pontuacao += 1

        if maior_abs > 100:
            pontuacao += 2

        # Evita coluna que parece percentual
        if serie.min() >= 0 and serie.max() <= 1.05:
            pontuacao -= 3

        if serie.min() >= 0 and serie.max() <= 100:
            pontuacao -= 1

        if pontuacao > melhor_pontuacao:
            melhor_pontuacao = pontuacao
            melhor_coluna = coluna

    # Se todas foram rejeitadas por serem percentuais, pega a primeira numérica
    if melhor_coluna is None:
        for coluna in colunas_numericas:
            if coluna != coluna_percentual:
                return coluna

    return melhor_coluna


def detectar_configuracao_automatica(df):
    """
    Detecta automaticamente a configuração principal da planilha.
    """

    coluna_data = detectar_coluna_data(df)
    coluna_percentual = detectar_coluna_percentual(df)
    coluna_categoria = detectar_coluna_categoria(df)
    coluna_valor = detectar_coluna_valor(
        df,
        coluna_percentual=coluna_percentual
    )

    configuracao = {
        "coluna_categoria": coluna_categoria,
        "coluna_valor": coluna_valor,
        "coluna_percentual": coluna_percentual,
        "coluna_data": coluna_data,
        "modo": "automatico"
    }

    return configuracao


def aplicar_configuracao_automatica(df, sobrescrever=True):
    """
    Detecta e salva automaticamente a configuração das colunas.
    """

    inicializar_configuracao_colunas()

    config_atual = obter_configuracao_colunas()

    if not sobrescrever and config_atual.get("coluna_categoria") is not None:
        return config_atual

    nova_config = detectar_configuracao_automatica(df)

    st.session_state.configuracao_colunas = nova_config

    return nova_config
