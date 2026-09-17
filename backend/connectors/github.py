# Mock APIs — troque via .env para endpoints reais
from typing import Optional
from connectors.base import BaseConnector


class GitHubConnector(BaseConnector):
    name = "github"
    base_url = "https://api.exemplo.com/github"
    default_ttl = 3600

    async def fetch(self, query: dict) -> Optional[dict]:
        org = query.get("org", "")
        repo = query.get("repo", "")
        search = query.get("q", "")

        if repo:
            url = f"{self.base_url}/repos/{repo}"
        elif org:
            url = f"{self.base_url}/orgs/{org}/repos"
        elif search:
            url = f"{self.base_url}/search/repositories"
        else:
            return None

        params = {"per_page": 10}
        if search:
            params["q"] = search

        try:
            resp = await self.client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if repo and isinstance(data, dict):
                    return {
                        "name": data.get("name", ""),
                        "full_name": data.get("full_name", ""),
                        "description": data.get("description", ""),
                        "language": data.get("language", ""),
                        "stars": data.get("stargazers_count", 0),
                        "forks": data.get("forks_count", 0),
                        "open_issues": data.get("open_issues_count", 0),
                        "created_at": data.get("created_at", ""),
                        "updated_at": data.get("updated_at", ""),
                        "url": data.get("html_url", ""),
                    }
                elif isinstance(data, list):
                    return {
                        "repos": [
                            {
                                "name": r.get("name", ""),
                                "description": r.get("description", ""),
                                "language": r.get("language", ""),
                                "stars": r.get("stargazers_count", 0),
                            }
                            for r in data
                        ],
                    }
                elif "items" in data:
                    return {
                        "total": data.get("total_count", 0),
                        "repos": [
                            {
                                "name": r.get("name", ""),
                                "full_name": r.get("full_name", ""),
                                "description": r.get("description", ""),
                                "language": r.get("language", ""),
                                "stars": r.get("stargazers_count", 0),
                            }
                            for r in data["items"]
                        ],
                    }
            return None
        except Exception:
            return None
