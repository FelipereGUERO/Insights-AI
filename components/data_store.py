import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime


def inicializar_estado_dados():
    """
    Inicializa as variáveis de sessão usadas para armazenar a planilha carregada.
    """

    if "dados_carregados" not in st.session_state:
        st.session_state.dados_carregados = False

    if "df_dados" not in st.session_state:
        st.session_state.df_dados = None

    if "nome_arquivo" not in st.session_state:
        st.session_state.nome_arquivo = None

    if "data_upload" not in st.session_state:
        st.session_state.data_upload = None


def normalizar_texto_numero(valor):
    """
    Converte valores em texto com aparência numérica para formato numérico.
    Exemplos:
    R$ 1.250,50 -> 1250.50
    1.250,50 -> 1250.50
    44,7% -> 44.7
    1140095.66 -> 1140095.66
    """

    if pd.isna(valor):
        return np.nan

    texto = str(valor).strip()

    if texto == "" or texto.lower() in ["nan", "none", "null"]:
        return np.nan

    texto = texto.replace("R$", "")
    texto = texto.replace("%", "")
    texto = texto.replace(" ", "")
    texto = texto.replace("\xa0", "")

    if texto.startswith("(") and texto.endswith(")"):
        texto = "-" + texto[1:-1]

    # Caso brasileiro: 1.250,50
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "")
            texto = texto.replace(",", ".")
        else:
            texto = texto.replace(",", "")

    # Caso brasileiro simples: 1250,50
    elif "," in texto:
        texto = texto.replace(".", "")
        texto = texto.replace(",", ".")

    return texto


def tentar_converter_coluna_para_numero(serie):
    """
    Tenta converter uma coluna para número.
    Só converte se a maior parte dos valores parecer numérica.
    """

    if pd.api.types.is_numeric_dtype(serie):
        return serie

    serie_original = serie.copy()

    valores_normalizados = serie.apply(normalizar_texto_numero)

    valores_convertidos = pd.to_numeric(
        valores_normalizados,
        errors="coerce"
    )

    total_validos = serie_original.notna().sum()

    if total_validos == 0:
        return serie_original

    total_convertidos = valores_convertidos.notna().sum()
    taxa_conversao = total_convertidos / total_validos

    # Se pelo menos 70% da coluna parece número, converte
    if taxa_conversao >= 0.7:
        return valores_convertidos

    return serie_original.astype(str)


def padronizar_dataframe(df):
    """
    Padroniza a base carregada:
    - remove linhas/colunas vazias;
    - ajusta nomes de colunas;
    - converte números em texto para número;
    - mantém categorias como texto.
    """

    df = df.copy()

    # Remove linhas e colunas totalmente vazias
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")

    # Se a planilha veio totalmente vazia
    if df.empty:
        return df

    # Padroniza nomes de colunas
    novas_colunas = []

    for i, coluna in enumerate(df.columns):
        nome = str(coluna).strip()

        if nome == "" or nome.lower().startswith("unnamed"):
            nome = f"Coluna {i + 1}"

        novas_colunas.append(nome)

    df.columns = novas_colunas

    # Remove espaços extras em textos
    for coluna in df.columns:
        if df[coluna].dtype == "object":
            df[coluna] = df[coluna].apply(
                lambda x: str(x).strip() if pd.notna(x) else x
            )

    # Tenta converter colunas numéricas
    for coluna in df.columns:
        df[coluna] = tentar_converter_coluna_para_numero(df[coluna])

    return df


def salvar_dados_upload(arquivo):
    """
    Lê Excel ou CSV e salva a base no estado da sessão.
    """

    inicializar_estado_dados()

    nome_arquivo = arquivo.name.lower()

    if nome_arquivo.endswith(".csv"):
        try:
            df = pd.read_csv(arquivo)
        except Exception:
            arquivo.seek(0)
            df = pd.read_csv(arquivo, sep=";")

    elif nome_arquivo.endswith(".xlsx") or nome_arquivo.endswith(".xls"):
        df = pd.read_excel(arquivo)

    else:
        raise ValueError("Formato de arquivo não suportado. Envie Excel ou CSV.")

    df = padronizar_dataframe(df)

    if df.empty:
        raise ValueError("A planilha está vazia ou não possui dados válidos.")

    st.session_state.df_dados = df
    st.session_state.nome_arquivo = arquivo.name
    st.session_state.data_upload = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.dados_carregados = True

    # Sempre que sobe novo arquivo, limpa configuração antiga
    if "configuracao_colunas" in st.session_state:
        del st.session_state.configuracao_colunas

    return df


def obter_dados():
    """
    Retorna o DataFrame salvo.
    """

    inicializar_estado_dados()
    return st.session_state.df_dados


def limpar_dados():
    """
    Limpa os dados carregados.
    """

    st.session_state.df_dados = None
    st.session_state.nome_arquivo = None
    st.session_state.data_upload = None
    st.session_state.dados_carregados = False

    if "configuracao_colunas" in st.session_state:
        del st.session_state.configuracao_colunas
