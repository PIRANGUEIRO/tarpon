"""
Crawler de dados do IBGE (API pública)
Fornece dados socioeconômicos por município para enriquecimento.
Usa a API SIDRA do IBGE para PIB per capita e população.
"""

import httpx

from crawlers.base import BaseCrawler, logger

IBGE_SIDRA_BASE = "https://api.exemplo.com/ibge/values"

MUNICIPIOS_IBGE = {
    "sao paulo": 3550308, "curitiba": 4106902, "santos": 3548500,
    "joinville": 4209102, "blumenau": 4202404, "campinas": 3509502,
    "guarulhos": 3518800, "sao bernardo do campo": 3548708,
    "sao jose dos campos": 3549904, "ribeirao preto": 3549805,
    "sorocaba": 3552809, "osasco": 3534401, "mogi das cruzes": 3530606,
    "santo andre": 3547809, "maua": 3528907, "itaquaquecetuba": 3523106,
    "franca": 3516206, "aracatuba": 3502803, "presidente prudente": 3541406,
    "marilia": 3529004, "bauru": 3506003, "jau": 3525507,
    "botucatu": 3506607, "ourinhos": 3534708, "assis": 3503603,
    "londrina": 4113700, "maringa": 4115101, "cascavel": 4104808,
    "foz do iguacu": 4108304, "ponta grossa": 4119905,
    "caxias do sul": 4305108, "pelotas": 4314100, "canoas": 4304606,
    "santa maria": 4319901, "criciuma": 4204608, "florianopolis": 4205407,
    "itajai": 4208104, "jaragua do sul": 4209003,
    "belo horizonte": 3106200, "contagem": 3118601, "uberlandia": 3170206,
    "juiz de fora": 3136702, "betim": 3106705, "montes claros": 3143302,
    "governador valadares": 3127701, "ipatinga": 3131307,
    "vitoria": 3205309, "vila velha": 3205200, "cariacica": 3201309,
    "serra": 3205101, "cachoeiro de itapemirim": 3201200,
    "salvador": 2927408, "feira de santo antonio": 2910800, "camacari": 2905707,
    "ilheus": 2913606, "jacobina": 2917301, "juazeiro": 2918408,
    "recife": 2611606, "jaboatao dos guararapes": 2636104,
    "olinda": 2609606, "caruaru": 2604102, "petrolina": 2611101,
    "fortaleza": 2304400, "caucaia": 2303709, "juazeiro do norte": 2307304,
    "maracanau": 2308104, "sobral": 2312906, "crato": 2304202,
    "manaus": 1302603, "parintins": 1303403, "coari": 1301209,
    "porto velho": 1100205, "ji-parana": 1100122, "arianopolis": 1100320,
    "rio branco": 1200401, "cruzeiro do sul": 1200203,
    "campo grande": 5002704, "dourados": 5003702, "tres lagoas": 5003751,
    "corumba": 5003207, "naviraí": 5006200,
    "goiania": 5208707, "aparecida de goiania": 5201138,
    "anapolis": 5201104, "rio verde": 5218800, "itumbiara": 5211507,
    "cuiaba": 5103403, "varzea grande": 5108409, "rondonopolis": 5107609,
    "sinop": 5107906, "sorriso": 5107873,
    "aracaju": 2800308, "nossa senhora do socorro": 2800605,
    "maceio": 2704302, "arapiraca": 2700300, "penedo": 2706705,
    "natal": 2408102, "mossoro": 2408001, "parnamirim": 2409306,
    "joao pessoa": 2507507, "campina grande": 2504009, "santa rita": 2513707,
    "tiradentes": 3168706, "ouro preto": 3146108,
    "palmas": 1721000, "araguaina": 1702109, "porto nacional": 1718205,
    "macapa": 1600303, "santana": 1600600,
    "boa vista": 1400100, "rorainopolis": 1400456,
    "rio de janeiro": 3304557, "niteroi": 3303302, "duque de caxias": 3301701,
    "nova iguacu": 3303500, "campos dos goytacazes": 3301008, "petropolis": 3303906,
    "paranagua": 4118204, "antonio cardoso": 2901701,
    "brusque": 4202909, "novo hamburgo": 4313409,
    "barueri": 3505708, "osasco": 3534401, "taboao da serra": 3552700,
    "camaqua": 4303501, "sao jose do rio preto": 3549904,
    "sao jose": 4209102,
}

IBGE_UF_PARA_CODIGO = {
    "AC": "12", "AL": "27", "AP": "16", "AM": "13", "BA": "29",
    "CE": "23", "DF": "53", "ES": "32", "GO": "52", "MA": "21",
    "MT": "51", "MS": "50", "MG": "31", "PA": "15", "PB": "25",
    "PR": "41", "PE": "26", "PI": "22", "RN": "24", "RS": "43",
    "RJ": "33", "RO": "11", "RR": "14", "SC": "42", "SP": "35",
    "SE": "28", "TO": "17",
}


class IBGECrawler(BaseCrawler):
    fonte = "ibge"

    def _match_municipio(self, nome: str) -> int | None:
        nome_lower = nome.lower().strip()
        if nome_lower in MUNICIPIOS_IBGE:
            return MUNICIPIOS_IBGE[nome_lower]
        for key, code in MUNICIPIOS_IBGE.items():
            if nome_lower in key or key in nome_lower:
                return code
        palavras = [p for p in nome_lower.split() if len(p) > 3]
        for key, code in MUNICIPIOS_IBGE.items():
            if any(p in key for p in palavras):
                return code
        return None

    def buscar_pib_municipio(self, municipio: str, uf: str, ano: int = 2022) -> dict | None:
        cod_ibge = self._match_municipio(municipio)
        if not cod_ibge:
            logger.warning(f"IBGE: código não encontrado para {municipio}/{uf}")
            return {"pib_per_capita": None, "pib_total_mil": None, "fonte": "nao_mapeado", "ano": ano}

        try:
            url = f"{IBGE_SIDRA_BASE}/t/5938/n6/{cod_ibge}/v/37/p/{ano}"
            r = httpx.get(url, timeout=30, follow_redirects=True)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 1:
                    row = data[1]
                    valor = row.get("V", "")
                    if valor and valor not in ("...", "-", ""):
                        pib_total_mil = float(valor.replace(".", "").replace(",", "."))
                        pib_total = pib_total_mil * 1000
                        pop = self.buscar_populacao(municipio, uf)
                        pop_val = pop.get("populacao") if pop else None
                        pib_per_capita = round(pib_total / pop_val, 2) if pop_val and pop_val > 0 else None
                        return {
                            "pib_per_capita": pib_per_capita,
                            "pib_total_mil": pib_total_mil,
                            "populacao": pop_val,
                            "fonte": url,
                            "ano": ano,
                        }
            logger.warning(f"IBGE PIB: dados não encontrados para {municipio}/{uf} (código {cod_ibge})")
            return {"pib_per_capita": None, "pib_total_mil": None, "fonte": url, "ano": ano}
        except Exception as e:
            logger.error(f"Erro IBGE PIB {municipio}/{uf}: {e}")
            return {"pib_per_capita": None, "pib_total_mil": None, "fonte": "erro", "ano": ano}

    def buscar_populacao(self, municipio: str, uf: str) -> dict | None:
        cod_ibge = self._match_municipio(municipio)
        if not cod_ibge:
            return {"populacao": None, "fonte": "nao_mapeado", "ano": 2024}

        try:
            url = f"{IBGE_SIDRA_BASE}/t/9514/n6/{cod_ibge}/v/9324/p/last"
            r = httpx.get(url, timeout=30, follow_redirects=True)
            if r.status_code == 200:
                data = r.json()
                if len(data) > 1:
                    row = data[1]
                    valor = row.get("V", "")
                    ano = row.get("D3C", "2024")
                    if valor and valor not in ("...", "-", ""):
                        pop = int(valor.replace(".", "").replace(",", "."))
                        return {"populacao": pop, "fonte": url, "ano": int(ano)}

            try:
                url2 = f"{IBGE_SIDRA_BASE}/t/6579/n6/{cod_ibge}/v/9324/p/last"
                r2 = httpx.get(url2, timeout=30, follow_redirects=True)
                if r2.status_code == 200:
                    data2 = r2.json()
                    if len(data2) > 1:
                        valor = data2[1].get("V", "")
                        ano = data2[1].get("D3C", "2022")
                        if valor and valor not in ("...", "-", ""):
                            pop = int(valor.replace(".", "").replace(",", "."))
                            return {"populacao": pop, "fonte": url2, "ano": int(ano)}
            except Exception:
                pass

            logger.warning(f"IBGE Pop: dados não encontrados para {municipio}/{uf}")
            return {"populacao": None, "fonte": url, "ano": 2024}
        except Exception as e:
            logger.error(f"Erro IBGE Pop {municipio}/{uf}: {e}")
            return {"populacao": None, "fonte": "erro", "ano": 2024}

    def enrich(self, municipio: str, uf: str) -> dict:
        """Enriquece dados de um município com PIB + população do IBGE."""
        pib = self.buscar_pib_municipio(municipio, uf)
        pop = self.buscar_populacao(municipio, uf)

        pib_per_capita = None
        populacao = None

        if pib and pib.get("pib_per_capita") is not None:
            pib_per_capita = pib["pib_per_capita"]
        if pop and pop.get("populacao") is not None:
            populacao = pop["populacao"]
        elif pib and pib.get("populacao") is not None:
            populacao = pib["populacao"]

        return {
            "municipio": municipio,
            "uf": uf,
            "pib_per_capita": pib_per_capita,
            "populacao": populacao,
        }


if __name__ == "__main__":
    crawler = IBGECrawler()
    resultado = crawler.enrich("São Paulo", "SP")
    print(f"  {resultado['municipio']}/{resultado['uf']}: PIB/cap={resultado.get('pib_per_capita')} Pop={resultado.get('populacao')}")
