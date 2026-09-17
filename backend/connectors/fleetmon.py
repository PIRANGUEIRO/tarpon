import os
from typing import Optional
from connectors.base import BaseConnector


class FleetMonConnector(BaseConnector):
    name = "fleetmon"
    base_url = "https://api.exemplo.com/fleetmon"
    default_ttl = 600

    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get("FLEETMON_API_KEY", "")

    async def fetch(self, query: dict) -> Optional[dict]:
        if not self.api_key:
            return {
                "erro": "FLEETMON_API_KEY não configurada. Obtenha em fleetmon.com",
                "total": 0,
                "vessels": [],
            }

        vessel_name = query.get("vessel_name", "")
        imo = query.get("imo", "")
        mmsi = query.get("mmsi", "")

        if imo:
            url = f"{self.base_url}/vessel/imo/{imo}/"
        elif mmsi:
            url = f"{self.base_url}/vessel/mmsi/{mmsi}/"
        elif vessel_name:
            url = f"{self.base_url}/vessel/search/"
        else:
            return None

        headers = {"Authorization": f"Token {self.api_key}"}
        params = {}
        if vessel_name:
            params["name"] = vessel_name

        try:
            resp = await self.client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if vessel_name and "results" in data:
                    vessels = data["results"]
                    return {
                        "total": len(vessels),
                        "vessels": [
                            {
                                "name": v.get("name", ""),
                                "imo": v.get("imo", ""),
                                "mmsi": v.get("mmsi", ""),
                                "type": v.get("vessel_type", ""),
                                "flag": v.get("flag", ""),
                                "length": v.get("length", 0),
                                "beam": v.get("beam", 0),
                            }
                            for v in vessels[:10]
                        ],
                    }
                elif isinstance(data, dict) and "name" in data:
                    return {
                        "name": data.get("name", ""),
                        "imo": data.get("imo", ""),
                        "mmsi": data.get("mmsi", ""),
                        "type": data.get("vessel_type", ""),
                        "flag": data.get("flag", ""),
                        "lat": data.get("latitude"),
                        "lon": data.get("longitude"),
                        "speed": data.get("speed", 0),
                        "course": data.get("course", 0),
                        "destination": data.get("destination", ""),
                        "eta": data.get("eta", ""),
                    }
            return None
        except Exception:
            return None
