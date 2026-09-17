# Mock APIs — troque via .env para endpoints reais
from typing import Optional
from datetime import datetime, timedelta
from connectors.base import BaseConnector


class GDELTConnector(BaseConnector):
    name = "gdelt"
    base_url = "https://api.exemplo.com/gdelt/api/v2"
    default_ttl = 3600

    async def fetch(self, query: dict) -> Optional[dict]:
        topic = query.get("topic", "")
        mode = query.get("mode", "ArtList")
        timespan = query.get("timespan", "24h")
        maxrecords = query.get("limit", 20)

        params = {
            "mode": mode,
            "maxrecords": maxrecords,
            "format": "json",
            "timespan": timespan,
        }
        if topic:
            params["query"] = topic

        try:
            resp = await self.client.get(f"{self.base_url}/doc/{mode}", params=params)
            if resp.status_code == 200:
                data = resp.json()
                articles = data.get("articles", [])
                return {
                    "total": data.get("count", len(articles)),
                    "articles": [
                        {
                            "title": a.get("title", ""),
                            "url": a.get("url", ""),
                            "source": a.get("domain", ""),
                            "date": a.get("seendate", ""),
                            "language": a.get("language", ""),
                            "tone": a.get("tone", 0),
                        }
                        for a in articles[:15]
                    ],
                }
            return {"erro": "GDELT API indisponível", "total": 0, "articles": []}
        except Exception:
            return {"erro": "GDELT API indisponível", "total": 0, "articles": []}

    async def risco_geopolitico(self, pais: str = "Brazil") -> Optional[dict]:
        return await self.fetch({
            "topic": f'"{pais}"',
            "mode": "ArtList",
            "timespan": "7d",
            "limit": 10,
        })
