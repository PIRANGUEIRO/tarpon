from fastapi import APIRouter, Query
from typing import Optional
from connectors.comexstat import ComexStatConnector
from connectors.un_comtrade import UNComtradeConnector
from connectors.world_bank import WorldBankConnector

router = APIRouter(prefix="/api/comex", tags=["Comércio Exterior"])


@router.get("/resumo")
async def resumo(uf: Optional[str] = Query(None), ano: int = Query(2025)):
    conn = ComexStatConnector()
    try:
        imp = await conn.cached_fetch({"flow": "import", "ano_inicio": ano, "ano_fim": ano, "uf": uf})
        exp = await conn.cached_fetch({"flow": "export", "ano_inicio": ano, "ano_fim": ano, "uf": uf})
        imp_ok = imp and not imp.get("erro")
        exp_ok = exp and not exp.get("erro")
        total_fob = (imp.get("total_fob_usd", 0) if imp_ok else 0) + (exp.get("total_fob_usd", 0) if exp_ok else 0)
        records = (imp.get("records", []) if imp_ok else []) + (exp.get("records", []) if exp_ok else [])
        ncms = set(r.get("ncm", "") for r in records if r.get("ncm"))
        paises = set(r.get("country", "") for r in records if r.get("country"))
        return {
            "total_fob": total_fob,
            "total_ncms": len(ncms),
            "total_paises": len(paises),
            "total_ufs": 27,
            "total_registros": len(records),
        }
    finally:
        await conn.close()


@router.get("/ufs")
async def comex_ufs(ano: int = Query(2025)):
    conn = ComexStatConnector()
    try:
        imp = await conn.cached_fetch({"flow": "import", "ano_inicio": ano, "ano_fim": ano})
        exp = await conn.cached_fetch({"flow": "export", "ano_inicio": ano, "ano_fim": ano})
        imp_ok = imp and not imp.get("erro")
        exp_ok = exp and not exp.get("erro")
        uf_agg = {}
        for flow_data in ([imp.get("records", [])] if imp_ok else []) + ([exp.get("records", [])] if exp_ok else []):
            pass
        all_records = (imp.get("records", []) if imp_ok else []) + (exp.get("records", []) if exp_ok else [])
        uf_stats = {}
        for r in all_records:
            uf = r.get("state", "")
            if not uf:
                continue
            if uf not in uf_stats:
                uf_stats[uf] = {"uf": uf, "ncms": set(), "total_fob": 0, "qtd": 0}
            uf_stats[uf]["ncms"].add(r.get("ncm", ""))
            uf_stats[uf]["total_fob"] += int(r.get("metricFOB", 0) or 0)
            uf_stats[uf]["qtd"] += 1
        result = []
        for uf, info in sorted(uf_stats.items(), key=lambda x: x[1]["total_fob"], reverse=True):
            result.append({
                "uf": uf,
                "ncms": len(info["ncms"]),
                "total_fob": info["total_fob"],
                "qtd": info["qtd"],
            })
        return {"ufs": result, "fonte": "comexstat"}
    finally:
        await conn.close()


@router.get("/top-ncms")
async def top_ncms(ano: int = Query(2025), limit: int = Query(10)):
    conn = ComexStatConnector()
    try:
        imp = await conn.cached_fetch({"flow": "import", "ano_inicio": ano, "ano_fim": ano})
        if not imp or imp.get("erro"):
            return {"ncms": []}
        ncm_agg = {}
        for r in imp.get("records", []):
            ncm = r.get("ncm", "")
            if not ncm:
                continue
            if ncm not in ncm_agg:
                ncm_agg[ncm] = {"ncm": ncm, "ufs": set(), "paises": set(), "total_fob": 0}
            ncm_agg[ncm]["ufs"].add(r.get("state", ""))
            ncm_agg[ncm]["paises"].add(r.get("country", ""))
            ncm_agg[ncm]["total_fob"] += int(r.get("metricFOB", 0) or 0)
        result = []
        for ncm, info in sorted(ncm_agg.items(), key=lambda x: x[1]["total_fob"], reverse=True)[:limit]:
            result.append({
                "ncm": ncm,
                "ufs": len(info["ufs"]),
                "paises": len(info["paises"]),
                "total_fob": info["total_fob"],
            })
        return {"ncms": result, "fonte": "comexstat"}
    finally:
        await conn.close()


@router.get("/busca")
async def busca(
    ncm: Optional[str] = Query(None),
    municipio: Optional[str] = Query(None),
    uf: Optional[str] = Query(None),
    limit: int = Query(100),
):
    conn = ComexStatConnector()
    try:
        data = await conn.cached_fetch({
            "flow": "import",
            "ano_inicio": 2025,
            "ano_fim": 2025,
            "uf": uf,
            "ncm": ncm,
        })
        if not data or data.get("erro"):
            return {"total": 0, "resultados": []}
        records = data.get("records", [])
        resultados = []
        for r in records[:limit]:
            resultados.append({
                "ncm": r.get("ncm", ""),
                "pais": r.get("country", ""),
                "valor_fob": int(r.get("metricFOB", 0) or 0),
            })
        return {"total": len(resultados), "resultados": resultados}
    finally:
        await conn.close()


@router.get("/uf/{uf}")
async def comex_por_uf(uf: str, ano: int = 2025):
    conn = ComexStatConnector()
    try:
        data = await conn.cached_fetch({
            "flow": "export",
            "uf": uf.upper(),
            "ano_inicio": ano,
            "ano_fim": ano,
        })
        return {"uf": uf.upper(), "ano": ano, "fonte": "comexstat", "dados": data}
    finally:
        await conn.close()


@router.get("/uf/{uf}/resumo")
async def resumo_uf(uf: str, ano: int = 2025):
    conn = ComexStatConnector()
    try:
        data = await conn.resumo_uf(uf.upper(), ano)
        return data
    finally:
        await conn.close()


@router.get("/paises")
async def comex_paises(
    periodo: Optional[str] = Query("2024"),
    limit: int = Query(20),
):
    conn = UNComtradeConnector()
    try:
        data = await conn.cached_fetch({"period": periodo, "limit": limit})
        return {"periodo": periodo, "fonte": "un_comtrade", "dados": data}
    finally:
        await conn.close()


@router.get("/indicadores")
async def indicadores_brasil():
    conn = WorldBankConnector()
    try:
        data = await conn.indicadores_brasil()
        return {"fonte": "world_bank", "indicadores": data}
    finally:
        await conn.close()


@router.get("/ncm/{ncm}")
async def detalhes_ncm(ncm: str, ano: int = Query(2025)):
    conn = ComexStatConnector()
    try:
        data = await conn.cached_fetch({
            "flow": "import",
            "ncm": ncm,
            "ano_inicio": ano,
            "ano_fim": ano,
        })
        if not data or data.get("erro"):
            return {"ncm": ncm, "por_pais": [], "por_uf": [], "erro": data.get("erro", "Sem dados")}
        records = data.get("records", [])
        pais_agg = {}
        uf_agg = {}
        for r in records:
            pais = r.get("country", "")
            uf = r.get("state", "")
            fob = int(r.get("metricFOB", 0) or 0)
            kg = int(r.get("metricKG", 0) or 0)
            if pais:
                if pais not in pais_agg:
                    pais_agg[pais] = {"pais": pais, "total_fob": 0, "total_peso_kg": 0}
                pais_agg[pais]["total_fob"] += fob
                pais_agg[pais]["total_peso_kg"] += kg
            if uf:
                if uf not in uf_agg:
                    uf_agg[uf] = {"uf": uf, "total_fob": 0, "total_peso_kg": 0}
                uf_agg[uf]["total_fob"] += fob
                uf_agg[uf]["total_peso_kg"] += kg
        por_pais = sorted(pais_agg.values(), key=lambda x: x["total_fob"], reverse=True)
        por_uf = sorted(uf_agg.values(), key=lambda x: x["total_fob"], reverse=True)
        return {"ncm": ncm, "por_pais": por_pais, "por_uf": por_uf}
    finally:
        await conn.close()


@router.get("/pais/{pais}")
async def comex_pais(pais: str):
    conn = UNComtradeConnector()
    try:
        data = await conn.cached_fetch({"reporter": pais, "limit": 30})
        return {"pais": pais, "fonte": "un_comtrade", "dados": data}
    finally:
        await conn.close()


@router.get("/macro/brasil")
async def macro_brasil():
    wb = WorldBankConnector()
    un = UNComtradeConnector()
    try:
        world_bank = await wb.indicadores_brasil()
        comtrade = await un.cached_fetch({"reporter": "Brazil", "limit": 20})
        return {"world_bank": world_bank, "un_comtrade": comtrade}
    finally:
        await wb.close()
        await un.close()
