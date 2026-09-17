# Repository Audit - Tarpon

Gerado em 2026-09-17.

## Inventário
- Linguagem: Python 3.11 (100%, 77 arquivos, ~7.3k linhas)
- Backend: FastAPI, 14 routers, 22 conectores, 5 scoring, 3 crawlers, 2 tests
- Frontend: Streamlit + httpx + pandas
- APIs: 20+ (ComexStat, Bacen, IBGE, ViaCEP, Nominatim, Overpass, OpenCorporates, Companies House, FleetMon, GDELT, OpenWeather, GitHub, UN Comtrade, World Bank, Wikidata, BrasilAPI, ReceitaWS, etc.)
- Infra: localhost:8000 (FastAPI) + Streamlit
- Testes: 2 (test_api.py, test_scoring.py)

## Classificação
D - Estudo / Pausado - projeto ambicioso demais, 7k linhas, escopo de plataforma inteira de inteligência Comex. Não retornará tão cedo.

## Segurança
- Chaves via os.environ.get com default "", mock por padrão
- Nenhum segredo hardcoded após sanitização
