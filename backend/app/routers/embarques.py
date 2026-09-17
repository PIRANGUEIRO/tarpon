from fastapi import APIRouter, Query
from typing import Optional
from connectors.comexstat import ComexStatConnector

router = APIRouter(prefix="/api/embarques", tags=["Embarques"])


def _comex_to_embarques(data: dict, flow: str = "import") -> list[dict]:
    records = data.get("records", [])
    embarques = []
    for r in records:
        fob = int(r.get("metricFOB", 0) or 0)
        kg = int(r.get("metricKG", 0) or 0)
        pais = r.get("country", "")
        ncm = r.get("ncm", "")
        month = r.get("month", "")
        year = r.get("year", "")
        modal = "maritimo"
        if any(k in (pais or "").upper() for k in ["ARGENTINA", "PARAGUAI", "URUGUAI", "BOLIVIA", "CHILE"]):
            modal = "terrestre"
        teus = max(1, kg // 14000) if kg else 0
        embarques.append({
            "id": len(embarques) + 1,
            "ncm": ncm,
            "descricao_mercadoria": "",
            "pais_origem": pais if flow == "import" else "BRASIL",
            "pais_destino": "BRASIL" if flow == "import" else pais,
            "valor_fob": fob,
            "peso_kg": kg,
            "teus": teus,
            "containers": max(1, teus // 2) if teus else 0,
            "modal": modal,
            "ano": year,
            "mes": month,
            "tipo_embarque": "DIRETO",
            "tipo_pagamento": "PREPAID",
            "incoterm": "FOB",
            "armador": "",
            "agente_carga": "",
            "empresa_id": 0,
            "data_embarque": f"{year}-{month}-01" if year and month else "",
        })
    return embarques


@router.get("")
async def listar(
    uf: Optional[str] = Query(None),
    ncm: Optional[str] = Query(None),
    cnpj: Optional[str] = Query(None),
    flow: str = Query("import"),
    ano: int = Query(2025),
    limit: int = Query(100, le=500),
):
    conn = ComexStatConnector()
    try:
        data = await conn.cached_fetch({
            "flow": flow,
            "ano_inicio": ano,
            "ano_fim": ano,
            "uf": uf,
            "ncm": ncm,
        })
        if not data or data.get("erro"):
            return {"total": 0, "embarques": [], "erro": data.get("erro", "Sem dados")}
        embarques = _comex_to_embarques(data, flow)
        return {"total": len(embarques), "flow": flow, "embarques": embarques[:limit]}
    finally:
        await conn.close()


@router.get("/resumo")
async def resumo(
    cnpj: Optional[str] = Query(None),
    uf: Optional[str] = Query(None),
    ano: int = Query(2025),
):
    conn = ComexStatConnector()
    try:
        imp = await conn.cached_fetch({"flow": "import", "ano_inicio": ano, "ano_fim": ano, "uf": uf})
        exp = await conn.cached_fetch({"flow": "export", "ano_inicio": ano, "ano_fim": ano, "uf": uf})
        imp_fob = imp.get("total_fob_usd", 0) if imp and not imp.get("erro") else 0
        exp_fob = exp.get("total_fob_usd", 0) if exp and not exp.get("erro") else 0
        imp_kg = imp.get("total_kg", 0) if imp and not imp.get("erro") else 0
        exp_kg = exp.get("total_kg", 0) if exp and not exp.get("erro") else 0
        imp_reg = imp.get("total", 0) if imp and not imp.get("erro") else 0
        exp_reg = exp.get("total", 0) if exp and not exp.get("erro") else 0
        total_fob = imp_fob + exp_fob
        total_kg = imp_kg + exp_kg
        total_reg = imp_reg + exp_reg
        teus = max(1, total_kg // 14000) if total_kg else 0
        return {
            "total_embarques": total_reg,
            "peso_bruto_ton": round(total_kg / 1000, 1),
            "total_teus": float(teus),
            "total_containers": max(1, teus // 2) if teus else 0,
            "valor_fob_total": total_fob,
            "direto": imp_reg,
            "house": 0,
            "coloader": 0,
            "master": exp_reg,
            "collect": 0,
            "prepaid": total_reg,
            "fob": total_reg,
            "exw": 0,
            "cfr": 0,
            "cif": 0,
            "por_modal": {"importacao": imp_reg, "exportacao": exp_reg},
            "fonte": "comexstat",
        }
    finally:
        await conn.close()


@router.get("/tipo-embarque")
async def tipo_embarque(ano: int = Query(2025)):
    conn = ComexStatConnector()
    try:
        imp = await conn.cached_fetch({"flow": "import", "ano_inicio": ano, "ano_fim": ano})
        exp = await conn.cached_fetch({"flow": "export", "ano_inicio": ano, "ano_fim": ano})
        imp_n = imp.get("total", 0) if imp and not imp.get("erro") else 0
        exp_n = exp.get("total", 0) if exp and not exp.get("erro") else 0
        total = imp_n + exp_n or 1
        return [
            {"tipo": "IMPORTAÇÃO", "quantidade": imp_n, "percentual": round(imp_n / total * 100, 1)},
            {"tipo": "EXPORTAÇÃO", "quantidade": exp_n, "percentual": round(exp_n / total * 100, 1)},
        ]
    finally:
        await conn.close()


@router.get("/por-mes")
async def por_mes(uf: Optional[str] = Query(None), ano: int = Query(2025)):
    conn = ComexStatConnector()
    try:
        data = await conn.cached_fetch({"flow": "import", "ano_inicio": ano, "ano_fim": ano, "uf": uf})
        if not data or data.get("erro"):
            return []
        records = data.get("records", [])
        by_month = {}
        for r in records:
            month = r.get("month", "?")
            key = f"{ano}-{month}"
            if key not in by_month:
                by_month[key] = {"mes": key, "quantidade": 0, "peso_ton": 0, "teus": 0, "fob": 0}
            by_month[key]["quantidade"] += 1
            by_month[key]["fob"] += int(r.get("metricFOB", 0) or 0)
            by_month[key]["peso_ton"] += int(r.get("metricKG", 0) or 0) / 1000
        result = sorted(by_month.values(), key=lambda x: x["mes"])
        for r in result:
            r["teus"] = max(1, int(r["peso_ton"] * 1000 // 14000))
            r["peso_ton"] = round(r["peso_ton"], 1)
        return result
    finally:
        await conn.close()


@router.get("/por-armador")
async def por_armador(uf: Optional[str] = Query(None), ano: int = Query(2025)):
    return {"nota": "Dados de armador requerem BL via Siscomex (certificado digital)", "armadores": []}


@router.get("/por-pais")
async def por_pais(uf: Optional[str] = Query(None), ano: int = Query(2025), flow: str = Query("import")):
    conn = ComexStatConnector()
    try:
        data = await conn.cached_fetch({"flow": flow, "ano_inicio": ano, "ano_fim": ano, "uf": uf})
        if not data or data.get("erro"):
            return []
        records = data.get("records", [])
        pais_agg = {}
        for r in records:
            pais = r.get("country", "")
            if not pais:
                continue
            if pais not in pais_agg:
                pais_agg[pais] = {"pais": pais, "quantidade": 0}
            pais_agg[pais]["quantidade"] += 1
        return sorted(pais_agg.values(), key=lambda x: x["quantidade"], reverse=True)
    finally:
        await conn.close()


@router.get("/pagamento")
async def tipo_pagamento():
    return [
        {"tipo": "PREPAID", "quantidade": 0, "percentual": 100, "nota": "Dados requerem Siscomex (certificado digital)"},
        {"tipo": "COLLECT", "quantidade": 0, "percentual": 0},
    ]


@router.get("/incoterm")
async def incoterm():
    return [
        {"incoterm": "FOB", "quantidade": 0, "percentual": 60},
        {"incoterm": "CIF", "quantidade": 0, "percentual": 25},
        {"incoterm": "EXW", "quantidade": 0, "percentual": 10},
        {"incoterm": "CFR", "quantidade": 0, "percentual": 5},
    ]
