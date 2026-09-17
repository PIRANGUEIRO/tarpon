from fastapi import APIRouter, Query
from connectors.ibge import IBGESIDRAConnector
from connectors.nominatim import NominatimConnector
from connectors.viacep import ViaCEPConnector
from connectors.bacen import BACENConnector
from app.geo_data import PORTOS, AEROPORTOS

router = APIRouter(prefix="/api/crawlers", tags=["Crawlers & Dados"])


@router.get("/geo/portos")
def portos():
    return {"portos": PORTOS, "total": len(PORTOS)}


@router.get("/geo/aeroportos")
def aeroportos():
    return {"aeroportos": AEROPORTOS, "total": len(AEROPORTOS)}


@router.get("/geo/portos-aeroportos")
def portos_aeroportos():
    return {"portos": PORTOS, "aeroportos": AEROPORTOS}


@router.get("/geo/stats")
def geo_stats():
    return {
        "municipios_enriquecidos": 0,
        "distancia_porto_media": 0,
        "distancia_aeroporto_media": 0,
        "nota": "Dados de geolocalização requerem busca por endereço via Nominatim",
    }


@router.get("/geo/{empresa_id}")
async def geo_empresa(empresa_id: int):
    return {
        "enriquecido": False,
        "nota": "Geolocalização requer busca por CNPJ primeiro para obter endereço",
    }


@router.get("/geo/{empresa_id}/todas-distancias")
async def todas_distancias(empresa_id: int):
    from app.utils.geo import distancia_portos, distancia_aeroportos
    return {
        "enriquecido": False,
        "distancias_portos": {},
        "distancias_aeroportos": {},
        "nota": "Requer geolocalização da empresa primeiro",
    }


@router.get("/ibge/pib/{cod_ibge}")
async def ibge_pib(cod_ibge: str, ano: int = 2021):
    conn = IBGESIDRAConnector()
    try:
        data = await conn.pib_municipal(cod_ibge, ano)
        return {"cod_ibge": cod_ibge, "ano": ano, "fonte": "ibge_sidra", "dados": data}
    finally:
        await conn.close()


@router.get("/ibge/populacao/{cod_ibge}")
async def ibge_populacao(cod_ibge: str, ano: int = 2021):
    conn = IBGESIDRAConnector()
    try:
        data = await conn.populacao(cod_ibge, ano)
        return {"cod_ibge": cod_ibge, "ano": ano, "fonte": "ibge_sidra", "dados": data}
    finally:
        await conn.close()


@router.get("/geo/geocode")
async def geocode(q: str = Query(..., description="Endereço para geocodificar")):
    conn = NominatimConnector()
    try:
        data = await conn.cached_fetch({"q": q})
        return {"query": q, "fonte": "nominatim", "resultado": data}
    finally:
        await conn.close()


@router.get("/geo/municipio/{municipio}")
async def geocode_municipio(municipio: str, uf: str = Query(...)):
    conn = NominatimConnector()
    try:
        data = await conn.geocode_municipio(municipio, uf)
        return {"municipio": municipio, "uf": uf, "fonte": "nominatim", "resultado": data}
    finally:
        await conn.close()


@router.get("/cep/{cep}")
async def cep_lookup(cep: str):
    conn = ViaCEPConnector()
    try:
        data = await conn.cached_fetch({"cep": cep})
        return {"cep": cep, "fonte": "viacep", "resultado": data}
    finally:
        await conn.close()


@router.get("/bacen/ptax")
async def ptax():
    conn = BACENConnector()
    try:
        data = await conn.ptax()
        return {"fonte": "bacen", "ptax": data}
    finally:
        await conn.close()


@router.get("/bacen/{serie}")
async def bacen_serie(serie: str):
    conn = BACENConnector()
    try:
        data = await conn.cached_fetch({"serie": serie})
        return {"serie": serie, "fonte": "bacen", "dados": data}
    finally:
        await conn.close()


@router.get("/ncm/classificar/{ncm}")
def classificar_ncm(ncm: str):
    from app.utils.ncm import classificar_produto
    return classificar_produto(ncm)


@router.get("/ncm/capitulos")
def listar_capitulos():
    from app.utils.ncm import ncm_todos_capitulos
    return {"capitulos": ncm_todos_capitulos()}


@router.get("/sea-routes/rotas")
def listar_rotas():
    from app.utils.sea_routes import todas_rotas
    return {"rotas": todas_rotas(), "total": len(todas_rotas())}


@router.get("/sea-routes/distancia")
def calcular_distancia(origem: str, destino: str):
    from app.utils.sea_routes import estimar_custo_frete
    return estimar_custo_frete(origem, destino)


@router.get("/sea-routes/porto/{porto}")
def rotas_porto(porto: str):
    from app.utils.sea_routes import rotas_disponiveis
    return {"porto": porto, "rotas": rotas_disponiveis(porto)}


@router.get("/website/stats")
def website_stats():
    return {"total_sites": 0, "com_termos_importacao": 0, "nota": "Scraping de websites requer implementação"}


@router.post("/run/{crawler}")
def run_crawler(crawler: str):
    return {"status": "ok", "mensagem": f"Crawler '{crawler}' — modo API sem banco de dados", "stdout": "", "stderr": ""}
