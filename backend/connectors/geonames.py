from typing import Optional
from connectors.base import BaseConnector


class GeoNamesConnector(BaseConnector):
    name = "geonames"
    base_url = "http://api.api.exemplo.com/geonames"
    default_ttl = 2592000

    def __init__(self):
        super().__init__()
        self.username = "demo"

    async def fetch(self, query: dict) -> Optional[dict]:
        q = query.get("q", "")
        country = query.get("country", "BR")
        max_rows = query.get("limit", 10)

        params = {
            "q": q,
            "maxRows": max_rows,
            "username": self.username,
            "style": "FULL",
        }
        if country:
            params["country"] = country

        try:
            resp = await self.client.get(f"{self.base_url}/searchJSON", params=params)
            if resp.status_code == 200:
                data = resp.json()
                geonames = data.get("geonames", [])
                return {
                    "total": len(geonames),
                    "places": [
                        {
                            "name": g.get("name", ""),
                            "country": g.get("countryName", ""),
                            "admin1": g.get("adminName1", ""),
                            "lat": float(g.get("lat", 0)),
                            "lon": float(g.get("lng", 0)),
                            "population": int(g.get("population", 0)),
                            "timezone": g.get("timezone", {}).get("timeZoneId", ""),
                            "geoname_id": g.get("geonameId", 0),
                        }
                        for g in geonames
                    ],
                }
            return None
        except Exception:
            return None

    async def city_info(self, geoname_id: int) -> Optional[dict]:
        params = {"geonameId": geoname_id, "username": self.username, "style": "FULL"}
        try:
            resp = await self.client.get(f"{self.base_url}/getJSON", params=params)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "name": data.get("name", ""),
                    "country": data.get("countryName", ""),
                    "lat": float(data.get("lat", 0)),
                    "lon": float(data.get("lng", 0)),
                    "population": int(data.get("population", 0)),
                    "timezone": data.get("timezone", {}).get("timeZoneId", ""),
                    "elevation": data.get("elevation", 0),
                }
            return None
        except Exception:
            return None
