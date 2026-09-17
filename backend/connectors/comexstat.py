from typing import Optional
from connectors.base import BaseConnector

UF_TO_COMEXSTAT = {
    "AC": "12", "AL": "27", "AM": "13", "AP": "16", "BA": "32",
    "CE": "23", "DF": "54", "ES": "34", "GO": "53", "MA": "21",
    "MG": "33", "MS": "55", "MT": "52", "PA": "15", "PB": "25",
    "PE": "26", "PI": "22", "PR": "42", "RJ": "36", "RN": "24",
    "RO": "11", "RR": "14", "RS": "45", "SC": "44", "SE": "31",
    "SP": "41", "TO": "17",
}


class ComexStatConnector(BaseConnector):
    name = "comexstat"
    base_url = "https://api.exemplo.com/comexstat"
    default_ttl = 604800

    async def fetch(self, query: dict) -> Optional[dict]:
        flow = query.get("flow", "export")
        ano_inicio = query.get("ano_inicio", 2025)
        ano_fim = query.get("ano_fim", 2025)
        mes_inicio = query.get("mes_inicio", "01")
        mes_fim = query.get("mes_fim", "12")
        uf = query.get("uf")
        ncm = query.get("ncm")

        details = ["country"]
        if uf:
            details.append("state")

        filters = []
        if uf:
            comexstat_code = UF_TO_COMEXSTAT.get(uf.upper(), uf)
            filters.append({"filter": "state", "values": [comexstat_code]})
        if ncm:
            filters.append({"filter": "ncm", "values": [ncm]})

        body = {
            "flow": flow,
            "monthDetail": True,
            "period": {
                "from": f"{ano_inicio}-{mes_inicio}",
                "to": f"{ano_fim}-{mes_fim}",
            },
            "details": details,
            "filters": filters,
            "metrics": ["metricFOB", "metricKG"],
        }

        try:
            resp = await self.client.post(
                f"{self.base_url}/general?language=pt",
                json=body,
            )
            if resp.status_code == 200:
                data = resp.json()
                lst = data.get("data", {}).get("list", [])
                total_fob = sum(int(r.get("metricFOB", 0)) for r in lst)
                total_kg = sum(int(r.get("metricKG", 0)) for r in lst)
                top_partners = sorted(
                    [{"pais": r.get("country", ""), "fob": int(r.get("metricFOB", 0))}
                     for r in lst],
                    key=lambda x: x["fob"],
                    reverse=True,
                )[:10]
                return {
                    "total": len(lst),
                    "flow": flow,
                    "total_fob_usd": total_fob,
                    "total_kg": total_kg,
                    "top_parceiros": top_partners,
                    "records": lst[:50],
                }
            elif resp.status_code == 429:
                return {"erro": "Rate limit ComexStat. Aguarde 10s.", "total": 0}
            else:
                err = resp.json().get("error", {}).get("message", resp.text[:200])
                return {"erro": err, "total": 0}
        except Exception as e:
            return {"erro": str(e), "total": 0}

    async def resumo_uf(self, uf: str, ano: int = 2025) -> dict:
        importacao = await self.fetch({
            "flow": "import",
            "ano_inicio": ano,
            "ano_fim": ano,
            "uf": uf,
        })
        exportacao = await self.fetch({
            "flow": "export",
            "ano_inicio": ano,
            "ano_fim": ano,
            "uf": uf,
        })
        return {
            "uf": uf.upper(),
            "ano": ano,
            "importacao": importacao,
            "exportacao": exportacao,
        }
