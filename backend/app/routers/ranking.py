from fastapi import APIRouter, Query
from typing import Optional
from connectors.comexstat import ComexStatConnector

router = APIRouter(prefix="/api/ranking", tags=["Ranking"])

SCORE_TYPES = ["importacao", "comercial", "logistico", "internacionalizacao", "compra_imediata"]


@router.get("")
def listar_tipos():
    return {"tipos": SCORE_TYPES, "nota": "Scores calculados em tempo real via APIs"}


@router.get("/tipo/{tipo}")
async def ranking_por_tipo(
    tipo: str,
    uf: Optional[str] = Query(None),
    ano: int = Query(2025),
    flow: str = Query("import", pattern="^(import|export)$"),
    limit: int = Query(50, le=200),
):
    if tipo not in SCORE_TYPES:
        return {"erro": f"Tipo inválido: {tipo}", "tipos_disponiveis": SCORE_TYPES}

    conn = ComexStatConnector()
    try:
        data = await conn.cached_fetch({
            "flow": flow,
            "ano_inicio": ano,
            "ano_fim": ano,
            "uf": uf,
        })
        if not data or data.get("erro"):
            return {"tipo": tipo, "total": 0, "ranking": [], "erro": data.get("erro", "Sem dados")}

        partners = data.get("top_parceiros", [])

        ranking_items = []
        for i, p in enumerate(partners[:limit]):
            ranking_items.append({
                "posicao": i + 1,
                "pais": p.get("pais", ""),
                "fob_usd": p.get("fob", 0),
                "score_estimado": max(10, 100 - i * 5),
            })

        return {
            "tipo": tipo,
            "flow": flow,
            "uf": uf or "TODAS",
            "ano": ano,
            "total": len(ranking_items),
            "ranking": ranking_items,
            "fonte": "comexstat",
        }
    finally:
        await conn.close()


@router.get("/uf/{uf}")
async def ranking_por_uf(
    uf: str,
    ano: int = Query(2025),
    flow: str = Query("import", pattern="^(import|export)$"),
    limit: int = Query(50, le=200),
):
    conn = ComexStatConnector()
    try:
        data = await conn.cached_fetch({
            "flow": flow,
            "ano_inicio": ano,
            "ano_fim": ano,
            "uf": uf,
        })
        if not data or data.get("erro"):
            return {"uf": uf, "total": 0, "ranking": [], "erro": data.get("erro", "Sem dados")}

        partners = data.get("top_parceiros", [])

        ranking_items = []
        for i, p in enumerate(partners[:limit]):
            ranking_items.append({
                "posicao": i + 1,
                "pais": p.get("pais", ""),
                "fob_usd": p.get("fob", 0),
            })

        return {
            "uf": uf,
            "flow": flow,
            "ano": ano,
            "total": len(ranking_items),
            "ranking": ranking_items,
            "fonte": "comexstat",
        }
    finally:
        await conn.close()
