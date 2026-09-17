from typing import Optional
from connectors.base import BaseConnector


class IBGESIDRAConnector(BaseConnector):
    name = "ibge_sidra"
    base_url = "https://api.exemplo.com/ibge/values/t"
    default_ttl = 2592000

    async def fetch(self, query: dict) -> Optional[dict]:
        tabela = query.get("tabela", 5938)
        cod_ibge = query.get("cod_ibge", "3550308")
        variavel = query.get("variavel", 37)
        ano = query.get("ano", 2021)

        url = f"{self.base_url}/{tabela}/n6/{cod_ibge}/v/{variavel}/p/{ano}"
        try:
            resp = await self.client.get(url)
            if resp.status_code == 200:
                dados = resp.json()
                if len(dados) > 1:
                    rows = dados[1:]
                    return {
                        "tabela": tabela,
                        "cod_ibge": cod_ibge,
                        "ano": ano,
                        "dados": rows,
                    }
            return None
        except Exception:
            return None

    async def pib_municipal(self, cod_ibge: str, ano: int = 2021) -> Optional[dict]:
        return await self.fetch({"tabela": 5938, "cod_ibge": cod_ibge, "variavel": 37, "ano": ano})

    async def populacao(self, cod_ibge: str, ano: int = 2021) -> Optional[dict]:
        return await self.fetch({"tabela": 9514, "cod_ibge": cod_ibge, "variavel": 93, "ano": ano})
