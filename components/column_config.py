import streamlit as st
import pandas as pd


def inicializar_configuracao_colunas():
    """
    Inicializa configuração das colunas.
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
    Retorna configuração atual.
    """

    inicializar_configuracao_colunas()
    return st.session_state.configuracao_colunas


def tratar_nenhuma(valor):
    """
    Converte 'Nenhuma' em None.
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
    Salva configuração escolhida pelo usuário.
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
    Cria lista para selectbox.
    """

    return ["Nenhuma"] + df.columns.tolist()


def encontrar_indice_opcao(opcoes, valor):
    """
    Retorna índice seguro de uma opção.
    """

    if valor in opcoes:
        return opcoes.index(valor)

    return 0


def detectar_coluna_data(df):
    """
    Detecta coluna de data.
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
        "período",
        "periodo"
    ]

    for coluna in df.columns:
        nome = str(coluna).lower()

        if any(palavra in nome for palavra in palavras_data):
            return coluna

    return None


def detectar_coluna_percentual(df):
    """
    Detecta coluna percentual.
    """

    colunas_numericas = df.select_dtypes(include="number").columns.tolist()

    if len(colunas_numericas) == 0:
        return None

    palavras_percentual = [
        "%",
        "percentual",
        "participacao",
        "participação",
        "share",
        "perc",
        "representatividade"
    ]

    # Primeiro tenta pelo nome
    for coluna in colunas_numericas:
        nome = str(coluna).lower()

        if any(palavra in nome for palavra in palavras_percentual):
            return coluna

    # Depois tenta pelo comportamento dos dados
    for coluna in colunas_numericas:
        serie = df[coluna].dropna()

        if len(serie) == 0:
            continue

        menor = serie.min()
        maior = serie.max()
        soma = serie.sum()

        # Percentual decimal: 0 a 1, soma perto de 1
        if menor >= 0 and maior <= 1.05 and 0.70 <= soma <= 1.30:
            return coluna

        # Percentual 0 a 100, soma perto de 100
        if menor >= 0 and maior <= 100 and 70 <= soma <= 130:
            return coluna

    return None


def detectar_coluna_categoria(df):
    """
    Detecta melhor coluna de categoria.
    """

    colunas_texto = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    if len(colunas_texto) == 0:
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
        "área",
        "area",
        "linha",
        "grupo",
        "departamento",
        "divisão",
        "divisao",
        "nome",
        "descrição",
        "descricao"
    ]

    for coluna in colunas_texto:
        serie = df[coluna].dropna().astype(str).str.strip()

        if len(serie) == 0:
            continue

        nome = str(coluna).lower()
        valores_unicos = serie.nunique()
        taxa_unicidade = valores_unicos / total_linhas
        tamanho_medio = serie.str.len().mean()

        pontuacao = 0

        if any(palavra in nome for palavra in palavras_categoria):
            pontuacao += 5

        if valores_unicos >= 2:
            pontuacao += 3

        if taxa_unicidade <= 0.95:
            pontuacao += 2

        if taxa_unicidade <= 0.70:
            pontuacao += 1

        if tamanho_medio <= 60:
            pontuacao += 1

        # Evita colunas que parecem vazias ou genéricas demais
        if valores_unicos <= 1:
            pontuacao -= 5

        if pontuacao > melhor_pontuacao:
            melhor_pontuacao = pontuacao
            melhor_coluna = coluna

    return melhor_coluna


def detectar_coluna_valor(df, coluna_percentual=None):
    """
    Detecta coluna numérica principal.
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
        "saldo",
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
        max_abs = serie.abs().max()
        valores_unicos = serie.nunique()

        if soma_abs > 0:
            pontuacao += 2

        if media_abs > 1:
            pontuacao += 1

        if max_abs > 100:
            pontuacao += 3

        if valores_unicos >= 2:
            pontuacao += 1

        # Penaliza coluna com cara de percentual
        if serie.min() >= 0 and serie.max() <= 1.05:
            pontuacao -= 4

        if serie.min() >= 0 and serie.max() <= 100:
            pontuacao -= 1

        if pontuacao > melhor_pontuacao:
            melhor_pontuacao = pontuacao
            melhor_coluna = coluna

    if melhor_coluna is None:
        for coluna in colunas_numericas:
            if coluna != coluna_percentual:
                return coluna

    return melhor_coluna


def detectar_configuracao_automatica(df):
    """
    Detecta automaticamente categoria, valor, percentual e data.
    """

    coluna_data = detectar_coluna_data(df)
    coluna_percentual = detectar_coluna_percentual(df)
    coluna_categoria = detectar_coluna_categoria(df)
    coluna_valor = detectar_coluna_valor(
        df,
        coluna_percentual=coluna_percentual
    )

    return {
        "coluna_categoria": coluna_categoria,
        "coluna_valor": coluna_valor,
        "coluna_percentual": coluna_percentual,
        "coluna_data": coluna_data,
        "modo": "automatico"
    }


def configuracao_valida(df, config):
    """
    Verifica se a configuração atual ainda existe na planilha.
    """

    if config is None:
        return False

    coluna_categoria = config.get("coluna_categoria")
    coluna_valor = config.get("coluna_valor")

    if coluna_categoria is None or coluna_valor is None:
        return False

    if coluna_categoria not in df.columns or coluna_valor not in df.columns:
        return False

    if not pd.api.types.is_numeric_dtype(df[coluna_valor]):
        return False

    return True


def aplicar_configuracao_automatica(df, sobrescrever=True):
    """
    Detecta e salva a configuração automática.
    """

    inicializar_configuracao_colunas()

    config_atual = obter_configuracao_colunas()

    if not sobrescrever and configuracao_valida(df, config_atual):
        return config_atual

    nova_config = detectar_configuracao_automatica(df)

    st.session_state.configuracao_colunas = nova_config

    return nova_config
