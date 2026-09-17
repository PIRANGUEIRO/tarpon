import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_root():
    r = client.get("/api/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200

def test_listar_empresas():
    r = client.get("/api/empresas?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "empresas" in data

def test_buscar_empresa_por_id():
    r = client.get("/api/empresas/1")
    assert r.status_code in (200, 404)

def test_ranking_tipos():
    r = client.get("/api/ranking")
    assert r.status_code == 200
    assert "tipos" in r.json()

def test_ranking_importacao():
    r = client.get("/api/ranking/importacao?limit=5")
    assert r.status_code == 200

def test_scoring_strategies():
    r = client.get("/api/scoring/strategies")
    assert r.status_code == 200
    assert "strategies" in r.json()

def test_scoring_calcular():
    r = client.post("/api/scoring/calcular/1?salvar=false")
    if r.status_code == 200:
        data = r.json()
        assert "score_geral" in data
        assert "scores" in data

def test_geo_stats():
    r = client.get("/api/crawlers/geo/stats")
    assert r.status_code == 200

def test_website_stats():
    r = client.get("/api/crawlers/website/stats")
    assert r.status_code == 200

def test_comexstat_por_uf():
    r = client.get("/api/crawlers/comexstat/uf/PR")
    assert r.status_code == 200

def test_criar_empresa_valida():
    data = {
        "cnpj": "12345678000195",
        "razao_social": "Teste Pytest Ltda",
        "uf": "SP",
        "municipio": "Sao Paulo",
    }
    r = client.post("/api/empresas", json=data)
    if r.status_code == 200:
        assert r.json()["cnpj"] == "12345678000195"
    else:
        assert r.status_code == 400

def test_criar_empresa_cnpj_repetido():
    data = {"cnpj": "56789123000145", "razao_social": "Outra Ltda"}
    client.post("/api/empresas", json=data)
    r = client.post("/api/empresas", json=data)
    assert r.status_code == 400

def test_buscar_por_cnpj():
    r = client.get("/api/empresas/cnpj/56789123000145")
    assert r.status_code == 200

# ─── Alertas ───────────────────────────────────────────────────────

def test_alertas_stats():
    r = client.get("/api/alertas/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "nao_lidos" in data
    assert "por_tipo" in data

def test_alertas_listar():
    r = client.get("/api/alertas/")
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "alertas" in data

def test_alertas_gerar():
    r = client.post("/api/alertas/gerar")
    assert r.status_code == 200
    data = r.json()
    assert "ok" in data
    assert "novos_alertas" in data

def test_alertas_marcar_lido():
    r = client.get("/api/alertas/")
    alertas = r.json().get("alertas", [])
    if alertas:
        aid = alertas[0]["id"]
        r2 = client.post(f"/api/alertas/{aid}/lido")
        assert r2.status_code == 200

# ─── Market Intel ──────────────────────────────────────────────────

def test_market_intel_panorama():
    r = client.get("/api/market-intel/panorama")
    assert r.status_code == 200
    data = r.json()
    assert "gerais" in data
    assert "armadores" in data
    assert "paises_origem" in data
    assert "top_produtos" in data

def test_market_intel_panorama_filtro_uf():
    r = client.get("/api/market-intel/panorama?uf=SP")
    assert r.status_code == 200
    data = r.json()
    assert "gerais" in data

# ─── NCM Classification ───────────────────────────────────────────

def test_ncm_classificar():
    r = client.get("/api/crawlers/ncm/classificar/84713000")
    assert r.status_code == 200
    data = r.json()
    assert "ncm" in data
    assert "capitulo" in data
    assert data["capitulo"] == "84"

def test_ncm_capitulos():
    r = client.get("/api/crawlers/ncm/capitulos")
    assert r.status_code == 200
    data = r.json()
    assert "capitulos" in data
    assert len(data["capitulos"]) > 0

# ─── Sea Routes ────────────────────────────────────────────────────

def test_sea_routes_distancia():
    r = client.get("/api/crawlers/sea-routes/distancia?origem=Shanghai&destino=Santos")
    assert r.status_code == 200
    data = r.json()
    assert "distancia_milhas" in data
    assert data["distancia_milhas"] > 0
    assert "tempo_viagem_dias" in data
    assert "custo_total_usd" in data

def test_sea_routes_rotas():
    r = client.get("/api/crawlers/sea-routes/rotas")
    assert r.status_code == 200
    data = r.json()
    assert "rotas" in data
    assert len(data["rotas"]) > 0

def test_sea_routes_porto():
    r = client.get("/api/crawlers/sea-routes/porto/Shanghai")
    assert r.status_code == 200
    data = r.json()
    assert "rotas" in data

# ─── ComexStat ─────────────────────────────────────────────────────

def test_comexstat_por_uf_dados():
    r = client.get("/api/crawlers/comexstat/uf/SP")
    assert r.status_code == 200
    data = r.json()
    assert "dados" in data
    assert len(data["dados"]) > 0

def test_comexstat_por_municipio():
    r = client.get("/api/crawlers/comexstat/municipio/Sao Paulo")
    assert r.status_code == 200
    data = r.json()
    assert "dados" in data
