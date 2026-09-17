"""Componentes de gráficos para o dashboard."""
import streamlit as st
import pandas as pd

def score_radar(scores: dict, titulo: str = "Scores"):
    """Radar chart simples usando st.line_chart com coordenadas polares."""
    df = pd.DataFrame({
        "score": list(scores.values()),
    }, index=list(scores.keys()))
    st.line_chart(df)

def barras_horizontais(df: pd.DataFrame, col_valor: str, col_rotulo: str, titulo: str = "", top_n: int = 10):
    """Gráfico de barras horizontais."""
    df = df.sort_values(col_valor, ascending=True).tail(top_n)
    st.bar_chart(df.set_index(col_rotulo)[col_valor])
