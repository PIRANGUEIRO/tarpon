import streamlit as st
import pandas as pd
import plotly.express as px
import httpx

CSS_MI = """
<style>
.mi-hero { background:linear-gradient(135deg,#0f111a 0%,#151829 100%); border:1px solid #1e2030; border-radius:14px; padding:1.5rem; margin-bottom:0.5rem; position:relative; overflow:hidden; }
.mi-hero::before { content:''; position:absolute; top:0; right:0; width:300px; height:300px; background:radial-gradient(circle,rgba(0,212,170,0.04) 0%,transparent 70%); pointer-events:none; }
.mi-hero .v { font-size:1.8rem; font-weight:700; letter-spacing:-0.5px; }
.mi-hero .l { color:#888; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:2px; }
.mi-hero .sub { color:#555; font-size:0.65rem; }
.mi-row { display:flex; justify-content:space-between; align-items:center; padding:6px 10px; border-bottom:1px solid #181a24; border-radius:6px; margin:2px 0; transition:all 0.15s; }
.mi-row:hover { background:rgba(0,212,170,0.04); }
.mi-badge { display:inline-block; background:#00d4aa18; color:#00d4aa; font-size:0.65rem; padding:1px 8px; border-radius:10px; font-weight:500; }
.stTabs [data-baseweb="tab-list"] { gap:4px; background:#0a0c10; padding:4px; border-radius:10px; }
.stTabs [data-baseweb="tab"] { background:#14161e; border-radius:8px!important; border:1px solid #1e2030; padding:6px 16px!important; font-size:0.75rem; }
.stTabs [aria-selected="true"] { background:#00d4aa15!important; border-color:#00d4aa44!important; color:#00d4aa!important; }
</style>
"""

API = "http://localhost:8000"


def kpi_mi(val, label, sub="", color="#00d4aa"):
    st.markdown(f'<div class="mi-hero"><div class="l">{label}</div><div class="v" style="color:{color};">{val}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)


def build_chart(df, x, y, title="", height=320, color_col=None, orient="h", text=True):
    fig = px.bar(df, x=x, y=y, orientation=orient, text=x if text else None,
                 color=color_col or x, color_continuous_scale="tealgrn",
                 labels={x: x.replace("_", " ").title(), y: ""})
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#aaa", size=11), height=height,
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis=dict(autorange="reversed", gridcolor="#1a1c26", tickfont=dict(size=10)),
        xaxis=dict(gridcolor="#1a1c26", tickfont=dict(size=10)),
        hoverlabel=dict(bgcolor="#1a1c26", font_size=11),
    )
    if text:
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", textfont=dict(size=10))
    return fig


def rank_table(rows, value_key, label_key, fmt="{:,.0f}", pct_key=None, limit=20):
    items = []
    for i, r in enumerate(rows[:limit]):
        val = r.get(value_key, 0)
        lbl = r.get(label_key, "")[:40]
        pct = f" <span style='color:#555;font-size:0.65rem;'>({r.get(pct_key, '')}%)</span>" if pct_key and r.get(pct_key) else ""
        items.append(f"""<div class="mi-row"><span><span style="color:#444;font-size:0.65rem;margin-right:6px;">#{i+1}</span><span style="color:#ccc;font-size:0.8rem;">{lbl}</span></span><span style="color:#00d4aa;font-weight:600;font-size:0.85rem;">{fmt.format(val)}</span>{pct}</div>""")
    st.markdown("".join(items), unsafe_allow_html=True)


@st.cache_data(ttl=60)
def fetch_panorama(filtros_hash: str = ""):
    """Busca panorama de market intel da API."""
    try:
        url = f"{API}/api/market-intel/panorama"
        if filtros_hash:
            url += f"?{filtros_hash}"
        r = httpx.get(url, timeout=30)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def render_market_intel(filtros_ativos=None, df_f=None):
    st.markdown(CSS_MI, unsafe_allow_html=True)

    has_filter = filtros_ativos and df_f is not None and not df_f.empty

    if has_filter:
        st.markdown("---")
        st.markdown("### 📊 Inteligência de Mercado — Dados Filtrados")
        st.caption("Agregado a partir dos registros filtrados no painel lateral")

        d = {}
        d["gerais"] = {}
        d["gerais"]["total_embarques"] = len(df_f)
        d["gerais"]["peso_bruto_ton"] = df_f["peso_kg"].sum() / 1000 if "peso_kg" in df_f.columns else 0
        d["gerais"]["total_teus"] = df_f["teus"].sum() if "teus" in df_f.columns else 0
        d["gerais"]["total_containers"] = df_f["containers"].sum() if "containers" in df_f.columns else 0

        def grp(col, val_col="teus", top=20, out_name=None):
            if col in df_f.columns:
                g = df_f.groupby(col)[val_col].sum().reset_index().sort_values(val_col, ascending=False).head(top)
                if out_name:
                    g = g.rename(columns={col: out_name})
                return g.to_dict("records")
            return []

        d["armadores"] = grp("armador", out_name="nome")
        d["portos_origem"] = [(r["porto_origem"], r["teus"]) for r in grp("porto_origem")]
        d["portos_destino"] = [(r["porto_destino"], r["teus"]) for r in grp("porto_destino")]
        d["paises_origem"] = grp("pais_origem")
        d["agentes_carga_nacionais"] = grp("agente_carga", out_name="nome")

        if "descricao_mercadoria" in df_f.columns:
            d["top_produtos"] = [(r["descricao_mercadoria"], r["teus"]) for r in grp("descricao_mercadoria")]
        elif "ncm" in df_f.columns:
            d["top_produtos"] = [(r["ncm"], r["teus"]) for r in grp("ncm")]
        else:
            d["top_produtos"] = []

        if "consignatario" in df_f.columns:
            d["top_importadores"] = grp("consignatario", out_name="nome")
        else:
            d["top_importadores"] = []

        for campo, chave in [("tipo_embarque", "tipo_embarque"), ("tipo_pagamento", "tipo_pagamento"),
                             ("incoterm", "incoterm"), ("tipo_container", "tipo_container")]:
            if campo in df_f.columns:
                d[chave] = df_f.groupby(campo)["teus"].sum().to_dict()
            else:
                d[chave] = {}

        d["rotas_principais"] = []
        if "porto_origem" in df_f.columns and "porto_destino" in df_f.columns:
            rotas = df_f.groupby(["porto_origem", "porto_destino"])["teus"].sum().reset_index().sort_values("teus", ascending=False).head(10)
            for _, r in rotas.iterrows():
                d["rotas_principais"].append((f"{r['porto_origem']} → {r['porto_destino']}", r["teus"], 0))

        total_teus = d["gerais"]["total_teus"] or 1
        for arm in d["armadores"]:
            arm["share"] = round(arm.get("teus", 0) / total_teus * 100, 2)
        for imp in d["top_importadores"]:
            imp["share"] = round(imp.get("teus", 0) / total_teus * 100, 2)
        for p in d.get("paises_origem", []):
            if isinstance(p, dict):
                p["share"] = round(p.get("teus", 0) / total_teus * 100, 2)

        d["armazens_destino"] = []
        d["agentes_carga_internacionais"] = []
        d["top_exportadores"] = []
    else:
        st.markdown("---")
        st.markdown("### 🌎 Inteligência de Mercado — Panorama Global do Comex Brasileiro")
        st.caption("Dados consolidados do banco de dados — embarques reais + ComexStat")

        # Buscar dados reais da API
        filtros_hash = ""
        try:
            import hashlib
            filtros_hash = hashlib.md5(b"global").hexdigest()[:8]
        except Exception:
            pass

        d = fetch_panorama(filtros_hash)

        if not d or d.get("gerais", {}).get("total_embarques", 0) == 0:
            # Fallback: usar dados estáticos se API não retornar nada
            from data.market_intel import DADOS_MERCADO
            d = DADOS_MERCADO

    # ─── KPI HERO ─────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_mi(f"{d['gerais']['total_embarques']:,}".replace(",", "."), "Embarques", "total registrado", "#00d4aa")
    with c2:
        peso = d['gerais']['peso_bruto_ton']
        kpi_mi(f"{peso/1e6:.1f}M" if peso > 1e6 else f"{peso:,.0f}".replace(",", "."), "Peso Bruto", "toneladas", "#3b82f6")
    with c3:
        teus = d['gerais']['total_teus']
        kpi_mi(f"{teus/1e6:.2f}M" if teus > 1e6 else f"{teus:,.0f}".replace(",", "."), "TEUs", "twenty-foot equivalent", "#f59e0b")
    with c4:
        cont = d['gerais']['total_containers']
        kpi_mi(f"{cont/1e6:.2f}M" if cont > 1e6 else f"{cont:,.0f}".replace(",", "."), "Contêineres", "volume total", "#ef4444")

    # ─── TABS ─────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🚢 Armadores", "🏢 Importadores / Exportadores",
        "🌍 Rotas & Países", "📦 Produtos & Tipos",
        "📍 Portos", "📋 Agentes de Carga"
    ])

    with tab1:
        df_arm = pd.DataFrame(d["armadores"])
        if df_arm.empty:
            st.info("Nenhum dado de armador disponível para este filtro.")
        else:
            col_a1, col_a2 = st.columns([2, 1.3])
            with col_a1:
                fig = build_chart(df_arm.head(15), "teus", "nome", height=380)
                st.plotly_chart(fig, use_container_width=True)
            with col_a2:
                st.markdown("<div style='margin-top:0.5rem;'><span style='color:#888;font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;'>Ranking por TEUs</span></div>", unsafe_allow_html=True)
                rank_table(d["armadores"], "teus", "nome", pct_key="share", limit=15)

    with tab2:
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.markdown("**🏢 Maiores Importadores**")
            df_imp = pd.DataFrame(d["top_importadores"])
            if not df_imp.empty:
                fig = build_chart(df_imp.head(12), "teus", "nome", height=380)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de importadores")
        with col_b2:
            st.markdown("**🌍 Maiores Exportadores**")
            df_exp = pd.DataFrame(d.get("top_exportadores", []))
            if not df_exp.empty:
                fig = build_chart(df_exp.head(12), "teus", "nome", height=380)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de exportadores")

    with tab3:
        col_c1, col_c2 = st.columns(2)
        df_rotas = pd.DataFrame(d["rotas_principais"], columns=["rota", "teus", "share"]) if d.get("rotas_principais") else pd.DataFrame()
        with col_c1:
            st.markdown("**🔄 Principais Rotas**")
            if not df_rotas.empty:
                fig = build_chart(df_rotas, "teus", "rota", height=320)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de rotas")
        with col_c2:
            st.markdown("**🌎 Países de Origem**")
            if d.get("paises_origem"):
                df_paises = pd.DataFrame(d["paises_origem"])
                if "pais" not in df_paises.columns and len(df_paises.columns) >= 2:
                    df_paises = df_paises.rename(columns={df_paises.columns[0]: "pais", df_paises.columns[1]: "teus"})
                if "teus" in df_paises.columns and "pais" in df_paises.columns:
                    fig = build_chart(df_paises.head(12), "teus", "pais", height=320)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Sem dados de países")
            else:
                st.info("Sem dados de países")

    with tab4:
        col_d1, col_d2 = st.columns([2, 1])
        with col_d1:
            st.markdown("**📦 Top Produtos**")
            df_prod = pd.DataFrame(d["top_produtos"], columns=["produto", "volume"]) if d.get("top_produtos") else pd.DataFrame()
            if not df_prod.empty:
                fig = build_chart(df_prod.head(15), "volume", "produto", height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de produtos")
        with col_d2:
            st.markdown("**📊 Distribuições**")
            for label, key in [("Tipo de Embarque", "tipo_embarque"), ("Pagamento", "tipo_pagamento"),
                               ("Incoterm", "incoterm"), ("Container", "tipo_container")]:
                data = d.get(key, {})
                if data:
                    df_tmp = pd.DataFrame(list(data.items()), columns=["tipo", "qtd"])
                    st.markdown(f"<div style='color:#888;font-size:0.7rem;margin-top:8px;'>{label}</div>", unsafe_allow_html=True)
                    st.dataframe(df_tmp.style.format({"qtd": "{:,.0f}"}), use_container_width=True, height=min(30 * len(df_tmp) + 10, 120))

    with tab5:
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.markdown("**🚢 Portos de Origem**")
            df_po = pd.DataFrame(d["portos_origem"], columns=["porto", "teus"]) if d.get("portos_origem") else pd.DataFrame()
            if not df_po.empty:
                fig = build_chart(df_po.head(12), "teus", "porto", height=380)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de portos de origem")
        with col_e2:
            st.markdown("**📍 Portos de Destino**")
            df_pd = pd.DataFrame(d["portos_destino"], columns=["porto", "teus"]) if d.get("portos_destino") else pd.DataFrame()
            if not df_pd.empty:
                fig = build_chart(df_pd.head(12), "teus", "porto", height=380)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de portos de destino")

    with tab6:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown("**🇧🇷 Agentes Nacionais**")
            df_an = pd.DataFrame(d["agentes_carga_nacionais"])
            if not df_an.empty:
                fig = build_chart(df_an.head(12), "teus", "nome", height=380)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de agentes nacionais")
        with col_f2:
            st.markdown("**🌐 Agentes Internacionais**")
            df_ai = pd.DataFrame(d.get("agentes_carga_internacionais", []))
            if not df_ai.empty:
                fig = build_chart(df_ai.head(12), "teus", "nome", height=380)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de agentes internacionais")
