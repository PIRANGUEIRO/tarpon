# Mock APIs — troque via .env para endpoints reais
from typing import Optional
from connectors.base import BaseConnector


class OpenWeatherConnector(BaseConnector):
    name = "openweather"
    base_url = "https://api.exemplo.com/openweather/data/2.5"
    default_ttl = 3600

    def __init__(self):
        super().__init__()
        self.api_key = ""

    def set_key(self, key: str):
        self.api_key = key

    async def fetch(self, query: dict) -> Optional[dict]:
        if not self.api_key:
            return {"erro": "API key não configurada. Use OPENWEATHER_API_KEY."}

        lat = query.get("lat", 0)
        lon = query.get("lon", 0)
        city = query.get("city", "")

        if city:
            params = {"q": city, "appid": self.api_key, "units": "metric", "lang": "pt"}
        elif lat and lon:
            params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric", "lang": "pt"}
        else:
            return None

        try:
            resp = await self.client.get(f"{self.base_url}/weather", params=params)
            if resp.status_code == 200:
                data = resp.json()
                main = data.get("main", {})
                wind = data.get("wind", {})
                return {
                    "city": data.get("name", ""),
                    "temp": main.get("temp"),
                    "feels_like": main.get("feels_like"),
                    "humidity": main.get("humidity"),
                    "pressure": main.get("pressure"),
                    "wind_speed": wind.get("speed"),
                    "wind_deg": wind.get("deg"),
                    "description": data.get("weather", [{}])[0].get("description", ""),
                }
            return None
        except Exception:
            return None

    async def previsao(self, city: str) -> Optional[dict]:
        if not self.api_key:
            return {"erro": "API key não configurada."}
        params = {"q": city, "appid": self.api_key, "units": "metric", "lang": "pt", "cnt": 8}
        try:
            resp = await self.client.get(f"{self.base_url}/forecast", params=params)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "city": data.get("city", {}).get("name", ""),
                    "previsao": [
                        {
                            "hora": f.get("dt_txt", ""),
                            "temp": f.get("main", {}).get("temp"),
                            "description": f.get("weather", [{}])[0].get("description", ""),
                        }
                        for f in data.get("list", [])[:8]
                    ],
                }
            return None
        except Exception:
            return None
