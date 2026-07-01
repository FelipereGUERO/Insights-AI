import streamlit as st
import pandas as pd
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
