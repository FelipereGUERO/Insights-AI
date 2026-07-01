import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime


def inicializar_estado_dados():
    """
    Inicializa as variáveis usadas para guardar os dados da planilha
    durante a sessão do usuário.
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
    Converte textos com aparência numérica para um formato que o pandas entende.

    Exemplos:
    R$ 1.250,50 -> 1250.50
    1.250,50    -> 1250.50
    1250,50     -> 1250.50
    1250.50     -> 1250.50
    44,7%       -> 44.7
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

    # Remove parênteses de número negativo, exemplo: (1000) -> -1000
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
    Só converte se a maior parte dos valores realmente parecer numérica.
    """

    if pd.api.types.is_numeric_dtype(serie):
        return serie

    serie_original = serie.copy()

    valores_normalizados = serie.apply(normalizar_texto_numero)

    valores_convertidos = pd.to_numeric(
        valores_normalizados,
        errors="coerce"
    )

    total_valores_validos = serie_original.notna().sum()

    if total_valores_validos == 0:
        return serie_original

    total_convertidos = valores_convertidos.notna().sum()

    taxa_conversao = total_convertidos / total_valores_validos

    # Se pelo menos 70% da coluna parecer número, converte a coluna inteira
    if taxa_conversao >= 0.7:
        return valores_convertidos

    return serie_original


def padronizar_dataframe(df):
    """
    Limpa e padroniza o DataFrame carregado.
    """

    # Remove linhas e colunas totalmente vazias
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")

    # Remove espaços dos nomes das colunas
    df.columns = [str(col).strip() for col in df.columns]

    # Renomeia colunas sem nome para facilitar leitura
    novas_colunas = []

    for i, coluna in enumerate(df.columns):
        if coluna.startswith("Unnamed"):
            novas_colunas.append(f"Coluna {i + 1}")
        else:
            novas_colunas.append(coluna)

    df.columns = novas_colunas

    # Tenta converter automaticamente colunas numéricas
    for coluna in df.columns:
        df[coluna] = tentar_converter_coluna_para_numero(df[coluna])

    return df


def salvar_dados_upload(arquivo):
    """
    Lê o arquivo enviado pelo usuário e salva os dados no session_state.
    Aceita arquivos Excel e CSV.
    """

    nome_arquivo = arquivo.name.lower()

    if nome_arquivo.endswith(".csv"):
        df = pd.read_csv(arquivo)

    elif nome_arquivo.endswith(".xlsx") or nome_arquivo.endswith(".xls"):
        df = pd.read_excel(arquivo)

    else:
        raise ValueError("Formato de arquivo não suportado. Envie Excel ou CSV.")

    df = padronizar_dataframe(df)

    st.session_state.df_dados = df
    st.session_state.nome_arquivo = arquivo.name
    st.session_state.data_upload = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.session_state.dados_carregados = True

    return df


def obter_dados():
    """
    Retorna o DataFrame salvo na sessão.
    """

    return st.session_state.df_dados


def limpar_dados():
    """
    Remove os dados carregados da sessão.
    """

    st.session_state.df_dados = None
    st.session_state.nome_arquivo = None
    st.session_state.data_upload = None
    st.session_state.dados_carregados = False
