import streamlit as st
import httpx
import pandas as pd
from datetime import datetime

from components.embarques import render_embarques
from components.filtro_premium import render_filtro_premium
from components.market_intel import render_market_intel


API = "http://localhost:8000"

st.set_page_config(page_title="Radar de Elite — Comex Intelligence", layout="wide")

CSS = """
<style>
    .main > div { padding: 1rem 1.5rem; }
    .stApp { background-color: #0a0c10; }
    h1, h2, h3 { color: #00d4aa !important; font-weight: 600; }
    h1 { font-size: 1.6rem; margin-bottom: 0.5rem; }
    h2 { font-size: 1.2rem; margin-bottom: 0.3rem; }
    .stMetric { background: #14161e; padding: 1rem; border-radius: 10px; border: 1px solid #1e2030; }
    .stMetric label { color: #888; }
    .stMetric [data-testid="stMetricValue"] { color: #00d4aa; font-size: 1.8rem; }
    .metric-card {
        background: #14161e; padding: 1.2rem; border-radius: 10px;
        border: 1px solid #1e2030; text-align: center;
    }
    .metric-card .value { font-size: 1.8rem; font-weight: bold; color: #00d4aa; }
    .metric-card .label { color: #666; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-card .sub { color: #444; font-size: 0.7rem; }
    .score-bar-bg { background: #1e2030; border-radius: 6px; height: 8px; overflow: hidden; }
    .score-bar-fill { height: 100%; border-radius: 6px; }
    div[data-testid="stDataFrame"] { font-size: 0.8rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 0; }
    .stTabs [data-baseweb="tab"] { background: #14161e; border-radius: 8px 8px 0 0; }
    .stTabs [aria-selected="true"] { background: #00d4aa22; border-bottom: 2px solid #00d4aa; }
    .stAlert { background: #14161e; border: 1px solid #1e2030; color: #ccc; }
    hr { border-color: #1e2030; }
    .stButton button { border-radius: 8px; border: 1px solid #2a2d37; background: #14161e; color: #ccc; }
    .stButton button:hover { border-color: #00d4aa; color: #00d4aa; }
    .stTextInput input { background: #14161e; border: 1px solid #2a2d37; color: #ccc; border-radius: 8px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

SIDEBAR_CSS = """
<style>
    [data-testid="stSidebar"] { background: #0f1117; border-right: 1px solid #1e2030; }
    [data-testid="stSidebar"] .stRadio label { font-size: 0.9rem; }
</style>
"""
st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="padding: 0.5rem 0; text-align: center;">
    <span style="font-size: 1.5rem; font-weight: bold; color: #00d4aa;">⚡ Radar</span>
    <span style="font-size: 1.5rem; font-weight: 300; color: #555;">de Elite</span>
    <div style="color: #444; font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase;">Comex Intelligence</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "📦 Operações", "🌍 Geo", "⚙️ Admin"],
)

st.sidebar.markdown("---")

filtros = render_filtro_premium()

st.sidebar.caption("Filtro premium centraliza buscas. Todas as páginas refletem a seleção.")

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="color: #333; font-size: 0.7rem; padding: 0.5rem;">
    Radar de Elite v2.0<br>
    Dados: APIs em tempo real (BrasilAPI, ReceitaWS, ComexStat)<br>
    Última atualização: {0}
</div>
""".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)

@st.cache_data(ttl=30)
def fetch(path):
    try:
        r = httpx.get(f"{API}{path}", timeout=15)
        return r.json() if r.status_code == 200 else {"erro": r.status_code}
    except Exception as e:
        return {"erro": str(e)}

def kpi_card(label, value, sub=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">{value}</div>
        <div class="label">{label}</div>
        <div class="sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

def score_bar(label, score, max_score=100):
    pct = min(score / max_score, 1.0)
    color = "#00d4aa" if pct > 0.6 else "#ffc107" if pct > 0.3 else "#ff5722"
    st.markdown(f"""
    <div style="margin:4px 0">
      <div style="display:flex;justify-content:space-between;color:#666;font-size:0.75rem">
        <span>{label}</span><span>{score:.0f}/{max_score:.0f}</span>
      </div>
      <div class="score-bar-bg"><div class="score-bar-fill" style="background:{color};width:{pct*100}%"></div></div>
    </div>
    """, unsafe_allow_html=True)

def montar_query_filtro(f):
    params = {}
    if f.get("cnpj"): params["cnpj"] = f["cnpj"]
    if f.get("anos"):
        anos = [str(x) for x in f["anos"]]
        params["ano"] = anos[0] if anos else "2025"
    if f.get("uf_imp"): params["uf"] = ",".join(f["uf_imp"])
    if f.get("ncm_posicao"): params["ncm"] = f["ncm_posicao"]
    if f.get("ncm_capitulo"): params["ncm"] = f["ncm_capitulo"]
    if f.get("pais_origem"): params["pais"] = ",".join(f["pais_origem"])
    return "&".join(f"{k}={v}" for k, v in params.items())

# ─── DASHBOARD ─────────────────────────────────────────────────────
if "Dashboard" in pagina:
    st.title("📊 Resumo Executivo")

    filtros_ativos = {k: v for k, v in filtros.items() if v and (
        isinstance(v, list) and len(v) > 0 or isinstance(v, str) and v.strip()
    )}
    qs = montar_query_filtro(filtros) if filtros_ativos else ""
    dados_filtrados = fetch(f"/api/filtro/buscar?{qs}&limit=500") if qs else None

    if filtros_ativos and dados_filtrados:
        resultados = dados_filtrados.get("resultados", [])
        total_filtro = dados_filtrados.get("total", 0)
        if resultados:
            df_f = pd.DataFrame(resultados)
            fob_total = df_f["valor_fob"].sum() if "valor_fob" in df_f.columns else 0
            n_emb_f = len(resultados)
            teus_f = df_f["teus"].sum() if "teus" in df_f.columns else 0
            peso_f = df_f["peso_kg"].sum() if "peso_kg" in df_f.columns else 0
            ncms_f = df_f["ncm"].nunique() if "ncm" in df_f.columns else 0
            paises_f = df_f["pais_origem"].nunique() if "pais_origem" in df_f.columns else 0
            n_emp_f = df_f["empresa_id"].nunique() if "empresa_id" in df_f.columns else 0
            st.caption(f"🔍 Dados filtrados por {total_filtro} registros")
        else:
            fob_total = 0; n_emp_f = 0; n_emb_f = 0; teus_f = 0; peso_f = 0; ncms_f = 0; paises_f = 0; df_f = pd.DataFrame()
    else:
        resumo = fetch("/api/comex/resumo")
        ufs_data = fetch("/api/comex/ufs").get("ufs", [])
        top_ncms = fetch("/api/comex/top-ncms?limit=5").get("ncms", [])
        emb_resumo = fetch("/api/embarques/resumo")
        track_stats = fetch("/api/tracking/stats")
        df_f = pd.DataFrame()

    kpi_style = lambda c: f"background:linear-gradient(135deg,#0f111a 0%,#151829 100%);border-radius:14px;border:1px solid #1e2030;padding:1.2rem;position:relative;overflow:hidden;"
    kpi_glow = lambda c: f"<div style='position:absolute;top:-30px;right:-30px;width:120px;height:120px;background:radial-gradient(circle,{c}22 0%,transparent 70%);pointer-events:none;'></div>"

    col_k1, col_k2, col_k3, col_k4 = st.columns(4)

    if filtros_ativos and not df_f.empty:
        with col_k1:
            st.markdown(f"""
            <div style="{kpi_style('#00d4aa')}">{kpi_glow('#00d4aa')}
                <div style="color:#888;font-size:0.65rem;letter-spacing:1px;text-transform:uppercase;">FOB Total</div>
                <div style="font-size:1.8rem;font-weight:700;color:#00d4aa;margin:4px 0;">R$ {fob_total/1e6:.2f}M</div>
                <div style="display:flex;gap:12px;color:#555;font-size:0.65rem;"><span>{ncms_f} NCMs</span><span>{paises_f} países</span></div>
            </div>""", unsafe_allow_html=True)
        with col_k2:
            st.markdown(f"""
            <div style="{kpi_style('#3b82f6')}">{kpi_glow('#3b82f6')}
                <div style="color:#888;font-size:0.65rem;letter-spacing:1px;text-transform:uppercase;">Empresas</div>
                <div style="font-size:1.8rem;font-weight:700;color:#3b82f6;margin:4px 0;">{n_emp_f}</div>
                <div style="display:flex;gap:12px;color:#555;font-size:0.65rem;"><span>{n_emb_f} embarques</span><span>{teus_f:,.0f} TEUs</span></div>
            </div>""", unsafe_allow_html=True)
        with col_k3:
            st.markdown(f"""
            <div style="{kpi_style('#f59e0b')}">{kpi_glow('#f59e0b')}
                <div style="color:#888;font-size:0.65rem;letter-spacing:1px;text-transform:uppercase;">Embarques</div>
                <div style="font-size:1.8rem;font-weight:700;color:#f59e0b;margin:4px 0;">{n_emb_f:,}</div>
                <div style="display:flex;gap:12px;color:#555;font-size:0.65rem;"><span>{teus_f:,.0f} TEUs</span><span>{peso_f/1000:,.0f}t</span></div>
            </div>""", unsafe_allow_html=True)
        with col_k4:
            st.markdown(f"""
            <div style="{kpi_style('#ef4444')}">{kpi_glow('#ef4444')}
                <div style="color:#888;font-size:0.65rem;letter-spacing:1px;text-transform:uppercase;">Peso Bruto</div>
                <div style="font-size:1.8rem;font-weight:700;color:#ef4444;margin:4px 0;">{peso_f/1e6:.1f}M</div>
                <div style="display:flex;gap:12px;color:#555;font-size:0.65rem;"><span>kg</span><span>{teus_f:,.0f} TEUs</span></div>
            </div>""", unsafe_allow_html=True)
    else:
        with col_k1:
            st.markdown(f"""
            <div style="{kpi_style('#00d4aa')}">{kpi_glow('#00d4aa')}
                <div style="color:#888;font-size:0.65rem;letter-spacing:1px;text-transform:uppercase;">FOB Total</div>
                <div style="font-size:1.8rem;font-weight:700;color:#00d4aa;margin:4px 0;">R$ {resumo.get('total_fob',0)/1e9:.2f}B</div>
                <div style="display:flex;gap:12px;color:#555;font-size:0.65rem;"><span>{resumo.get('total_ncms',0):,} NCMs</span><span>{resumo.get('total_paises',0)} países</span></div>
            </div>""", unsafe_allow_html=True)
        with col_k2:
            st.markdown(f"""
            <div style="{kpi_style('#3b82f6')}">{kpi_glow('#3b82f6')}
                <div style="color:#888;font-size:0.65rem;letter-spacing:1px;text-transform:uppercase;">Empresas</div>
                <div style="font-size:1.8rem;font-weight:700;color:#3b82f6;margin:4px 0;">—</div>
                <div style="display:flex;gap:12px;color:#555;font-size:0.65rem;"><span>Busca por CNPJ</span><span>{resumo.get('total_ufs',0)} UFs</span></div>
            </div>""", unsafe_allow_html=True)
        with col_k3:
            n_emb = emb_resumo.get('total_embarques', 0)
            teus = emb_resumo.get('total_teus', 0)
            st.markdown(f"""
            <div style="{kpi_style('#f59e0b')}">{kpi_glow('#f59e0b')}
                <div style="color:#888;font-size:0.65rem;letter-spacing:1px;text-transform:uppercase;">Embarques</div>
                <div style="font-size:1.8rem;font-weight:700;color:#f59e0b;margin:4px 0;">{n_emb:,}</div>
                <div style="display:flex;gap:12px;color:#555;font-size:0.65rem;"><span>{teus:,.0f} TEUs</span><span>{emb_resumo.get('peso_bruto_ton',0):,.0f}t</span></div>
            </div>""", unsafe_allow_html=True)
        with col_k4:
            vlr_fob = emb_resumo.get('valor_fob_total', 0)
            peso = emb_resumo.get('peso_bruto_ton', 0)
            st.markdown(f"""
            <div style="{kpi_style('#ef4444')}">{kpi_glow('#ef4444')}
                <div style="color:#888;font-size:0.65rem;letter-spacing:1px;text-transform:uppercase;">Peso Bruto</div>
                <div style="font-size:1.8rem;font-weight:700;color:#ef4444;margin:4px 0;">{peso/1e6:.1f}M</div>
                <div style="display:flex;gap:12px;color:#555;font-size:0.65rem;"><span>toneladas</span><span>R$ {vlr_fob/1e6:.1f}M</span></div>
            </div>""", unsafe_allow_html=True)

    render_market_intel(filtros_ativos=filtros_ativos, df_f=df_f if not df_f.empty else None)

    # ─── Se CNPJ foi digitado no filtro ────────────────────────
    cnpj_digitado = filtros.get("cnpj", "").strip()
    empresa_unica = None
    if cnpj_digitado:
        cnpj_clean = cnpj_digitado.replace(".", "").replace("/", "").replace("-", "")
        if len(cnpj_clean) == 14:
            emp_data = fetch(f"/api/empresas/cnpj/{cnpj_clean}")
            if "erro" not in emp_data:
                empresa_unica = emp_data

    if empresa_unica:
        e = empresa_unica
        cnpj = e.get("cnpj", "")
        cnae = e.get("cnae_principal", "") or ""
        cnae_fmt = f"{cnae[:2]}.{cnae[2:4]}-{cnae[4:]}" if len(cnae) == 7 else cnae
        porte = e.get("porte", "—")

        st.markdown(f"""
        <div style="background:#0f111a; border:1px solid #1e2030; border-radius:12px; padding:1.2rem 1.5rem; margin-bottom:0.5rem;">
            <div style="font-size:1.3rem; font-weight:700; color:#00d4aa;">{e['razao_social']} — {e.get('municipio','')}/{e.get('uf','')}</div>
            <div style="color:#888; font-size:0.85rem; margin-top:0.4rem;">
                🆔 {cnpj} · 📂 {cnae_fmt} · 💰 R$ {e.get('capital_social',0):,.0f} · 🏢 {porte} · 📊 {e.get('situacao_cadastral','—')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Calcular scoring
        scores_data = fetch(f"/api/scoring/calcular/{cnpj}")
        if "erro" not in scores_data and scores_data.get("scores"):
            col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
            with col_s1:
                for sc in scores_data["scores"]:
                    val = sc["score_valor"]
                    label = sc["score_tipo"].replace("_", " ").title()
                    pct = val / 100
                    cor = "#00d4aa" if pct > 0.6 else "#ffc107" if pct > 0.3 else "#ff5722"
                    st.markdown(f"""
                    <div style="margin:4px 0">
                        <div style="display:flex;justify-content:space-between;color:#666;font-size:0.75rem">
                            <span>{label}</span><span>{val:.0f}/100</span>
                        </div>
                        <div style="background:#1e2030;border-radius:6px;height:8px;overflow:hidden;">
                            <div style="height:100%;border-radius:6px;background:{cor};width:{pct*100}%"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_s2:
                geo = scores_data.get("geo")
                if geo and geo.get("enriquecido"):
                    st.markdown(f"""
                    <div style="background:#14161e; border:1px solid #1e2030; border-radius:10px; padding:0.8rem 1rem; text-align:center;">
                        <div style="color:#888; font-size:0.7rem;">DISTÂNCIA</div>
                        <div style="font-size:1.1rem; font-weight:700; color:#60a5fa; margin:0.3rem 0;">{geo.get('distancia_porto_km',0):.0f} km</div>
                        <div style="color:#555; font-size:0.7rem;">do porto mais próximo</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_s3:
                score_geral = scores_data.get("score_geral", 0)
                pct_g = score_geral / 100
                st.markdown(f"""
                <div style="background:#14161e; border:1px solid #1e2030; border-radius:10px; padding:0.8rem 1rem; text-align:center;">
                    <div style="color:#888; font-size:0.7rem;">SCORE GERAL</div>
                    <div style="font-size:2rem; font-weight:700; color:#ffd700;">{score_geral:.0f}</div>
                    <div style="background:#1e2030;border-radius:6px;height:6px;overflow:hidden;margin-top:0.3rem;">
                        <div style="height:100%;border-radius:6px;background:#ffd700;width:{pct_g*100}%"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        render_embarques(cnpj, e.get("razao_social", ""))
        st.markdown("---")

    st.subheader("🏢 Buscar Empresa")
    col_b1, col_b2 = st.columns([2, 1])
    with col_b1:
        cnpj_input = st.text_input("CNPJ", placeholder="Digite o CNPJ (apenas números)", max_chars=18)
    with col_b2:
        if st.button("🔍 Buscar", type="primary", use_container_width=True):
            cnpj_norm = cnpj_input.replace(".","").replace("/","").replace("-","")
            if len(cnpj_norm) == 14:
                dados = fetch(f"/api/empresas/cnpj/{cnpj_norm}")
                if "erro" not in dados:
                    st.success(f"Empresa encontrada: {dados.get('razao_social', '')}")
                else:
                    st.warning(dados.get("erro", "CNPJ não encontrado"))

    st.markdown("---")
    st.subheader("🌎 UFs")

    if filtros_ativos and not df_f.empty and "uf" in df_f.columns:
        uf_agg = df_f.groupby("uf").agg(
            total_fob=("valor_fob", "sum"),
            qtd=("id", "count"),
            ncms=("ncm", "nunique"),
        ).reset_index().sort_values("total_fob", ascending=False)
        col_uf1, col_uf2 = st.columns([2, 1])
        with col_uf1:
            st.markdown("**🌎 Ranking por UF (FOB) — Filtrado**")
            st.bar_chart(uf_agg.set_index("uf")["total_fob"] / 1e6, height=300)
        with col_uf2:
            st.dataframe(
                uf_agg.style.format({"total_fob": "R$ {:,.0f}"}),
                use_container_width=True, height=300,
            )
        if "pais_origem" in df_f.columns:
            st.markdown("**🌍 Países de Origem — Filtrado**")
            pais_agg = df_f.groupby("pais_origem").agg(total_fob=("valor_fob", "sum"), qtd=("id", "count")).reset_index().sort_values("total_fob", ascending=False)
            st.bar_chart(pais_agg.set_index("pais_origem")["total_fob"] / 1e6, height=250)
    else:
        ufs_data = fetch("/api/comex/ufs").get("ufs", [])
        top_ncms = fetch("/api/comex/top-ncms?limit=5").get("ncms", [])
        col_uf1, col_uf2 = st.columns([2, 1])
        with col_uf1:
            if ufs_data:
                df_ufs = pd.DataFrame(ufs_data)
                st.markdown("**🌎 Ranking por UF (FOB)**")
                st.bar_chart(df_ufs.set_index("uf")[["total_fob"]] / 1e6, height=300)
            else:
                st.info("Nenhum dado de comex.")
        col_uf2_1, col_uf2_2 = st.columns([1, 1])
        with col_uf2_1:
            if ufs_data:
                st.markdown("**📊 Dados**")
                st.dataframe(pd.DataFrame(ufs_data)[["uf", "ncms", "total_fob", "qtd"]].style.format({"total_fob": "R$ {:,.0f}"}), use_container_width=True, height=300)
        with col_uf2_2:
            if top_ncms:
                st.markdown("**📦 Top 5 NCMs**")
                st.dataframe(pd.DataFrame(top_ncms)[["ncm", "ufs", "paises", "total_fob"]].style.format({"total_fob": "R$ {:,.0f}"}), use_container_width=True, height=300)
        if top_ncms:
            st.markdown("**📦 Top NCMs — FOB (R$ M)**")
            st.bar_chart(pd.DataFrame(top_ncms).set_index("ncm")[["total_fob"]] / 1e6, height=200)

    st.markdown("---")
    st.subheader("🚢 Embarques")

    if filtros_ativos and not df_f.empty:
        n_emb = len(df_f)
        peso_ton = df_f["peso_kg"].sum() / 1000 if "peso_kg" in df_f.columns else 0
        teus = df_f["teus"].sum() if "teus" in df_f.columns else 0
        vlr_fob = df_f["valor_fob"].sum() if "valor_fob" in df_f.columns else 0
        containers = df_f["containers"].sum() if "containers" in df_f.columns else 0

        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        with col_e1: kpi_card("Embarques (Filtrado)", f'{n_emb:,}', "total")
        with col_e2: kpi_card("Peso", f'{peso_ton:,.1f}t', "bruto")
        with col_e3: kpi_card("TEUs", f'{teus:,.0f}', "total")
        with col_e4: kpi_card("Valor FOB", f'R$ {vlr_fob/1e6:.1f}M', "total")

        col_m1, col_m2 = st.columns([1, 2])
        with col_m1:
            if "modal" in df_f.columns:
                modal_counts = df_f["modal"].value_counts()
                for m, v in modal_counts.items():
                    pct = v / len(df_f) * 100
                    st.markdown(f"""<div style="background:#14161e; padding:8px; border-radius:6px; margin:4px 0;"><span style="color:#888;">{m}</span> <span><span style="color:#00d4aa; font-weight:bold;">{v:,}</span> <span style="color:#555;">({pct:.1f}%)</span></span></div>""", unsafe_allow_html=True)
        with col_m2:
            if "modal" in df_f.columns:
                st.bar_chart(df_f["modal"].value_counts(), height=200)

        if "armador" in df_f.columns:
            st.markdown("**🚢 Embarques por Armador**")
            arm_agg = df_f["armador"].value_counts().head(10)
            st.bar_chart(arm_agg, height=200)
    else:
        emb_resumo = fetch("/api/embarques/resumo")
        if emb_resumo.get("total_embarques", 0) > 0:
            r = emb_resumo
            col_e1, col_e2, col_e3, col_e4 = st.columns(4)
            with col_e1: kpi_card("Embarques", f'{r["total_embarques"]:,}', "total")
            with col_e2: kpi_card("Peso", f'{r["peso_bruto_ton"]:,.1f}t', "bruto")
            with col_e3: kpi_card("TEUs", f'{r["total_teus"]:,.0f}', "total")
            with col_e4: kpi_card("Valor FOB", f'R$ {r.get("valor_fob_total",0)/1e6:.1f}M', "total")

            st.markdown("**🚢 Distribuição por Modal**")
            modais = r.get("por_modal", {})
            col_m1, col_m2 = st.columns([1, 2])
            with col_m1:
                for m, v in modais.items():
                    total_m = sum(modais.values()) or 1
                    pct = v / total_m * 100
                    st.markdown(f"""<div style="background:#14161e; padding:8px; border-radius:6px; margin:4px 0;"><span style="color:#888;">{'IMPORTAÇÃO' if m == 'importacao' else 'EXPORTAÇÃO'}</span> <span><span style="color:#00d4aa; font-weight:bold;">{v:,}</span> <span style="color:#555;">({pct:.1f}%)</span></span></div>""", unsafe_allow_html=True)
            with col_m2:
                vals = {"importação": modais.get("importacao", 0), "exportação": modais.get("exportacao", 0)}
                st.bar_chart(pd.DataFrame([{"modal": k, "qtd": v} for k, v in vals.items()]).set_index("modal"), height=200)

            meses = fetch("/api/embarques/por-mes")
            if meses and "erro" not in meses:
                df_meses = pd.DataFrame(meses)
                if not df_meses.empty:
                    st.markdown("**📈 Tendência Mensal**")
                    st.line_chart(df_meses.set_index("mes")[["quantidade", "peso_ton"]], height=200)
        else:
            st.info("Nenhum dado de embarques disponível.")

    st.markdown("---")
    st.subheader("📦 Tracking")

    track_stats = fetch("/api/tracking/stats")
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1: kpi_card("Total Trackings", str(track_stats.get("total", 0)), "registros")
    with col_t2: kpi_card("Armadores", str(track_stats.get("armadores", 0)), "únicos")
    with col_t3: kpi_card("Ativos (30d)", str(track_stats.get("ativos_30d", 0)), "containers")
    with col_t4: kpi_card("Concluídos", str(track_stats.get("concluidos", 0)), "entregues")
    if track_stats.get("nota"):
        st.caption(track_stats["nota"])

    st.markdown("---")
    st.subheader("🏆 Rankings")

    st.markdown("---")
    st.markdown("### 📍 Por Estado")
    estados = ["SP", "PR", "SC", "RS", "MT", "MS", "MG", "RJ", "BA", "PE", "CE", "AM", "ES", "GO", "DF"]
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        uf = st.selectbox("Selecione o estado", estados, key="rank_uf_estado")
    with col_u2:
        st.metric("UF", uf)

    ranking_data = fetch(f"/api/ranking/importacao?uf={uf}&limit=50")
    if "erro" not in ranking_data and ranking_data.get("ranking"):
        df_rank = pd.DataFrame(ranking_data["ranking"])
        st.markdown(f"**🏆 Top países - Importações em {uf}**")
        st.dataframe(df_rank[["posicao", "pais", "fob_usd", "score_estimado"]], use_container_width=True, height=400)

    st.markdown("---")
    st.markdown("### 🏭 Por Setor (CNAE)")
    cnae_map = {
        "46": "Comércio Atacadista", "47": "Comércio Varejista",
        "29": "Fabricação de Veículos", "20": "Químicos",
        "21": "Farmacêuticos", "26": "Equip. Eletrônicos", "28": "Máquinas",
    }
    cnae_opts = ["46", "47", "29", "20", "21", "26", "28"]
    cnae = st.selectbox(
        "Capítulo CNAE", cnae_opts,
        format_func=lambda x: f"{x} — {cnae_map.get(x, '')}",
        key="rank_cnae",
    )

    ncm_data = fetch(f"/api/comex/ncm/{cnae}")
    if "erro" not in ncm_data and ncm_data.get("por_pais"):
        st.markdown(f"**📦 NCM capítulo {cnae} — por país**")
        df_ncm = pd.DataFrame(ncm_data["por_pais"])
        if not df_ncm.empty:
            st.bar_chart(df_ncm.head(10).set_index("pais")["total_fob"] / 1e6, height=300)
            st.dataframe(df_ncm.head(10), use_container_width=True)

# ─── OPERAÇÕES ───────────────────────────────────────────────
elif "Operações" in pagina:
    st.title("📦 Operações")

    stats = fetch("/api/tracking/stats")

    col_k1, col_k2, col_k3, col_k4, col_k5, col_k6 = st.columns(6)
    with col_k1: kpi_card("Total", stats.get("total", 0), "containers")
    with col_k2: kpi_card("🚢 Embarcados", stats.get("embarcados", 0), "a aguardar")
    with col_k3: kpi_card("🔄 Em Trânsito", stats.get("em_transito", 0), "navegando")
    with col_k4: kpi_card("📋 Desembaraçando", stats.get("desembaracando", 0), "na alfândega")
    with col_k5: kpi_card("🔴 Atrasados", stats.get("atrasados", 0), "fora do prazo")
    with col_k6: kpi_card("🏷 Armadores", stats.get("total_armadores", 0), "em operação")

    if stats.get("nota"):
        st.info(stats["nota"])

    st.markdown("---")
    st.subheader("🚢 Rotas Marítimas")

    rotas_data = fetch("/api/tracking/rotas-completas")
    dados_arm = rotas_data.get("dados", [])
    armadores_lista = rotas_data.get("armadores", [])

    if dados_arm:
        col_s1, col_s2 = st.columns([1, 1])
        with col_s1:
            armador_filtro = st.selectbox("Armador", ["Todos"] + armadores_lista, key="schedule_armador")
        with col_s2:
            if armador_filtro != "Todos":
                arm_data = next((d for d in dados_arm if d["armador"] == armador_filtro), None)
                total_rotas = arm_data["total_rotas"] if arm_data else 0
            else:
                total_rotas = sum(d["total_rotas"] for d in dados_arm)
            st.metric("Rotas Ativas", total_rotas)

        import plotly.graph_objects as go
        CORES_ARM = ["#00d4aa", "#3b82f6", "#ef4444", "#f59e0b", "#8b5cf6"]

        if armador_filtro != "Todos":
            dados_filtrados = [d for d in dados_arm if d["armador"] == armador_filtro]
        else:
            dados_filtrados = dados_arm

        fig = go.Figure()
        arm_cores = {}
        for i, d in enumerate(dados_filtrados):
            arm_cores[d["armador"]] = CORES_ARM[i % len(CORES_ARM)]
            for rota in d["rotas"]:
                lats = []
                lons = []
                labels = []
                if rota.get("origem_lat") and rota.get("origem_lon"):
                    lats.append(rota["origem_lat"]); lons.append(rota["origem_lon"]); labels.append(rota["origem"])
                if rota.get("destino_lat") and rota.get("destino_lon"):
                    lats.append(rota["destino_lat"]); lons.append(rota["destino_lon"]); labels.append(rota["destino"])
                if len(lats) >= 2:
                    fig.add_trace(go.Scattermap(
                        lat=lats, lon=lons, mode="lines+markers",
                        line=dict(width=2, color=arm_cores[d["armador"]]),
                        marker=dict(size=10, color=arm_cores[d["armador"]]),
                        name=f"{d['armador']}: {rota['origem'][:10]} → {rota['destino'][:10]}",
                        text=labels, hovertemplate="<b>%{text}</b><extra></extra>",
                    ))

        fig.update_layout(
            map=dict(style="open-street-map", center=dict(lat=-15, lon=-50), zoom=3),
            margin=dict(t=0, b=0, l=0, r=0), height=500,
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#ccc"),
        )
        st.plotly_chart(fig, use_container_width=True)

        for d in dados_filtrados:
            with st.expander(f"🚢 {d['armador']} — {d['total_rotas']} rotas"):
                for rota in d["rotas"]:
                    st.markdown(f"""
                    <div style="background:#0f111a;border:1px solid #1e2030;border-radius:8px;padding:0.5rem 1rem;margin:0.3rem 0;">
                        <span style="font-weight:600;color:#00d4aa;">{rota['origem']}</span>
                        <span style="color:#555;"> → </span>
                        <span style="font-weight:600;color:#00d4aa;">{rota['destino']}</span>
                        <span style="color:#666;font-size:0.8rem;margin-left:0.5rem;">📏 {rota['distancia_km']:,.0f} km</span>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma rota disponível.")

    st.markdown("---")
    st.subheader("📋 Tracking NCM")
    col1, col2 = st.columns([2, 1])
    with col1:
        ncm = st.text_input("Código NCM", placeholder="Ex: 84, 87, 46120000", max_chars=10)
    with col2:
        if st.button("🔍 Buscar", type="primary", use_container_width=True):
            pass

    if ncm and len(ncm) >= 2:
        with st.spinner(f"Buscando dados do NCM {ncm}..."):
            dados = fetch(f"/api/comex/ncm/{ncm}")
            if "erro" not in dados and dados.get("por_pais"):
                col_a, col_b, col_c = st.columns(3)
                with col_a: kpi_card("Países", len(dados["por_pais"]), "parceiros")
                with col_b: kpi_card("UFs", len(dados["por_uf"]), "estados")
                total_fob = sum(p["total_fob"] for p in dados["por_pais"])
                with col_c: kpi_card("FOB Total", f"R$ {total_fob/1e6:.1f}M", "valor total")

                st.markdown("##### 🌍 Por País")
                df_pais = pd.DataFrame(dados["por_pais"])
                if not df_pais.empty:
                    st.bar_chart(df_pais.set_index("pais")["total_fob"], height=400)
                    st.dataframe(df_pais.style.format({"total_fob": "R$ {:,.2f}", "total_peso_kg": "{:,.0f} kg"}), use_container_width=True)

                st.markdown("##### 🇧🇷 Por UF")
                df_uf = pd.DataFrame(dados["por_uf"])
                if not df_uf.empty:
                    st.bar_chart(df_uf.set_index("uf")["total_fob"], height=400)
                    st.dataframe(df_uf.style.format({"total_fob": "R$ {:,.2f}", "total_peso_kg": "{:,.0f} kg"}), use_container_width=True)
            else:
                st.warning(f"Nenhum dado encontrado para NCM {ncm}. Tente um capítulo (ex: 84, 46, 87)")

    st.markdown("---")
    st.markdown("### 🔝 Top NCMs em volume")
    top_ncms = fetch("/api/comex/top-ncms?limit=10").get("ncms", [])
    if top_ncms:
        df_top = pd.DataFrame(top_ncms)
        st.dataframe(df_top.style.format({"total_fob": "R$ {:,.0f}"}), use_container_width=True)

        with st.expander("💡 Oportunidades — NCMs com alta concentração"):
            oport = fetch("/api/insights/oportunidades-ncm?limit=10")
            if "erro" not in oport and oport.get("oportunidades"):
                df_op = pd.DataFrame(oport["oportunidades"])
                st.markdown("NCMs com alto volume de importação")
                st.dataframe(df_op.style.format({"total_fob_usd": "US$ {:,.0f}"}), use_container_width=True)

# ─── GEO ───────────────────────────────────────────────────────────
elif "Geo" in pagina:
    st.title("🌍 Mapa Logístico Interativo")

    geo_stats = fetch("/api/crawlers/geo/stats")
    total_geo = geo_stats.get("municipios_enriquecidos", 0)

    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1: kpi_card("Municípios", f"{total_geo}", "enriquecidos")
    with col_g2: kpi_card("Dist. Média Porto", f'{geo_stats.get("distancia_porto_media", 0):.0f} km', "média geral")
    with col_g3: kpi_card("Dist. Média Aeroporto", f'{geo_stats.get("distancia_aeroporto_media", 0):.0f} km', "média geral")

    portos_data = fetch("/api/crawlers/geo/portos-aeroportos")
    PORTOS = portos_data.get("portos", {})
    AEROPORTOS = portos_data.get("aeroportos", {})

    if not PORTOS:
        st.info("Nenhum dado de portos disponível.")
        st.stop()

    import plotly.graph_objects as go

    fig = go.Figure()

    fig.add_trace(go.Scattermap(
        lat=[p["lat"] for p in PORTOS.values()],
        lon=[p["lon"] for p in PORTOS.values()],
        mode="markers+text",
        marker=dict(size=14, color="#2563eb", symbol="harbor"),
        text=list(PORTOS.keys()),
        textposition="top center",
        textfont=dict(size=8, color="#60a5fa"),
        name="Portos",
        hovertemplate="<b>%{text}</b><extra></extra>",
    ))

    fig.add_trace(go.Scattermap(
        lat=[a["lat"] for a in AEROPORTOS.values()],
        lon=[a["lon"] for a in AEROPORTOS.values()],
        mode="markers+text",
        marker=dict(size=12, color="#dc2626", symbol="airport"),
        text=list(AEROPORTOS.keys()),
        textposition="top center",
        textfont=dict(size=8, color="#ef4444"),
        name="Aeroportos",
        hovertemplate="<b>%{text}</b><extra></extra>",
    ))

    fig.update_layout(
        map=dict(style="open-street-map", center=dict(lat=-15, lon=-50), zoom=3),
        margin=dict(t=0, b=0, l=0, r=0), height=500,
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#ccc"),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🚢 Distâncias Marítimas")

    with st.expander("Ver todas as rotas mapeadas"):
        rotas_data = fetch("/api/crawlers/sea-routes/rotas")
        if rotas_data and rotas_data.get("rotas"):
            df_rotas = pd.DataFrame(rotas_data["rotas"])
            st.dataframe(df_rotas, use_container_width=True, height=400)

    col_sr1, col_sr2 = st.columns(2)
    with col_sr1:
        origem_rota = st.selectbox("Porto Origem", ["Shanghai", "Ningbo", "Shenzhen", "Hamburg", "Rotterdam", "Singapura", "Busan", "Houston"], key="sr_origem")
    with col_sr2:
        destino_rota = st.selectbox("Porto Destino", ["Santos", "Navegantes", "Paranaguá", "Rio de Janeiro", "Salvador", "Manaus", "Suape", "Itapoá"], key="sr_destino")

    if st.button("🔍 Calcular Rota", use_container_width=True):
        rota_info = fetch(f"/api/crawlers/sea-routes/distancia?origem={origem_rota}&destino={destino_rota}")
        if rota_info and "erro" not in rota_info:
            col_r1, col_r2, col_r3, col_r4 = st.columns(4)
            with col_r1: kpi_card("Distância", f"{rota_info.get('distancia_milhas',0):,.0f} milhas", f"{rota_info.get('distancia_km',0):,.0f} km")
            with col_r2: kpi_card("Tempo Estimado", f"{rota_info.get('tempo_viagem_dias',0)} dias", "viagem")
            with col_r3: kpi_card("Frete Estimado", f"US$ {rota_info.get('custo_frete_usd',0):,.0f}", "por TEU")
            with col_r4: kpi_card("Custo Total", f"US$ {rota_info.get('custo_total_usd',0):,.0f}", "frete + operação")
        else:
            st.warning("Rota não encontrada")

# ─── ADMIN ─────────────────────────────────────────────────────────
elif "Admin" in pagina:
    st.title("⚙️ Admin — Dados e Fontes")

    st.markdown("""
    <div style="background:#14161e; padding:1rem; border-radius:10px; border:1px solid #1e2030; margin-bottom:1rem;">
    <strong>Modo operacional:</strong> API em tempo real — sem banco de dados local.<br>
    Todos os dados são buscados diretamente de APIs públicas.<br>
    Cache em SQLite mantém respostas por até TTL configurado (evita rate limits).
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🔄 Calcular Scoring", use_container_width=True):
            cnpj = st.text_input("CNPJ para scoring", key="admin_scoring_cnpj")
            if cnpj:
                r = fetch(f"/api/scoring/calcular/{cnpj}")
                st.json(r)
                st.cache_data.clear()
    with col2:
        if st.button("🔔 Gerar Alertas", use_container_width=True):
            r = httpx.post(f"{API}/api/alertas/gerar", timeout=30)
            st.json(r.json())
    with col3:
        if st.button("🔄 Limpar Cache", use_container_width=True):
            try:
                httpx.get(f"{API}/api/cache/clear", timeout=10)
                st.success("Cache limpo")
            except:
                pass
    with col4:
        if st.button("🏥 Health Check", use_container_width=True):
            health = fetch("/api/health")
            st.json(health)

    st.markdown("---")
    st.subheader("📊 Status dos Dados")

    c1, c2, c3, c4, c5 = st.columns(5)
    health = fetch("/api/health")
    connectors = health.get("connectors", {})
    c1.metric("BrasilAPI", connectors.get("brasilapi", "?"))
    c2.metric("ComexStat", connectors.get("comexstat", "?"))
    c3.metric("IBGE", connectors.get("ibge", "?"))
    c4.metric("Nominatim", connectors.get("nominatim", "?"))
    c5.metric("Cache", health.get("cache", {}).get("valid", 0))

    comex_resumo = fetch("/api/comex/resumo")
    st.markdown("**📈 Dados de Comércio Exterior**")
    st.json(comex_resumo)

    st.markdown("---")
    st.subheader("📊 Alertas")
    alertas = fetch("/api/alertas/?limit=10")
    if alertas.get("alertas"):
        st.dataframe(pd.DataFrame(alertas["alertas"]), use_container_width=True)
    else:
        st.info("Nenhum alerta gerado. Clique em Gerar Alertas.")

    st.markdown("---")
    st.subheader("🔤 Classificação NCM")
    col_ncm1, col_ncm2 = st.columns([1, 2])
    with col_ncm1:
        ncm_input = st.text_input("Código NCM", placeholder="Ex: 84713000", key="ncm_class")
    with col_ncm2:
        if ncm_input and len(ncm_input) >= 2:
            ncm_info = fetch(f"/api/crawlers/ncm/classificar/{ncm_input}")
            if ncm_info:
                st.markdown(f"""
                <div style="background:#14161e;border:1px solid #1e2030;border-radius:10px;padding:0.8rem 1rem;">
                    <div style="color:#00d4aa;font-weight:600;">{ncm_info.get('ncm', '')}</div>
                    <div style="color:#888;font-size:0.8rem;">Capítulo: {ncm_info.get('descricao_capitulo', '')}</div>
                    <div style="color:#ccc;font-size:0.85rem;">{ncm_info.get('descricao_posicao', '')}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🌍 Indicadores Macroeconômicos")
    indicadores = fetch("/api/comex/indicadores")
    if indicadores:
        st.json(indicadores)
