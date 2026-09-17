import streamlit as st
import httpx
import pandas as pd
from datetime import datetime

API = "http://localhost:8000"

@st.cache_data(ttl=30)
def fetch(path):
    try:
        r = httpx.get(f"{API}{path}", timeout=15)
        return r.json() if r.status_code == 200 else {"erro": r.status_code}
    except Exception as e:
        return {"erro": str(e)}

CSS_EMBARQUES = """
<style>
    .emb-kpi { background: #14161e; padding: 0.8rem; border-radius: 8px; border: 1px solid #1e2030; text-align: center; }
    .emb-kpi .v { font-size: 1.4rem; font-weight: bold; color: #00d4aa; }
    .emb-kpi .l { color: #888; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .emb-kpi .s { color: #555; font-size: 0.65rem; }
    .emb-label { color: #999; font-size: 0.75rem; margin-bottom: 2px; }
    .emb-val { color: #00d4aa; font-weight: 600; font-size: 0.95rem; }
    .emb-val-muted { color: #88d4c0; font-weight: 500; font-size: 0.85rem; }
    .emb-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 8px; border-bottom: 1px solid #1a1c26; background: #0f1117; border-radius: 4px; margin: 2px 0; }
    .emb-row:hover { background: #1a1c28; }
    div[data-testid="stDataFrame"] { font-size: 0.75rem !important; }
    div[data-testid="stDataFrame"] td { padding: 4px 8px !important; }
    .st-bb { background-color: #14161e !important; }
</style>
"""

def render_embarques(cnpj: str, razao_social: str):
    st.markdown(CSS_EMBARQUES, unsafe_allow_html=True)

    params = f"cnpj={cnpj}"
    resumo = fetch(f"/api/embarques/resumo?{params}")

    if "erro" in resumo or resumo.get("total_embarques", 0) == 0:
        st.info("Nenhum embarque encontrado para este CNPJ no período.")
        return

    r = resumo

    st.markdown("### 📊 KPIs")
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f'<div class="emb-kpi"><div class="v">{r["total_embarques"]:,}</div><div class="l">Embarques</div><div class="s">total</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="emb-kpi"><div class="v">{r["peso_bruto_ton"]:,.1f}</div><div class="l">Peso Bruto</div><div class="s">toneladas</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="emb-kpi"><div class="v">{r["total_teus"]:,.0f}</div><div class="l">TEUs</div><div class="s">total</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="emb-kpi"><div class="v">{r["total_containers"]:,}</div><div class="l">Contêineres</div><div class="s">total</div></div>', unsafe_allow_html=True)
    with k5:
        vf = r.get("valor_fob_total", 0)
        st.markdown(f'<div class="emb-kpi"><div class="v">R$ {vf/1e6:.2f}M</div><div class="l">Valor FOB</div><div class="s">total</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    modais = r.get("por_modal", {})
    total_modal = sum(modais.values()) or 1

    st.markdown("#### 📦 Tipo Embarque")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        te_data = fetch(f"/api/embarques/tipo-embarque?{params}")
        if te_data and "erro" not in te_data:
            df_te = pd.DataFrame(te_data)
            if not df_te.empty:
                st.bar_chart(df_te.set_index("tipo")["quantidade"], height=250)

    with col_b:
        st.markdown("**Distribuição por Tipo de Embarque**")
        tipos_map = {"DIRETO": r["direto"], "HOUSE": r["house"], "COLOADER": r["coloader"], "MASTER": r["master"]}
        total_t = sum(tipos_map.values()) or 1
        for t, v in tipos_map.items():
            pct = v / total_t * 100
            st.markdown(f"""
            <div class="emb-row">
                <span class="emb-label">{t}</span>
                <span><span class="emb-val">{v:,}</span> <span style="color:#555;font-size:0.7rem">({pct:.1f}%)</span></span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 💳 Pagamento")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        pg_data = fetch(f"/api/embarques/pagamento?{params}")
        if pg_data and "erro" not in pg_data:
            df_pg = pd.DataFrame(pg_data)
            if not df_pg.empty:
                st.bar_chart(df_pg.set_index("tipo")["quantidade"], height=250)
    with col_b:
        st.markdown("**Distribuição por Tipo de Pagamento**")
        pags = {"COLLECT": r["collect"], "PREPAID": r["prepaid"]}
        total_pag = sum(pags.values()) or 1
        for t, v in pags.items():
            pct = v / total_pag * 100
            st.markdown(f"""
            <div class="emb-row">
                <span class="emb-label">{t}</span>
                <span><span class="emb-val">{v:,}</span> <span style="color:#555;font-size:0.7rem">({pct:.1f}%)</span></span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📋 Incoterms")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        ic_data = fetch(f"/api/embarques/incoterm?{params}")
        if ic_data and "erro" not in ic_data:
            df_ic = pd.DataFrame(ic_data)
            if not df_ic.empty:
                st.bar_chart(df_ic.set_index("incoterm")["quantidade"], height=250)
    with col_b:
        st.markdown("**Distribuição por Incoterm**")
        incs = {"FOB": r["fob"], "EXW": r["exw"], "CFR": r["cfr"], "CIF": r["cif"]}
        total_inc = sum(incs.values()) or 1
        for t, v in incs.items():
            pct = v / total_inc * 100
            st.markdown(f"""
            <div class="emb-row">
                <span class="emb-label">{t}</span>
                <span><span class="emb-val">{v:,}</span> <span style="color:#555;font-size:0.7rem">({pct:.1f}%)</span></span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📈 Por Mês")
    mes_data = fetch(f"/api/embarques/por-mes?{params}")
    if mes_data and "erro" not in mes_data:
        df_mes = pd.DataFrame(mes_data)
        if not df_mes.empty:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                df_plot = df_mes.set_index("mes")[["quantidade"]]
                st.line_chart(df_plot, height=250)
            with col_m2:
                df_plot2 = df_mes.set_index("mes")[["peso_ton"]]
                st.line_chart(df_plot2, height=250)

            st.dataframe(
                df_mes.style.format({"peso_ton": "{:,.2f} t", "teus": "{:,.1f}"}),
                use_container_width=True,
            )

    st.markdown("---")
    st.markdown("#### 🚢 Modal")
    st.markdown("**🚢 Distribuição por Modal**")
    col_md1, col_md2, col_md3 = st.columns(3)
    with col_md1:
        st.markdown(f'<div class="emb-kpi"><div class="v">{modais.get("maritimo",0):,}</div><div class="l">Marítimo</div><div class="s">{modais.get("maritimo",0)/total_modal*100:.1f}%</div></div>', unsafe_allow_html=True)
    with col_md2:
        st.markdown(f'<div class="emb-kpi"><div class="v">{modais.get("aereo",0):,}</div><div class="l">Aéreo</div><div class="s">{modais.get("aereo",0)/total_modal*100:.1f}%</div></div>', unsafe_allow_html=True)
    with col_md3:
        st.markdown(f'<div class="emb-kpi"><div class="v">{total_modal:,}</div><div class="l">Total</div><div class="s">100%</div></div>', unsafe_allow_html=True)

    df_modal = pd.DataFrame([
        {"modal": "MARÍTIMO", "quantidade": modais.get("maritimo", 0)},
        {"modal": "AÉREO", "quantidade": modais.get("aereo", 0)},
    ])
    col_md_a, col_md_b = st.columns([1, 1])
    with col_md_a:
        st.bar_chart(df_modal.set_index("modal"), height=250)
    with col_md_b:
        for m, v in modais.items():
            pct = v / total_modal * 100
            st.markdown(f"""
            <div class="emb-row">
                <span class="emb-label">{'MARÍTIMO' if m == 'maritimo' else 'AÉREO'}</span>
                <span><span class="emb-val">{v:,}</span> <span style="color:#555;font-size:0.7rem">({pct:.1f}%)</span></span>
            </div>
            """, unsafe_allow_html=True)

    embarques_modal = fetch(f"/api/embarques?{params}&limit=200")
    if embarques_modal and "erro" not in embarques_modal and embarques_modal.get("embarques"):
        df_emb_m = pd.DataFrame(embarques_modal["embarques"])
        if "modal" in df_emb_m.columns and "data_embarque" in df_emb_m.columns:
            df_emb_m["data_embarque"] = pd.to_datetime(df_emb_m["data_embarque"], errors="coerce")
            df_emb_m["mes"] = df_emb_m["data_embarque"].dt.to_period("M").astype(str)
            st.markdown("**📈 Tendência por Modal**")
            df_modal_mes = df_emb_m.groupby(["mes", "modal"]).size().reset_index(name="qtd")
            try:
                df_pivot_m = df_modal_mes.pivot_table(index="mes", columns="modal", values="qtd", aggfunc="sum", fill_value=0)
                st.line_chart(df_pivot_m, height=250)
            except Exception:
                pass

    st.markdown("---")
    st.markdown("#### 🚢 Armador")
    arm_data = fetch(f"/api/embarques/por-armador?{params}")
    if arm_data and "erro" not in arm_data and arm_data:
        df_arm = pd.DataFrame(arm_data)
        armadores_top = df_arm.groupby("armador")["quantidade"].sum().nlargest(8).index.tolist()
        df_arm_top = df_arm[df_arm["armador"].isin(armadores_top)]
        df_pivot = df_arm_top.pivot_table(
            index="mes", columns="armador", values="quantidade", aggfunc="sum", fill_value=0
        )
        st.markdown("**🚢 Embarques por Armador (Top 8)**")
        st.line_chart(df_pivot, height=350)

        st.markdown("**📊 Total por Armador**")
        total_arm = df_arm.groupby("armador")["quantidade"].sum().sort_values(ascending=False).reset_index()
        total_arm.columns = ["Armador", "Embarques"]
        col_a1, col_a2 = st.columns([2, 1])
        with col_a1:
            st.bar_chart(total_arm.set_index("Armador").head(15), height=300)
        with col_a2:
            for _, row in total_arm.head(10).iterrows():
                st.markdown(f"""
                <div class="emb-row">
                    <span class="emb-label">{row['Armador'][:25]}</span>
                    <span class="emb-val">{row['Embarques']:,}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nenhum dado de armador disponível.")

    st.markdown("---")
    st.markdown("#### 🌍 País Origem")
    pais_data = fetch(f"/api/embarques/por-pais?{params}")
    if pais_data and "erro" not in pais_data and pais_data:
        df_pais = pd.DataFrame(pais_data)
        total_pais = df_pais.groupby("pais")["quantidade"].sum().sort_values(ascending=False).reset_index()
        total_pais.columns = ["País", "Embarques"]

        col_pie, col_rank = st.columns([2, 1])
        with col_pie:
            st.markdown("**🌍 Distribuição por País de Origem**")
            import plotly.express as px
            fig = px.pie(
                total_pais.head(10),
                names="País",
                values="Embarques",
                color_discrete_sequence=px.colors.sequential.Tealgrn,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ccc", size=11),
                margin=dict(t=0, b=0, l=0, r=0),
                height=380,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_rank:
            st.markdown("**📊 Ranking**")
            for _, row in total_pais.head(10).iterrows():
                st.markdown(f"""
                <div class="emb-row">
                    <span class="emb-label">{row['País'][:25]}</span>
                    <span class="emb-val">{row['Embarques']:,}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nenhum dado de país de origem disponível.")

    st.markdown("---")
    st.markdown("#### 🤝 Agente de Carga")
    embarques_list = fetch(f"/api/embarques?{params}&limit=200")
    if embarques_list and "erro" not in embarques_list and embarques_list.get("embarques"):
        df_emb = pd.DataFrame(embarques_list["embarques"])

        if "agente_carga" in df_emb.columns:
            top_agents = df_emb["agente_carga"].value_counts().reset_index()
            top_agents.columns = ["Agente de Carga", "Embarques"]

            st.markdown("**🤝 Top Agentes de Carga**")
            col_ag1, col_ag2 = st.columns([2, 1])
            with col_ag1:
                st.bar_chart(top_agents.set_index("Agente de Carga").head(15), height=350)
            with col_ag2:
                for _, row in top_agents.head(10).iterrows():
                    pct = row["Embarques"] / len(df_emb) * 100
                    st.markdown(f"""
                    <div class="emb-row">
                        <span class="emb-label">{row['Agente de Carga'][:25]}</span>
                        <span><span class="emb-val">{row['Embarques']:,}</span> <span style="color:#555;font-size:0.7rem">({pct:.1f}%)</span></span>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**📋 Últimos Embarques**")
        cols = ["data_embarque", "ncm", "descricao_mercadoria", "pais_origem", "porto_origem",
                "porto_destino", "modal", "tipo_embarque", "agente_carga", "armador",
                "peso_kg", "teus", "containers", "valor_fob"]
        cols = [c for c in cols if c in df_emb.columns]
        df_show = df_emb[cols].copy()
        if "peso_kg" in df_show.columns:
            df_show["peso_ton"] = (df_show["peso_kg"] / 1000).round(2)
            df_show = df_show.drop(columns=["peso_kg"])
        if "valor_fob" in df_show.columns:
            df_show["valor_fob"] = df_show["valor_fob"].fillna(0).round(2)
        st.dataframe(
            df_show.style.format({"valor_fob": "R$ {:,.2f}"}),
            use_container_width=True, height=350,
        )
