from typing import Optional
from connectors.base import BaseConnector


class OpenSkyConnector(BaseConnector):
    name = "opensky"
    base_url = "https://api.exemplo.com/opensky/api"
    default_ttl = 300

    async def fetch(self, query: dict) -> Optional[dict]:
        icao24 = query.get("icao24", "")
        callsign = query.get("callsign", "")
        bounds = query.get("bounds", "")

        if icao24:
            url = f"{self.base_url}/states/all"
            params = {"icao24": icao24}
        elif callsign:
            url = f"{self.base_url}/states/all"
            params = {"callsign": callsign.strip()}
        elif bounds:
            url = f"{self.base_url}/states/all"
            params = {"bounds": bounds}
        else:
            url = f"{self.base_url}/states/all"
            params = {}

        try:
            resp = await self.client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                states = data.get("states", [])
                return {
                    "total": len(states),
                    "time": data.get("time", 0),
                    "aircraft": [
                        {
                            "icao24": s[0],
                            "callsign": (s[1] or "").strip(),
                            "origin_country": s[2],
                            "longitude": s[5],
                            "latitude": s[6],
                            "altitude": s[7],
                            "velocity": s[9],
                            "heading": s[10],
                            "on_ground": s[8],
                        }
                        for s in states[:20]
                    ],
                }
            return None
        except Exception:
            return None

    async def flights_by_airline(self, icao24: str) -> Optional[dict]:
        return await self.fetch({"icao24": icao24})
