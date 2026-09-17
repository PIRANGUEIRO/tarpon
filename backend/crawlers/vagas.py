"""
Crawler de vagas de comércio exterior (LinkedIn, Indeed, Catho)
Usa scraping público via Google Search + httpx para detectar empresas contratando para funções de importação.
"""

import httpx
import re
import urllib.parse

from crawlers.base import BaseCrawler, logger

KEYWORDS_VAGAS_IMPORTACAO = [
    "analista de importação", "analista de comércio exterior",
    "assistente de importação", "coordenador de importação",
    "coordenador de comex", "analista de comex",
    "comprador internacional", "trade analyst",
    "supply chain internacional", "logística internacional",
    "despachante aduaneiro", "import analyst",
    "foreign trade analyst", "sourcing analyst",
    "global procurement", "international buyer",
]

GOOGLE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


class VagasCrawler(BaseCrawler):
    fonte = "vagas"

    def buscar_empresa(self, razao_social: str) -> dict | None:
        """Busca vagas da empresa em múltiplas fontes."""
        return self._fetch_vagas(razao_social)

    def _fetch_vagas(self, razao_social: str):
        """Busca vagas via Google Search em sites de emprego."""
        vagas_encontradas = []
        fontes_consultadas = []

        sites_busca = [
            ("linkedin.com/jobs", "LinkedIn"),
            ("indeed.com", "Indeed"),
            ("catho.com.br", "Catho"),
            ("infojobs.com.br", "InfoJobs"),
            ("vagas.com.br", "Vagas.com.br"),
            ("glassdoor.com", "Glassdoor"),
        ]

        for site, nome_site in sites_busca:
            try:
                query = urllib.parse.quote(f'"{razao_social}" "{site}" importação OR comex OR "comércio exterior" OR "foreign trade"')
                r = httpx.get(
                    f"https://api.exemplo.com/google/search?q={query}&hl=pt-BR",
                    headers=GOOGLE_HEADERS,
                    timeout=15,
                    follow_redirects=True,
                )

                if r.status_code != 200:
                    continue

                text = r.text.lower()
                fontes_consultadas.append(nome_site)

                empresa_lower = razao_social.lower()
                tem_empresa = empresa_lower in text or any(
                    palavra in text for palavra in empresa_lower.split() if len(palavra) > 4
                )

                if not tem_empresa:
                    continue

                vagas_site = []
                for kw in KEYWORDS_VAGAS_IMPORTACAO:
                    if kw.lower() in text:
                        vagas_site.append(kw)

                if vagas_site:
                    vagas_encontradas.extend(vagas_site)

            except Exception as e:
                logger.debug(f"Erro busca {nome_site} para {razao_social}: {e}")
                continue

        vagas_unicas = list(set(vagas_encontradas))

        return {
            "empresa": razao_social,
            "total_vagas_importacao": len(vagas_unicas),
            "vagas_encontradas": sorted(vagas_unicas)[:10],
            "possui_vaga_importacao": len(vagas_unicas) > 0,
            "fontes_consultadas": fontes_consultadas,
        }

    def score_empresa(self, razao_social: str) -> dict:
        """Calcula score de contratação para importação."""
        resultado = self.buscar_empresa(razao_social) or {}

        total_vagas = resultado.get("total_vagas_importacao", 0)
        fontes = len(resultado.get("fontes_consultadas", []))

        score_vagas = min(total_vagas * 8 + fontes * 3, 100)

        return {
            "score_vagas": score_vagas,
            "total_vagas": total_vagas,
            "vagas_encontradas": resultado.get("vagas_encontradas", []),
            "fontes": resultado.get("fontes_consultadas", []),
        }


if __name__ == "__main__":
    crawler = VagasCrawler()
    resultado = crawler.score_empresa("Petrobras")
    print(f"  score={resultado.get('score_vagas', 0)}, vagas={resultado.get('total_vagas', 0)}")
