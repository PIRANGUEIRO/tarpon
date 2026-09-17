# Mock APIs — troque via .env para endpoints reais
from typing import Optional
from connectors.base import BaseConnector


class OpenCorporatesConnector(BaseConnector):
    name = "opencorporates"
    base_url = "https://api.exemplo.com/opencorporates/v0.4"
    default_ttl = 86400

    async def fetch(self, query: dict) -> Optional[dict]:
        q = query.get("q", "")
        jurisdiction = query.get("jurisdiction", "")
        page = query.get("page", 1)

        params = {"q": q, "page": page, "per_page": 10}
        if jurisdiction:
            params["jurisdiction_code"] = jurisdiction

        try:
            resp = await self.client.get(f"{self.base_url}/companies/search", params=params)
            if resp.status_code == 200:
                data = resp.json()
                companies = data.get("results", {}).get("companies", [])
                return {
                    "total": data.get("results", {}).get("total", 0),
                    "companies": [
                        {
                            "name": c.get("company", {}).get("name", ""),
                            "number": c.get("company", {}).get("company_number", ""),
                            "jurisdiction": c.get("company", {}).get("jurisdiction_code", ""),
                            "status": c.get("company", {}).get("status", ""),
                            "incorporation_date": c.get("company", {}).get("incorporation_date", ""),
                            "address": c.get("company", {}).get("registered_address_in_full", ""),
                        }
                        for c in companies
                    ],
                }
            if resp.status_code == 401:
                return {"erro": "API key necessária. Cadastre-se em opencorporates.com", "total": 0, "companies": []}
            return None
        except Exception:
            return None
