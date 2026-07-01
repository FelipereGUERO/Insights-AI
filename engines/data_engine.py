import pandas as pd


def ler_arquivo(arquivo):
    """
    Lê arquivos Excel ou CSV enviados pelo usuário.
    Retorna um DataFrame do pandas.
    """

    nome_arquivo = arquivo.name.lower()

    if nome_arquivo.endswith(".csv"):
        try:
            df = pd.read_csv(arquivo, sep=None, engine="python")
        except Exception:
            arquivo.seek(0)
            df = pd.read_csv(arquivo, sep=";")

    elif nome_arquivo.endswith(".xlsx") or nome_arquivo.endswith(".xls"):
        df = pd.read_excel(arquivo)

    else:
        raise ValueError("Formato de arquivo não suportado. Envie Excel ou CSV.")

    return df


def resumo_dados(df):
    """
    Gera um resumo básico da planilha.
    """

    total_linhas = df.shape[0]
    total_colunas = df.shape[1]
    colunas = list(df.columns)

    colunas_numericas = df.select_dtypes(include="number").columns.tolist()
    colunas_texto = df.select_dtypes(include="object").columns.tolist()

    resumo = {
        "total_linhas": total_linhas,
        "total_colunas": total_colunas,
        "colunas": colunas,
        "colunas_numericas": colunas_numericas,
        "colunas_texto": colunas_texto,
    }

    return resumo


def limpar_dados(df):
    """
    Faz uma limpeza inicial simples nos dados.
    """

    df_limpo = df.copy()

    # Remove linhas totalmente vazias
    df_limpo = df_limpo.dropna(how="all")

    # Remove colunas totalmente vazias
    df_limpo = df_limpo.dropna(axis=1, how="all")

    # Remove espaços extras dos nomes das colunas
    df_limpo.columns = df_limpo.columns.astype(str).str.strip()

    return df_limpo
