from fastapi import APIRouter, Query
from connectors.brasilapi import BrasilAPIConnector
from connectors.receitaws import ReceitaWSConnector
from connectors.nominatim import NominatimConnector
from app.scoring import ScoreEngine, ScoreImportacao, ScoreComercial, ScoreLogistico, ScoreInternacionalizacao, ScoreCompraImediata
from app.schemas import ScoreInput

router = APIRouter(prefix="/api/scoring", tags=["Scoring"])

STRATEGIES = ["importacao", "comercial", "logistico", "internacionalizacao", "compra_imediata"]


def _build_engine() -> ScoreEngine:
    engine = ScoreEngine()
    engine.registrar(ScoreImportacao())
    engine.registrar(ScoreComercial())
    engine.registrar(ScoreLogistico())
    engine.registrar(ScoreInternacionalizacao())
    engine.registrar(ScoreCompraImediata())
    return engine


def _normalize_empresa(data: dict, cnpj: str) -> dict:
    cnae = data.get("cnae_fiscal") or data.get("cnae_fiscal_descricao") or data.get("cnae", "") or ""
    if isinstance(cnae, int):
        cnae = str(cnae)
    situacao = data.get("descricao_situacao_cadastral") or data.get("situacao", "")
    if isinstance(situacao, int):
        situacao = str(situacao)
    tel = data.get("ddd_telefone_1") or data.get("telefone", "")
    return {
        "cnpj": data.get("cnpj", cnpj),
        "razao_social": data.get("razao_social") or data.get("nome", ""),
        "nome_fantasia": data.get("nome_fantasia") or data.get("fantasia", ""),
        "cnae_fiscal_principal": cnae,
        "capital_social": float(data.get("capital_social", 0) or 0),
        "porte": data.get("porte", ""),
        "situacao_cadastral": situacao,
        "municipio": data.get("municipio", ""),
        "uf": data.get("uf", ""),
        "telefone1": tel,
        "email1": data.get("email", ""),
        "website_url": data.get("site") or data.get("url", ""),
    }


async def _fetch_empresa_data(cnpj: str) -> dict | None:
    brasilapi = BrasilAPIConnector()
    try:
        data = await brasilapi.cached_fetch({"cnpj": cnpj})
        if data:
            return _normalize_empresa(data, cnpj)
    finally:
        await brasilapi.close()

    receitaws = ReceitaWSConnector()
    try:
        data = await receitaws.cached_fetch({"cnpj": cnpj})
        if data:
            return _normalize_empresa(data, cnpj)
    finally:
        await receitaws.close()
    return None


@router.get("/strategies")
def listar_strategies():
    return {"strategies": STRATEGIES}


@router.get("/{cnpj}")
@router.post("/calcular/{cnpj}")
async def calcular_empresa(cnpj: str):
    cnpj_norm = cnpj.replace(".", "").replace("/", "").replace("-", "")
    if len(cnpj_norm) != 14:
        return {"erro": "CNPJ inválido"}

    empresa = await _fetch_empresa_data(cnpj_norm)
    if not empresa:
        return {"erro": "Empresa não encontrada"}

    geo = None
    municipio = empresa.get("municipio", "")
    uf = empresa.get("uf", "")
    if municipio and uf:
        nom = NominatimConnector()
        try:
            geo_data = await nom.geocode_municipio(municipio, uf)
            if geo_data:
                from app.utils.geo import distancia_mais_proxima
                lat, lon = geo_data["lat"], geo_data["lon"]
                dist_porto, porto = distancia_mais_proxima(lat, lon, "portos")
                dist_aero, aero = distancia_mais_proxima(lat, lon, "aeroportos")
                geo = {
                    "lat": lat, "lon": lon,
                    "distancia_porto_km": round(dist_porto, 1),
                    "porto_mais_proximo": porto,
                    "distancia_aeroporto_km": round(dist_aero, 1),
                    "aeroporto_mais_proximo": aero,
                    "enriquecido": True,
                }
        finally:
            await nom.close()

    website = None
    website_url = empresa.get("website_url") or empresa.get("website") or empresa.get("url")
    if website_url:
        website = {"url": website_url, "termos_importacao": None, "e_importador": None}

    score_input = ScoreInput(
        empresa_id=0,
        razao_social=empresa.get("razao_social", ""),
        nome_fantasia=empresa.get("nome_fantasia", ""),
        cnae_principal=empresa.get("cnae_fiscal_principal", ""),
        capital_social=empresa.get("capital_social"),
        porte=empresa.get("porte", ""),
        situacao_cadastral=empresa.get("situacao_cadastral", ""),
        municipio=municipio,
        uf=uf,
        email=empresa.get("email1", ""),
        telefone=empresa.get("telefone1", ""),
        website_url=website_url,
    )

    engine = _build_engine()
    resultados = engine.calcular_todos(score_input)
    geral = engine.score_geral(resultados)

    return {
        "cnpj": cnpj_norm,
        "empresa": {
            "razao_social": empresa.get("razao_social", ""),
            "municipio": municipio,
            "uf": uf,
            "cnae": empresa.get("cnae_fiscal_principal", ""),
        },
        "geo": geo,
        "scores": [r.model_dump() for r in resultados],
        "score_geral": geral,
    }


@router.post("/batch")
async def calcular_batch(cnpjs: str = Query(..., description="CNPJs separados por vírgula")):
    cnpj_list = [c.strip().replace(".", "").replace("/", "").replace("-", "") for c in cnpjs.split(",")]
    cnpj_list = [c for c in cnpj_list if len(c) == 14][:20]

    resultados = []
    for cnpj in cnpj_list:
        try:
            r = await calcular_empresa(cnpj)
            resultados.append(r)
        except Exception as e:
            resultados.append({"cnpj": cnpj, "erro": str(e)})

    return {"total": len(cnpj_list), "processados": len(resultados), "resultados": resultados}
