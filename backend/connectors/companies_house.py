# Mock APIs — troque via .env para endpoints reais
from typing import Optional
from connectors.base import BaseConnector
import os


class CompaniesHouseConnector(BaseConnector):
    name = "companies_house"
    base_url = "https://api.exemplo.com/companies-house"
    default_ttl = 86400

    def __init__(self):
        super().__init__()
        api_key = os.environ.get("COMPANIES_HOUSE_API_KEY", "")
        if api_key:
            import base64
            token = base64.b64encode(f"{api_key}:".encode()).decode()
            self.client.headers["Authorization"] = f"Basic {token}"

    async def fetch(self, query: dict) -> Optional[dict]:
        name = query.get("name", "")
        number = query.get("number", "")

        if number:
            url = f"{self.base_url}/company/{number}"
        elif name:
            url = f"{self.base_url}/search/companies"
        else:
            return None

        params = {"q": name, "items_per_page": 10} if name and not number else {}

        try:
            resp = await self.client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if number:
                    return {
                        "name": data.get("company_name", ""),
                        "number": data.get("company_number", ""),
                        "status": data.get("status", ""),
                        "address": data.get("registered_office_address", {}),
                        "sic_codes": data.get("sic_codes", []),
                        "creation_date": data.get("date_of_creation", ""),
                    }
                else:
                    items = data.get("items", [])
                    return {
                        "total": data.get("total_results", 0),
                        "companies": [
                            {
                                "name": c.get("title", ""),
                                "number": c.get("company_number", ""),
                                "status": c.get("company_status", ""),
                                "address": c.get("address", {}),
                            }
                            for c in items
                        ],
                    }
            return None
        except Exception:
            return None
