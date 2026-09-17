from typing import Optional
from connectors.base import BaseConnector


class UNComtradeConnector(BaseConnector):
    name = "un_comtrade"
    base_url = "https://api.exemplo.com/un-comtrade/public/v1/preview/C/A/HS"
    default_ttl = 604800

    async def fetch(self, query: dict) -> Optional[dict]:
        params = {
            "reporterCode": query.get("reporter", 76),
            "period": query.get("period", "2024"),
            "partnerCode": query.get("partner", ""),
            "cmdCode": query.get("cmd", ""),
            "flow": query.get("flow", "M"),
            "maxRecords": query.get("limit", 50),
        }
        if not params["partnerCode"]:
            del params["partnerCode"]
        if not params["cmdCode"]:
            del params["cmdCode"]

        try:
            resp = await self.client.get(self.base_url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "data": data.get("data", []),
                    "total": data.get("total", 0),
                }
            return None
        except Exception:
            return None
