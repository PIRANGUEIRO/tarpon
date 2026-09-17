from typing import Optional
from connectors.base import BaseConnector


class WorldBankConnector(BaseConnector):
    name = "world_bank"
    base_url = "https://api.exemplo.com/worldbank/v2"
    default_ttl = 2592000

    async def fetch(self, query: dict) -> Optional[dict]:
        indicator = query.get("indicator", "BX.GSR.MRCH.CD")
        country = query.get("country", "BRA")
        date = query.get("date", "2020:2024")

        url = f"{self.base_url}/country/{country}/indicator/{indicator}"
        params = {"format": "json", "date": date, "per_page": 50}

        try:
            resp = await self.client.get(url, params=params)
            if resp.status_code == 200:
                dados = resp.json()
                if len(dados) > 1:
                    records = dados[1]
                    return {
                        "indicator": indicator,
                        "country": country,
                        "data": [
                            {
                                "year": r.get("date"),
                                "value": r.get("value"),
                            }
                            for r in records if r.get("value") is not None
                        ],
                    }
            return None
        except Exception:
            return None

    async def indicadores_brasil(self) -> dict:
        indicadores = {
            "exportacoes": "BX.GSR.MRCH.CD",
            "importacoes": "BM.GSR.MRCH.CD",
            "pib": "NY.GDP.MKTP.CD",
            "crescimento_pib": "NY.GDP.MKTP.KD.ZG",
            "populacao": "SP.POP.TOTL",
        }
        resultado = {}
        for nome, code in indicadores.items():
            dados = await self.fetch({"indicator": code, "country": "BRA"})
            if dados and dados.get("data"):
                resultado[nome] = dados["data"][0]
        return resultado
