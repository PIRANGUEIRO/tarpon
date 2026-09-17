from fastapi import APIRouter, Query
from connectors.comexstat import ComexStatConnector

router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.get("/importadores-por-uf")
async def importadores_por_uf(ano: int = Query(2025)):
    conn = ComexStatConnector()
    try:
        imp = await conn.cached_fetch({"flow": "import", "ano_inicio": ano, "ano_fim": ano})
        exp = await conn.cached_fetch({"flow": "export", "ano_inicio": ano, "ano_fim": ano})

        ufs = {}
        for flow_data, tipo in [(imp, "importacao"), (exp, "exportacao")]:
            if not flow_data or flow_data.get("erro"):
                continue
            for r in flow_data.get("records", []):
                pais = r.get("country", "")
                fob = int(r.get("metricFOB", 0) or 0)
                if pais not in ufs:
                    ufs[pais] = {"pais": pais, "importacao_fob": 0, "exportacao_fob": 0, "registros": 0}
                ufs[pais][f"{tipo}_fob"] += fob
                ufs[pais]["registros"] += 1

        resultado = sorted(ufs.values(), key=lambda x: x["importacao_fob"] + x["exportacao_fob"], reverse=True)
        return {"ufs": resultado[:30], "fonte": "comexstat"}
    finally:
        await conn.close()


@router.get("/oportunidades-ncm")
async def oportunidades_ncm(ano: int = Query(2025), limit: int = 30):
    conn = ComexStatConnector()
    try:
        imp = await conn.cached_fetch({"flow": "import", "ano_inicio": ano, "ano_fim": ano})
        if not imp or imp.get("erro"):
            return {"oportunidades": [], "erro": imp.get("erro", "Sem dados")}

        ncm_agg = {}
        for r in imp.get("records", []):
            ncm = r.get("ncm", "")
            if not ncm:
                continue
            fob = int(r.get("metricFOB", 0) or 0)
            kg = int(r.get("metricKG", 0) or 0)
            pais = r.get("country", "")
            if ncm not in ncm_agg:
                ncm_agg[ncm] = {"ncm": ncm, "total_fob": 0, "total_kg": 0, "paises": set(), "qtd_registros": 0}
            ncm_agg[ncm]["total_fob"] += fob
            ncm_agg[ncm]["total_kg"] += kg
            ncm_agg[ncm]["paises"].add(pais)
            ncm_agg[ncm]["qtd_registros"] += 1

        oportunidades = []
        for ncm, info in sorted(ncm_agg.items(), key=lambda x: x[1]["total_fob"], reverse=True)[:limit]:
            oportunidades.append({
                "ncm": ncm,
                "total_fob_usd": info["total_fob"],
                "total_kg": info["total_kg"],
                "paises_fornecedor": list(info["paises"]),
                "qtd_fornecedores": len(info["paises"]),
                "qtd_registros": info["qtd_registros"],
                "oportunidade": "alta" if info["total_fob"] > 100_000_000 else "media" if info["total_fob"] > 10_000_000 else "baixa",
            })

        return {"oportunidades": oportunidades, "total_ncms": len(ncm_agg), "fonte": "comexstat"}
    finally:
        await conn.close()


@router.get("/empresas-potenciais/{uf}")
async def empresas_potenciais(uf: str, ano: int = Query(2025), limit: int = 20):
    conn = ComexStatConnector()
    try:
        data = await conn.cached_fetch({"flow": "import", "ano_inicio": ano, "ano_fim": ano, "uf": uf.upper()})
        if not data or data.get("erro"):
            return {"uf": uf.upper(), "principais_ncms": [], "empresas": [], "erro": data.get("erro", "Sem dados")}

        ncm_agg = {}
        for r in data.get("records", []):
            ncm = r.get("ncm", "")
            fob = int(r.get("metricFOB", 0) or 0)
            if ncm not in ncm_agg:
                ncm_agg[ncm] = {"ncm": ncm, "total_fob": 0, "paises": set()}
            ncm_agg[ncm]["total_fob"] += fob
            ncm_agg[ncm]["paises"].add(r.get("country", ""))

        principais = sorted(ncm_agg.values(), key=lambda x: x["total_fob"], reverse=True)[:limit]
        for p in principais:
            p["paises"] = list(p["paises"])

        return {
            "uf": uf.upper(),
            "principais_ncms": principais,
            "empresas": [],
            "nota": "Dados de empresas requerem busca por CNPJ via BrasilAPI/ReceitaWS",
            "fonte": "comexstat",
        }
    finally:
        await conn.close()


@router.get("/comparativo-uf")
async def comparativo_uf(uf_a: str, uf_b: str, ano: int = Query(2025)):
    conn = ComexStatConnector()
    try:
        data_a = await conn.cached_fetch({"flow": "import", "ano_inicio": ano, "ano_fim": ano, "uf": uf_a.upper()})
        data_b = await conn.cached_fetch({"flow": "import", "ano_inicio": ano, "ano_fim": ano, "uf": uf_b.upper()})

        def get_stats(data):
            if not data or data.get("erro"):
                return {"ncms": 0, "paises": 0, "total_fob": 0, "total_peso_kg": 0}
            records = data.get("records", [])
            ncms = set()
            paises = set()
            total_fob = 0
            total_kg = 0
            for r in records:
                ncms.add(r.get("ncm", ""))
                paises.add(r.get("country", ""))
                total_fob += int(r.get("metricFOB", 0) or 0)
                total_kg += int(r.get("metricKG", 0) or 0)
            return {
                "ncms": len(ncms),
                "paises": len(paises),
                "total_fob": total_fob,
                "total_peso_kg": total_kg,
            }

        return {
            uf_a.upper(): get_stats(data_a),
            uf_b.upper(): get_stats(data_b),
            "fonte": "comexstat",
        }
    finally:
        await conn.close()
