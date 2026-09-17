from typing import Optional
from connectors.base import BaseConnector


class WikidataConnector(BaseConnector):
    name = "wikidata"
    base_url = "https://api.exemplo.com/wikidata/w/api.php"
    default_ttl = 86400

    async def fetch(self, query: dict) -> Optional[dict]:
        search = query.get("q", "")
        qid = query.get("qid", "")

        if qid:
            params = {
                "action": "wbgetentities",
                "ids": qid,
                "format": "json",
                "props": "labels|descriptions|claims|sitelinks",
                "languages": "en|pt|es",
            }
        elif search:
            params = {
                "action": "wbsearchentities",
                "search": search,
                "language": "en",
                "limit": 5,
                "format": "json",
            }
        else:
            return None

        try:
            resp = await self.client.get(self.base_url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if search:
                    results = data.get("search", [])
                    return {
                        "total": len(results),
                        "results": [
                            {
                                "id": r.get("id", ""),
                                "label": r.get("label", ""),
                                "description": r.get("description", ""),
                            }
                            for r in results
                        ],
                    }
                else:
                    entities = data.get("entities", {})
                    for eid, entity in entities.items():
                        labels = entity.get("labels", {})
                        desc = entity.get("descriptions", {})
                        return {
                            "id": eid,
                            "label": labels.get("en", {}).get("value", ""),
                            "label_pt": labels.get("pt", {}).get("value", ""),
                            "description": desc.get("en", {}).get("value", ""),
                            "description_pt": desc.get("pt", {}).get("value", ""),
                        }
                    return None
            return None
        except Exception:
            return None
