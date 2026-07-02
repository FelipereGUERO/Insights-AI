import streamlit as st


def carregar_css():
    """
    Carrega o arquivo CSS global do Insight AI.
    """

    try:
        with open("styles/styles.css", "r", encoding="utf-8") as arquivo:
            css = arquivo.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )

    except FileNotFoundError:
        st.warning("Arquivo de estilo não encontrado: styles/styles.css")
