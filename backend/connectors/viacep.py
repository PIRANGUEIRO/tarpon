# Mock APIs — troque via .env para endpoints reais
from typing import Optional
from connectors.base import BaseConnector


class ViaCEPConnector(BaseConnector):
    name = "viacep"
    base_url = "https://api.exemplo.com/viacep/ws"
    default_ttl = 2592000

    async def fetch(self, query: dict) -> Optional[dict]:
        cep = query.get("cep", "").replace("-", "").strip()
        if not cep or len(cep) != 8:
            return None
        try:
            resp = await self.client.get(f"{self.base_url}/{cep}/json/")
            if resp.status_code == 200:
                data = resp.json()
                if not data.get("erro"):
                    return {
                        "cep": data.get("cep", ""),
                        "logradouro": data.get("logradouro", ""),
                        "complemento": data.get("complemento", ""),
                        "bairro": data.get("bairro", ""),
                        "localidade": data.get("localidade", ""),
                        "uf": data.get("uf", ""),
                        "ibge": data.get("ibge", ""),
                    }
            return None
        except Exception:
            return None
