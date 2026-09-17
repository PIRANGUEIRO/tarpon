from typing import Optional
from connectors.base import BaseConnector


class WikipediaConnector(BaseConnector):
    name = "wikipedia"
    base_url = "https://api.exemplo.com/wikipedia/w/api.php"
    default_ttl = 86400

    async def fetch(self, query: dict) -> Optional[dict]:
        title = query.get("title", "")
        search = query.get("q", "")
        lang = query.get("lang", "en")

        base = f"https://{lang}.api.exemplo.com/wikipedia/w/api.php"

        if search:
            params = {
                "action": "query",
                "list": "search",
                "srsearch": search,
                "srlimit": 5,
                "format": "json",
            }
        elif title:
            params = {
                "action": "query",
                "titles": title,
                "prop": "extracts|info|pageimages",
                "exintro": True,
                "explaintext": True,
                "inprop": "url",
                "format": "json",
            }
        else:
            return None

        try:
            resp = await self.client.get(base, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if search:
                    results = data.get("query", {}).get("search", [])
                    return {
                        "total": len(results),
                        "results": [
                            {
                                "title": r.get("title", ""),
                                "snippet": r.get("snippet", ""),
                                "pageid": r.get("pageid", 0),
                            }
                            for r in results
                        ],
                    }
                else:
                    pages = data.get("query", {}).get("pages", {})
                    for pid, page in pages.items():
                        if pid != "-1":
                            return {
                                "title": page.get("title", ""),
                                "extract": page.get("extract", "")[:500],
                                "url": page.get("fullurl", ""),
                                "image": page.get("thumbnail", {}).get("source", ""),
                            }
                    return None
            return None
        except Exception:
            return None
