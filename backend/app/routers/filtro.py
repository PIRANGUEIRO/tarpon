from fastapi import APIRouter, Query
from typing import Optional
from connectors.comexstat import ComexStatConnector

router = APIRouter(prefix="/api/filtro", tags=["Filtro Premium"])


@router.get("/valores")
async def valores_filtro():
    conn = ComexStatConnector()
    try:
        data = await conn.cached_fetch({"flow": "import", "ano_inicio": 2025, "ano_fim": 2025})
        paises = []
        ncms = []
        if data and not data.get("erro"):
            for r in data.get("records", []):
                pais = r.get("country", "")
                ncm = r.get("ncm", "")
                if pais and pais not in paises:
                    paises.append(pais)
                if ncm and ncm not in ncms:
                    ncms.append(ncm)

        return {
            "empresas": [],
            "importadores": [],
            "paises": sorted(paises)[:50],
            "portos_origem": [],
            "portos_destino": [],
            "agentes_carga": [],
            "armadores": [],
            "ufs": ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA",
                     "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN",
                     "RO", "RR", "RS", "SC", "SE", "SP", "TO"],
            "cidades": [],
            "tipos_carga": ["geral", "perigosa", "perecivel", "refrigerada"],
            "tipos_container": ["20gp", "40gp", "40hc", "45hc", "20rf", "40rf"],
            "pagamentos": ["COLLECT", "PREPAID"],
            "incoterms": ["FOB", "CIF", "EXW", "CFR"],
            "anos": [2025, 2024, 2023],
            "ncms": sorted(ncms)[:30],
        }
    finally:
        await conn.close()


@router.get("/buscar")
async def buscar(
    uf: Optional[str] = Query(None),
    ncm: Optional[str] = Query(None),
    pais: Optional[str] = Query(None),
    flow: str = Query("import"),
    ano: int = Query(2025),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
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
            return {"total": 0, "resultados": [], "erro": data.get("erro", "Sem dados")}

        records = data.get("records", [])
        if pais:
            records = [r for r in records if pais.upper() in (r.get("country", "") or "").upper()]

        resultados = []
        for r in records[offset:offset + limit]:
            fob = int(r.get("metricFOB", 0) or 0)
            kg = int(r.get("metricKG", 0) or 0)
            resultados.append({
                "id": len(resultados) + 1,
                "ncm": r.get("ncm", ""),
                "pais_origem": r.get("country", "") if flow == "import" else "BRASIL",
                "pais_destino": "BRASIL" if flow == "import" else r.get("country", ""),
                "valor_fob": fob,
                "peso_kg": kg,
                "teus": max(1, kg // 14000) if kg else 0,
                "uf": uf or "",
                "modal": "importacao" if flow == "import" else "exportacao",
                "armador": "",
                "containers": 0,
                "empresa_id": 0,
                "ncm_posicao": r.get("ncm", "")[:6],
                "ncm_capitulo": r.get("ncm", "")[:2],
            })

        return {"total": len(records), "resultados": resultados, "flow": flow, "fonte": "comexstat"}
    finally:
        await conn.close()
