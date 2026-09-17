"""Componentes compartilhados para o dashboard Streamlit."""
import streamlit as st

def metric_card(label: str, value, help_text: str = None):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {f'<div style="color:#666;font-size:0.75rem">{help_text}</div>' if help_text else ''}
    </div>
    """, unsafe_allow_html=True)

def score_bar(score: float, label: str = "Score", max_score: float = 100):
    pct = min(score / max_score, 1.0)
    color = "#00d4aa" if pct > 0.6 else "#ffc107" if pct > 0.3 else "#ff5722"
    st.markdown(f"""
    <div style="margin: 0.5rem 0;">
        <div style="display:flex;justify-content:space-between;color:#888;font-size:0.85rem">
            <span>{label}</span>
            <span>{score:.0f}/{max_score:.0f}</span>
        </div>
        <div style="background:#2a2d37;border-radius:8px;height:10px;overflow:hidden">
            <div style="background:{color};width:{pct*100}%;height:100%;border-radius:8px;
                        transition:width 0.3s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def section_title(title: str):
    st.markdown(f"<h3 style='color:#00d4aa'>{title}</h3>", unsafe_allow_html=True)
