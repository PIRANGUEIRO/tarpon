import re

KEYWORDS_IMPORTACAO = [
    "importação", "importador", "importado", "comércio exterior",
    "comex", "despachante aduaneiro", "logística internacional",
    "trade compliance", "agente de carga", "sourcing global",
]

KEYWORDS_PRODUTO = [
    "produto", "categoria", "catálogo", "linha", "marca",
]

def extrair_termos_importacao(texto: str) -> list[str]:
    encontrados = []
    for kw in KEYWORDS_IMPORTACAO:
        if re.search(kw, texto, re.IGNORECASE):
            encontrados.append(kw)
    return encontrados

def extrair_produtos(texto: str) -> list[str]:
    encontrados = []
    for kw in KEYWORDS_PRODUTO:
        if re.search(kw, texto, re.IGNORECASE):
            encontrados.append(kw)
    return encontrados

def limpar_html(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html).strip()

def score_importador_por_texto(texto: str) -> tuple[float, list[str]]:
    termos = extrair_termos_importacao(texto)
    score = min(len(termos) * 15, 100)
    return score, termos
