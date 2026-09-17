"""Componentes de filtro para o dashboard."""
import streamlit as st

def filtros_busca():
    col1, col2, col3 = st.columns(3)
    with col1:
        q = st.text_input("🔍 Buscar", placeholder="Nome ou CNPJ", key="filtro_q")
    with col2:
        uf = st.text_input("UF", max_chars=2, placeholder="SP", key="filtro_uf").upper()
    with col3:
        cnae = st.text_input("CNAE", placeholder="46", key="filtro_cnae")
    return q, uf, cnae

def filtros_sidebar():
    with st.sidebar:
        st.markdown("### Filtros")
        porte = st.selectbox("Porte", ["", "ME", "EPP", "DEMAIS", "GRANDE"], key="filtro_porte")
        score_min = st.slider("Score mínimo", 0, 100, 0, key="filtro_score")
        limit = st.number_input("Limite", 10, 200, 50, key="filtro_limit")
    return porte, score_min, limit
