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


def tratar_nenhuma(valor):
    """
    Converte opção Nenhuma em None.
    """

    if valor == "Nenhuma":
        return None

    return valor


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


def criar_opcoes_colunas(df):
    """
    Cria lista de opções para selectbox.
    """

    return ["Nenhuma"] + df.columns.tolist()


def encontrar_indice_opcao(opcoes, valor):
    """
    Encontra índice de uma opção.
    """

    if valor in opcoes:
        return opcoes.index(valor)

    return 0


def detectar_coluna_percentual(df):
    """
    Detecta coluna percentual.
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

    for coluna in df.columns:
        nome = str(coluna).lower()

        if any(palavra in nome for palavra in palavras_percentual):
            if coluna in colunas_numericas:
                return coluna

    for coluna in colunas_numericas:
        serie = df[coluna].dropna()

        if len(serie) == 0:
            continue

        menor = serie.min()
        maior = serie.max()
        soma = serie.sum()

        if menor >= 0 and maior <= 1.05 and 0.80 <= soma <= 1.20:
            return coluna

        if menor >= 0 and maior <= 100 and 80 <= soma <= 120:
            return coluna

    return None


def detectar_coluna_data(df):
    """
    Detecta coluna de data.
    """

    colunas_data = df.select_dtypes(
        include=["datetime", "datetimetz"]
    ).columns.tolist()

    if len(colunas_data) > 0:
        return colunas_data[0]

    palavras_data = [
        "data",
        "date",
        "dia",
        "mes",
        "mês",
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


def detectar_coluna_categoria(df):
    """
    Detecta a melhor coluna de categoria.
    """

    # Primeiro procura colunas de texto
    colunas_texto = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    if len(colunas_texto) == 0:
        # Se não encontrar texto, usa a primeira coluna não numérica possível
        if len(df.columns) > 0:
            return df.columns[0]
        return None

    melhor_coluna = None
    melhor_pontuacao = -999

    total_linhas = max(len(df), 1)

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
        "departamento",
        "nome",
        "descricao",
        "descrição"
    ]

    for coluna in colunas_texto:
        serie = df[coluna].dropna().astype(str).str.strip()

        if len(serie) == 0:
            continue

        valores_unicos = serie.nunique()
        taxa_unicidade = valores_unicos / total_linhas
        tamanho_medio = serie.str.len().mean()
        nome = str(coluna).lower()

        pontuacao = 0

        if any(palavra in nome for palavra in palavras_categoria):
            pontuacao += 6

        if valores_unicos >= 2:
            pontuacao += 3

        if taxa_unicidade <= 0.95:
            pontuacao += 2

        if taxa_unicidade <= 0.70:
            pontuacao += 1

        if tamanho_medio <= 50:
            pontuacao += 1

        if tamanho_medio > 100:
            pontuacao -= 3

        if pontuacao > melhor_pontuacao:
            melhor_pontuacao = pontuacao
            melhor_coluna = coluna

    if melhor_coluna is None and len(colunas_texto) > 0:
        melhor_coluna = colunas_texto[0]

    return melhor_coluna


def detectar_coluna_valor(df, coluna_percentual=None):
    """
    Detecta a principal coluna numérica.
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
        "volume",
        "realizado",
        "resultado"
    ]

    melhor_coluna = None
    melhor_pontuacao = -999

    for coluna in colunas_numericas:
        if coluna == coluna_percentual:
            continue

        serie = df[coluna].dropna()

        if len(serie) == 0:
            continue

        nome = str(coluna).lower()
        pontuacao = 0

        if any(palavra in nome for palavra in palavras_valor):
            pontuacao += 6

        soma_abs = serie.abs().sum()
        media_abs = serie.abs().mean()
        maior_abs = serie.abs().max()

        if soma_abs > 0:
            pontuacao += 2

        if media_abs > 1:
            pontuacao += 1

        if maior_abs > 100:
            pontuacao += 3

        # Penaliza colunas que parecem percentual
        if serie.min() >= 0 and serie.max() <= 1.05:
            pontuacao -= 5

        if serie.min() >= 0 and serie.max() <= 100:
            pontuacao -= 1

        if pontuacao > melhor_pontuacao:
            melhor_pontuacao = pontuacao
            melhor_coluna = coluna

    if melhor_coluna is None:
        for coluna in colunas_numericas:
            if coluna != coluna_percentual:
                return coluna

        return colunas_numericas[0]

    return melhor_coluna


def detectar_configuracao_automatica(df):
    """
    Detecta automaticamente as colunas principais.
    """

    coluna_percentual = detectar_coluna_percentual(df)
    coluna_categoria = detectar_coluna_categoria(df)
    coluna_valor = detectar_coluna_valor(
        df,
        coluna_percentual=coluna_percentual
    )
    coluna_data = detectar_coluna_data(df)

    return {
        "coluna_categoria": coluna_categoria,
        "coluna_valor": coluna_valor,
        "coluna_percentual": coluna_percentual,
        "coluna_data": coluna_data,
        "modo": "automatico"
    }


def aplicar_configuracao_automatica(df, sobrescrever=True):
    """
    Aplica e salva configuração automática.
    """

    inicializar_configuracao_colunas()

    config_atual = obter_configuracao_colunas()

    if not sobrescrever:
        if (
            config_atual.get("coluna_categoria") is not None
            and config_atual.get("coluna_valor") is not None
        ):
            return config_atual

    nova_config = detectar_configuracao_automatica(df)

    st.session_state.configuracao_colunas = nova_config

    return nova_config
