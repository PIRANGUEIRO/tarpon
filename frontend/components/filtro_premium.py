"""Filtro premium lateral scrollável com todos os campos do projeto."""
import streamlit as st
import httpx
from datetime import datetime

API = "http://localhost:8000"


@st.cache_data(ttl=60)
def fetch_valores():
    try:
        r = httpx.get(f"{API}/api/filtro/valores", timeout=15)
        if r.status_code == 200:
            return r.json()
        return {}
    except Exception:
        return {}


def _mock_fallback(valores: dict, chave: str, fallback: list):
    data = valores.get(chave, [])
    if data and len(data) > 0:
        return data
    return fallback


def render_filtro_premium():
    st.sidebar.markdown("### 🔍 Filtro Premium")
    st.sidebar.caption("Role para baixo para ver todos os filtros")
    valores = fetch_valores()

    with st.sidebar:
        with st.expander("🏢 Empresa", expanded=True):
            empresas = valores.get("empresas", [])
            emp_opts = {e["id"]: f"{e['razao_social'][:50]} — {e['municipio']}/{e['uf']}" for e in empresas}
            emp_ids = list(emp_opts.keys())
            if emp_ids:
                st.multiselect("Empresa", options=emp_ids, format_func=lambda x: emp_opts.get(x, ""), key="fp_empresa", placeholder="Selecione empresas")
            else:
                st.selectbox("Empresa", [""], key="fp_empresa")
            st.text_input("CNPJ", placeholder="Digite o CNPJ", max_chars=18, key="fp_cnpj")

        with st.expander("📅 Período", expanded=True):
            anos_raw = valores.get("anos", [])
            anos = []
            for a in anos_raw:
                try:
                    if isinstance(a, (int, float)):
                        anos.append(int(a))
                    elif isinstance(a, str) and a.isdigit():
                        anos.append(int(a))
                    elif hasattr(a, 'year'):
                        anos.append(a.year)
                except (ValueError, TypeError):
                    pass
            if not anos:
                anos = list(range(datetime.now().year, 2019, -1))
            else:
                anos = sorted(set(anos), reverse=True)
            st.multiselect("Ano", options=anos, key="fp_ano", placeholder="Selecione anos")

            meses = [
                (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
                (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
                (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro"),
            ]
            st.multiselect("Mês", options=[m[0] for m in meses], format_func=lambda x: dict(meses)[x], key="fp_mes", placeholder="Selecione meses")

        with st.expander("🚢 Embarque", expanded=False):
            importadores = _mock_fallback(valores, "importadores", ["BRADESCO", "MERCANTIL", "VALE", "PETROBRAS", "GERDAU", "WEG", "MARCOPOLO", "EMBRAER", "JBS", "BRF"])
            st.multiselect("Importador", options=importadores, key="fp_importador", placeholder="Selecione importadores")
            st.multiselect("Exportador", options=importadores, key="fp_exportador", placeholder="Selecione exportadores")

            paises = _mock_fallback(valores, "paises", ["China", "EUA", "Alemanha", "Argentina", "Coreia do Sul", "Índia", "Itália", "Japão", "França", "Chile"])
            st.multiselect("País de Origem", options=paises, key="fp_pais_origem", placeholder="Selecione países")

            portos_origem = _mock_fallback(valores, "portos_origem", ["Santos", "Paranaguá", "Itajaí", "Rio de Janeiro", "Salvador", "Manaus", "Rio Grande", "Vitória", "Suape", "Fortaleza"])
            portos_destino = _mock_fallback(valores, "portos_destino", ["Roterdã", "Xangai", "Cingapura", "Hamburgo", "Long Beach", "Buenos Aires", "Valparaíso", "Antuérpia", "Barcelona", "Hong Kong"])
            st.multiselect("Porto de Origem", options=portos_origem, key="fp_porto_origem", placeholder="Selecione portos")
            st.multiselect("Porto de Destino", options=portos_destino, key="fp_porto_destino", placeholder="Selecione portos")

        with st.expander("💳 Pagamento", expanded=False):
            st.multiselect("Tipo de Pagamento", options=["COLLECT", "PREPAID"], key="fp_pagamento")
            st.multiselect("Incoterm", options=["FOB", "CIF", "EXW", "CFR"], key="fp_incoterm")

        with st.expander("📦 Produto", expanded=False):
            st.text_input("Posição NCM (4 dígitos)", placeholder="Ex: 4612", max_chars=4, key="fp_ncm_pos")
            st.text_input("Capítulo NCM (2 dígitos)", placeholder="Ex: 46", max_chars=2, key="fp_ncm_cap")

        with st.expander("🚛 Logística", expanded=False):
            armadores = _mock_fallback(valores, "armadores", ["MSC", "Maersk", "CMA CGM", "COSCO", "Hapag-Lloyd", "ONE", "Evergreen", "ZIM", "Yang Ming", "HMM"])
            st.multiselect("Armador", options=armadores, key="fp_armador", placeholder="Selecione armadores")
            agentes = _mock_fallback(valores, "agentes_carga", ["DHL Global", "Kuehne+Nagel", "DB Schenker", "Panalpina", "CEVA Logistics", "Hellmann", "Bolloré", "Geodis", "DSV", "Expeditors"])
            st.multiselect("Agente de Carga", options=agentes, key="fp_agente_carga", placeholder="Selecione agentes")
            st.multiselect("Agente Internacional", options=agentes, key="fp_agente_int", placeholder="Selecione agentes")
            st.text_input("Notify", placeholder="Nome do notify", key="fp_notify")
            st.text_input("NVOCC", placeholder="Código NVOCC", key="fp_nvocc")
            st.text_input("Armazém de Destino", placeholder="Nome do armazém", key="fp_armazem")

        with st.expander("📊 Localização", expanded=False):
            ufs = _mock_fallback(valores, "ufs", ["SP", "PR", "SC", "RS", "MT", "MS", "MG", "RJ", "BA", "PE", "CE", "AM", "ES", "GO", "DF", "PA", "MA", "RN", "PB", "AL", "SE", "PI", "TO", "RO", "AC", "AP", "RR"])
            st.multiselect("UF do Importador", options=ufs, key="fp_uf_imp")
            cidades = _mock_fallback(valores, "cidades", ["São Paulo", "Curitiba", "Joinville", "Porto Alegre", "Belo Horizonte", "Rio de Janeiro", "Salvador", "Fortaleza", "Manaus", "Brasília", "Campinas", "Guarulhos", "Santos", "Blumenau", "Caxias do Sul"])
            st.multiselect("Cidade do Importador", options=cidades, key="fp_cidade_imp", placeholder="Selecione cidades")

        with st.expander("📦 Carga", expanded=False):
            tipos_carga = _mock_fallback(valores, "tipos_carga", ["DRY", "REEFER", "TANK", "OPENTOP", "FLAT RACK", "HIGH CUBE"])
            st.multiselect("Tipo de Carga", options=tipos_carga, key="fp_tipo_carga")
            tipos_container = _mock_fallback(valores, "tipos_container", ["DRY", "REEFER", "TANK", "OPENTOP", "HIGH CUBE"])
            st.multiselect("Tipo de Container", options=tipos_container, key="fp_tipo_container")

        st.markdown("---")
        if st.button("🔄 Limpar Filtros", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("fp_"):
                    if isinstance(st.session_state[k], list):
                        st.session_state[k] = []
                    elif isinstance(st.session_state[k], str):
                        st.session_state[k] = ""
                    elif isinstance(st.session_state[k], (int, float)):
                        st.session_state[k] = 0
            st.rerun()

    return {
        "empresa_ids": st.session_state.get("fp_empresa", []),
        "cnpj": st.session_state.get("fp_cnpj", ""),
        "anos": st.session_state.get("fp_ano", []),
        "meses": st.session_state.get("fp_mes", []),
        "importador": st.session_state.get("fp_importador", []),
        "exportador": st.session_state.get("fp_exportador", []),
        "pais_origem": st.session_state.get("fp_pais_origem", []),
        "porto_origem": st.session_state.get("fp_porto_origem", []),
        "porto_destino": st.session_state.get("fp_porto_destino", []),
        "pagamento": st.session_state.get("fp_pagamento", []),
        "incoterm": st.session_state.get("fp_incoterm", []),
        "ncm_posicao": st.session_state.get("fp_ncm_pos", ""),
        "ncm_capitulo": st.session_state.get("fp_ncm_cap", ""),
        "armador": st.session_state.get("fp_armador", []),
        "agente_carga": st.session_state.get("fp_agente_carga", []),
        "agente_internacional": st.session_state.get("fp_agente_int", []),
        "notify": st.session_state.get("fp_notify", ""),
        "nvocc": st.session_state.get("fp_nvocc", ""),
        "uf_imp": st.session_state.get("fp_uf_imp", []),
        "cidade_imp": st.session_state.get("fp_cidade_imp", []),
        "armazem_destino": st.session_state.get("fp_armazem", ""),
        "tipo_carga": st.session_state.get("fp_tipo_carga", []),
        "tipo_container": st.session_state.get("fp_tipo_container", []),
    }
