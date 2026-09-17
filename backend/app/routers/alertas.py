from fastapi import APIRouter, Query
from connectors.comexstat import ComexStatConnector
from connectors.brasilapi import BrasilAPIConnector
import time

router = APIRouter(prefix="/api/alertas", tags=["Alertas"])

_alertas_cache: list[dict] = []
_ultimo_gerado: float = 0


async def _gerar_alertas_reais() -> list[dict]:
    global _alertas_cache, _ultimo_gerado
    alertas = []

    conn = ComexStatConnector()
    try:
        imp = await conn.cached_fetch({"flow": "import", "ano_inicio": 2025, "ano_fim": 2025})
        exp = await conn.cached_fetch({"flow": "export", "ano_inicio": 2025, "ano_fim": 2025})

        if imp and not imp.get("erro"):
            top_imp = imp.get("top_parceiros", [])[:5]
            for p in top_imp:
                fob = p.get("fob", 0)
                if fob > 100_000_000:
                    alertas.append({
                        "id": len(alertas) + 1,
                        "tipo": "oportunidade_importacao",
                        "severidade": "alta",
                        "titulo": f"Alto volume de importação de {p.get('pais', '?')}",
                        "descricao": f"USD {fob / 1e6:.1f}M em importações do(a) {p.get('pais', '?')}. Potencial parceiro comercial.",
                        "pais": p.get("pais", ""),
                        "valor_fob": fob,
                        "lido": 0,
                        "data": "2025-01-01",
                    })

        if exp and not exp.get("erro"):
            top_exp = exp.get("top_parceiros", [])[:5]
            for p in top_exp:
                fob = p.get("fob", 0)
                if fob > 50_000_000:
                    alertas.append({
                        "id": len(alertas) + 1,
                        "tipo": "destino_exportacao",
                        "severidade": "media",
                        "titulo": f"Exportação significativa para {p.get('pais', '?')}",
                        "descricao": f"USD {fob / 1e6:.1f}M em exportações para {p.get('pais', '?')}. Mercado em expansão.",
                        "pais": p.get("pais", ""),
                        "valor_fob": fob,
                        "lido": 0,
                        "data": "2025-01-01",
                    })

        alertas.append({
            "id": len(alertas) + 1,
            "tipo": "sistema",
            "severidade": "info",
            "titulo": "Sistema operando via APIs em tempo real",
            "descricao": "Todos os dados são buscados diretamente das APIs públicas. Cache ativo para evitar rate limits.",
            "lido": 0,
            "data": "2025-01-01",
        })

    finally:
        await conn.close()

    _alertas_cache = alertas
    _ultimo_gerado = time.time()
    return alertas


@router.get("/")
async def listar_alertas(
    tipo: str | None = None,
    severidade: str | None = None,
    lido: int | None = None,
    limit: int = 50,
):
    global _alertas_cache
    if not _alertas_cache:
        await _gerar_alertas_reais()

    result = _alertas_cache
    if tipo:
        result = [a for a in result if a["tipo"] == tipo]
    if severidade:
        result = [a for a in result if a["severidade"] == severidade]
    if lido is not None:
        result = [a for a in result if a["lido"] == lido]

    return {"total": len(result[:limit]), "alertas": result[:limit]}


@router.get("/stats")
async def stats_alertas():
    global _alertas_cache
    if not _alertas_cache:
        await _gerar_alertas_reais()

    por_tipo = {}
    nao_lidos = 0
    for a in _alertas_cache:
        t = a["tipo"]
        por_tipo[t] = por_tipo.get(t, 0) + 1
        if not a["lido"]:
            nao_lidos += 1

    return {
        "total": len(_alertas_cache),
        "nao_lidos": nao_lidos,
        "por_tipo": por_tipo,
    }


@router.post("/{alerta_id}/lido")
def marcar_lido(alerta_id: int):
    global _alertas_cache
    for a in _alertas_cache:
        if a["id"] == alerta_id:
            a["lido"] = 1
            return {"ok": True, "alerta_id": alerta_id}
    return {"erro": "Alerta não encontrado"}


@router.post("/gerar")
async def gerar_alertas():
    alertas = await _gerar_alertas_reais()
    return {"ok": True, "novos_alertas": len(alertas)}
