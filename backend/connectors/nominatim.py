# Mock APIs — troque via .env para endpoints reais
from typing import Optional
from connectors.base import BaseConnector


class NominatimConnector(BaseConnector):
    name = "nominatim"
    base_url = "https://api.exemplo.com/nominatim/search"
    default_ttl = 2592000

    async def fetch(self, query: dict) -> Optional[dict]:
        q = query.get("q", "")
        if not q:
            return None
        params = {
            "q": q,
            "format": "json",
            "limit": 1,
            "countrycodes": "br",
        }
        try:
            resp = await self.client.get(self.base_url, params=params)
            if resp.status_code == 200:
                dados = resp.json()
                if dados:
                    r = dados[0]
                    return {
                        "lat": float(r.get("lat", 0)),
                        "lon": float(r.get("lon", 0)),
                        "display_name": r.get("display_name", ""),
                        "type": r.get("type", ""),
                        "importance": r.get("importance", 0),
                    }
            return None
        except Exception:
            return None

    async def geocode_municipio(self, municipio: str, uf: str) -> Optional[dict]:
        return await self.fetch({"q": f"{municipio}, {uf}, Brasil"})
