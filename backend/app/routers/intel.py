import os
from fastapi import APIRouter, Query
from connectors.opensky import OpenSkyConnector
from connectors.fleetmon import FleetMonConnector
from connectors.geonames import GeoNamesConnector
from connectors.wikipedia import WikipediaConnector
from connectors.wikidata import WikidataConnector
from connectors.gdelt import GDELTConnector
from connectors.openweather import OpenWeatherConnector

router = APIRouter(prefix="/api/intel", tags=["Inteligência"])


@router.get("/aereo/voos")
async def voos_em_tempo_real(
    icao24: str = Query(None, description="Código ICAO24 da aeronave"),
    callsign: str = Query(None, description="Callsign do voo"),
    bounds: str = Query(None, description="lat1,lon1,lat2,lon2"),
):
    conn = OpenSkyConnector()
    try:
        if icao24:
            data = await conn.cached_fetch({"icao24": icao24}, ttl=60)
        elif callsign:
            data = await conn.cached_fetch({"callsign": callsign}, ttl=60)
        elif bounds:
            data = await conn.cached_fetch({"bounds": bounds}, ttl=60)
        else:
            data = await conn.cached_fetch({}, ttl=60)
        return {"fonte": "opensky", "dados": data}
    finally:
        await conn.close()


@router.get("/aereo/{icao24}")
async def aeronave(icao24: str):
    conn = OpenSkyConnector()
    try:
        data = await conn.cached_fetch({"icao24": icao24}, ttl=60)
        return {"icao24": icao24, "fonte": "opensky", "dados": data}
    finally:
        await conn.close()


@router.get("/maritimo/busca")
async def busca_navio(
    nome: str = Query(None),
    imo: str = Query(None),
    mmsi: str = Query(None),
):
    conn = FleetMonConnector()
    try:
        query = {}
        if nome:
            query["vessel_name"] = nome
        if imo:
            query["imo"] = imo
        if mmsi:
            query["mmsi"] = mmsi
        data = await conn.cached_fetch(query, ttl=600)
        return {"fonte": "fleetmon", "dados": data}
    finally:
        await conn.close()


@router.get("/geonames/busca")
async def busca_cidade(
    q: str = Query(..., description="Nome da cidade"),
    pais: str = Query("BR", description="Código do país"),
    limit: int = Query(5),
):
    conn = GeoNamesConnector()
    try:
        data = await conn.cached_fetch({"q": q, "country": pais, "limit": limit})
        return {"fonte": "geonames", "dados": data}
    finally:
        await conn.close()


@router.get("/geonames/{geoname_id}")
async def detalhes_cidade(geoname_id: int):
    conn = GeoNamesConnector()
    try:
        data = await conn.city_info(geoname_id)
        return {"geoname_id": geoname_id, "fonte": "geonames", "dados": data}
    finally:
        await conn.close()


@router.get("/wikipedia")
async def busca_wikipedia(
    q: str = Query(..., description="Termo de busca"),
    lang: str = Query("en"),
):
    conn = WikipediaConnector()
    try:
        data = await conn.cached_fetch({"q": q, "lang": lang})
        return {"fonte": "wikipedia", "dados": data}
    finally:
        await conn.close()


@router.get("/wikipedia/{title}")
async def artigo_wikipedia(title: str, lang: str = Query("en")):
    conn = WikipediaConnector()
    try:
        data = await conn.cached_fetch({"title": title, "lang": lang})
        return {"fonte": "wikipedia", "dados": data}
    finally:
        await conn.close()


@router.get("/wikidata")
async def busca_wikidata(q: str = Query(..., description="Termo de busca")):
    conn = WikidataConnector()
    try:
        data = await conn.cached_fetch({"q": q})
        return {"fonte": "wikidata", "dados": data}
    finally:
        await conn.close()


@router.get("/wikidata/{qid}")
async def detalhes_wikidata(qid: str):
    conn = WikidataConnector()
    try:
        data = await conn.cached_fetch({"qid": qid})
        return {"qid": qid, "fonte": "wikidata", "dados": data}
    finally:
        await conn.close()


@router.get("/geopolitica/{pais}")
async def risco_geopolitico(pais: str):
    conn = GDELTConnector()
    try:
        data = await conn.risco_geopolitico(pais)
        return {"pais": pais, "fonte": "gdelt", "dados": data}
    finally:
        await conn.close()


@router.get("/clima/{cidade}")
async def clima(cidade: str):
    conn = OpenWeatherConnector()
    conn.set_key(os.environ.get("OPENWEATHER_API_KEY", ""))
    try:
        data = await conn.fetch({"city": cidade})
        return {"cidade": cidade, "fonte": "openweather", "dados": data}
    finally:
        await conn.close()


@router.get("/clima/{cidade}/previsao")
async def previsao_clima(cidade: str):
    conn = OpenWeatherConnector()
    conn.set_key(os.environ.get("OPENWEATHER_API_KEY", ""))
    try:
        data = await conn.previsao(cidade)
        return {"cidade": cidade, "fonte": "openweather", "dados": data}
    finally:
        await conn.close()
