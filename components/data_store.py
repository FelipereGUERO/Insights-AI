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
    Converte textos com aparência numérica para formato numérico.
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

    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "")
            texto = texto.replace(",", ".")
        else:
            texto = texto.replace(",", "")

    elif "," in texto:
        texto = texto.replace(".", "")
        texto = texto.replace(",", ".")

    return texto


def tentar_converter_coluna_para_numero(serie):
    """
    Tenta converter uma coluna para número.
    Só converte se a maioria dos valores parecer numérica.
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

    if taxa_conversao >= 0.70:
        return valores_convertidos

    return serie_original.astype(str)


def padronizar_nomes_colunas(df):
    """
    Padroniza nomes de colunas.
    """

    novas_colunas = []

    for i, coluna in enumerate(df.columns):
        nome = str(coluna).strip()

        if nome == "" or nome.lower().startswith("unnamed") or nome.lower() == "nan":
            nome = f"Coluna {i + 1}"

        novas_colunas.append(nome)

    df.columns = novas_colunas

    return df


def remover_linhas_vazias_e_totais_iniciais(df):
    """
    Remove linhas e colunas totalmente vazias.
    """

    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")

    return df


def padronizar_dataframe(df):
    """
    Limpa e padroniza o DataFrame carregado.
    """

    df = remover_linhas_vazias_e_totais_iniciais(df)

    df = padronizar_nomes_colunas(df)

    for coluna in df.columns:
        df[coluna] = tentar_converter_coluna_para_numero(df[coluna])

    return df


def ler_arquivo_excel(arquivo):
    """
    Lê arquivo Excel.
    """

    df = pd.read_excel(arquivo)

    return df


def ler_arquivo_csv(arquivo):
    """
    Lê arquivo CSV com tentativa de separadores comuns.
    """

    try:
        df = pd.read_csv(arquivo)
        return df

    except Exception:
        arquivo.seek(0)
        df = pd.read_csv(arquivo, sep=";")
        return df


def salvar_dados_upload(arquivo):
    """
    Lê o arquivo enviado pelo usuário e salva os dados no session_state.
    Aceita Excel e CSV.
    """

    nome_arquivo = arquivo.name.lower()

    if
