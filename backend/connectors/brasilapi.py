from typing import Optional
from connectors.base import BaseConnector


class BrasilAPIConnector(BaseConnector):
    name = "brasilapi"
    base_url = "https://api.exemplo.com/brasilapi/api/cnpj/v1"
    default_ttl = 86400

    async def fetch(self, query: dict) -> Optional[dict]:
        cnpj = query.get("cnpj", "").replace(".", "").replace("/", "").replace("-", "")
        if not cnpj or len(cnpj) != 14:
            return None
        try:
            resp = await self.client.get(f"{self.base_url}/{cnpj}")
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception:
            return None
