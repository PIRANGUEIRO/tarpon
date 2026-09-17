"""
Crawler de websites com extração heurística (regex + keywords)
Identifica se uma empresa é importadora pelo site.
"""

import re
import httpx
import urllib.parse

from crawlers.base import BaseCrawler, logger

KEYWORDS_IMPORTACAO = [
    r"importad[oaei]",
    r"importação",
    r"importado por",
    r"importamos de",
    r"distribuidor exclusivo",
    r"representante exclusivo",
    r"comércio exterior",
    r"comex",
    r"despachante aduaneiro",
    r"compr[ao] internacional",
    r"logística internacional",
    r"agente de carga",
    r"trade compliance",
    r"fornecedor internacional",
    r"produto importado",
    r"importação de equipamentos",
    r"importa direto",
    r"parceiro global",
    r"marca internacional",
    r"linha importada",
    r"catálogo internacional",
    r"representante no brasil",
    r"subsidiária",
    r"sourcing global",
    r"supply chain global",
]

KEYWORDS_PRODUTOS = [
    r"produtos?", r"linhas?", r"categorias?",
    r"catálogo", r"catalogo", r"produto",
    r"soluções", r"solucoes", r"marcas?",
]

KEYWORDS_MARCAS = [
    r"marcas?", r"brands?", r"nossas marcas",
    r"portfólio", r"portfolio", r"representamos",
]

KEYWORDS_NEGATIVAS = [
    r"template", r"wordpress", r"under construction",
    r"em breve", r"site em construção",
    r"coming soon", r"pagina inicial",
]

class WebsiteCrawler(BaseCrawler):
    fonte = "website"

    def extrair_texto(self, url: str) -> str | None:
        """Baixa o HTML e extrai texto limpo."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            }
            r = httpx.get(url, headers=headers, timeout=20, follow_redirects=True)
            if r.status_code != 200:
                return None

            html = r.text.lower()

            html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
            html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
            html = re.sub(r"<[^>]+>", " ", html)
            html = re.sub(r"\s+", " ", html).strip()

            for kw in KEYWORDS_NEGATIVAS:
                if re.search(kw, html):
                    logger.info(f"  Site parece template: {url}")
                    return None

            return html[:50000]

        except Exception as e:
            logger.error(f"Erro ao acessar {url}: {e}")
            return None

    def analisar_texto(self, texto: str) -> dict:
        """Analisa texto com heurística (regex)."""
        resultado = {
            "termos_importacao": [],
            "produtos": [],
            "marcas": [],
            "score_heuristica": 0,
            "e_importador": False,
        }

        for kw in KEYWORDS_IMPORTACAO:
            matches = re.findall(kw, texto, re.IGNORECASE)
            if matches:
                resultado["termos_importacao"].extend(matches)

        for kw in KEYWORDS_PRODUTOS:
            if re.search(kw, texto, re.IGNORECASE):
                resultado["produtos"].append(kw)

        for kw in KEYWORDS_MARCAS:
            if re.search(kw, texto, re.IGNORECASE):
                resultado["marcas"].append(kw)

        resultado["termos_importacao"] = list(set(resultado["termos_importacao"]))

        score = 0
        score += len(resultado["termos_importacao"]) * 15
        score += len(resultado["produtos"]) * 5
        score += len(resultado["marcas"]) * 8
        resultado["score_heuristica"] = min(score, 100)
        resultado["e_importador"] = resultado["score_heuristica"] >= 30

        return resultado

    def encontrar_url_empresa(self, razao_social: str, cnae: str = None) -> str | None:
        """Tenta encontrar o site da empresa via Google."""
        try:
            query = urllib.parse.quote(f'{razao_social} site oficial')
            r = httpx.get(
                f"https://api.exemplo.com/google/search?q={query}",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            urls = re.findall(r'https?://(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+[/a-zA-Z0-9-]*', r.text)
            for url in urls:
                if not any(skip in url for skip in ["google", "youtube", "facebook", "instagram", "linkedin"]):
                    return url.split("&")[0]
        except Exception:
            pass
        return None

    def analisar_empresa(self, razao_social: str, url: str = None, cnae: str = None) -> dict | None:
        """Analisa o website de uma empresa e retorna o resultado."""
        if not url:
            url = self.encontrar_url_empresa(razao_social, cnae)
        if not url:
            return None

        texto = self.extrair_texto(url)
        if not texto:
            return None

        analise = self.analisar_texto(texto)

        return {
            "url": url,
            "score": analise["score_heuristica"],
            "e_importador": analise["e_importador"],
            "termos": analise["termos_importacao"],
            "produtos": analise["produtos"],
            "marcas": analise["marcas"],
        }


if __name__ == "__main__":
    crawler = WebsiteCrawler()
    resultado = crawler.analisar_empresa("Petrobras", "https://petrobras.com.br")
    if resultado:
        print(f"  URL: {resultado['url']}")
        print(f"  Score: {resultado['score']}")
        print(f"  É importador: {resultado['e_importador']}")
