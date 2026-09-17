# Mock APIs — troque via .env para endpoints reais
from typing import Optional
from datetime import datetime, timedelta
from connectors.base import BaseConnector


class BACENConnector(BaseConnector):
    name = "bacen"
    base_url = "https://api.exemplo.com/bcb/dados/serie/bcdata.sgs"
    default_ttl = 3600

    SERIES = {
        "ptax_compra": 1,
        "ptax_venda": 10813,
        "ipca": 432,
        "selic": 11,
        "balanca_comercial": 3696,
    }

    def _last_30_days(self) -> tuple[str, str]:
        hoje = datetime.now()
        inicio = hoje - timedelta(days=30)
        return inicio.strftime("%d/%m/%Y"), hoje.strftime("%d/%m/%Y")

    async def fetch(self, query: dict) -> Optional[dict]:
        serie_nome = query.get("serie", "ptax_compra")
        codigo = self.SERIES.get(serie_nome, 1)
        data_inicio = query.get("data_inicio", "")
        data_fim = query.get("data_fim", "")

        if not data_inicio:
            data_inicio, data_fim = self._last_30_days()

        url = f"{self.base_url}.{codigo}/dados"
        params = {"formato": "json", "dataInicial": data_inicio}
        if data_fim:
            params["dataFinal"] = data_fim

        try:
            resp = await self.client.get(url, params=params)
            if resp.status_code == 200:
                dados = resp.json()
                if isinstance(dados, list) and dados:
                    ultimo = dados[-1]
                    return {
                        "serie": serie_nome,
                        "codigo": codigo,
                        "valor": float(ultimo.get("valor", 0)),
                        "data": ultimo.get("data", ""),
                        "historico_30d": dados[-30:] if len(dados) >= 30 else dados,
                    }
            return None
        except Exception:
            return None

    async def ptax(self) -> dict:
        compra = await self.fetch({"serie": "ptax_compra"})
        venda = await self.fetch({"serie": "ptax_venda"})
        return {
            "compra": compra.get("valor") if compra else None,
            "venda": venda.get("valor") if venda else None,
            "data": compra.get("data") if compra else None,
        }
