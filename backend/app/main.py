from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    geral, empresas, empresas_intl, ranking, crawlers, scoring,
    comex, insights, embarques, tracking, filtro, alertas,
    market_intel, intel,
)

app = FastAPI(
    title="Radar de Elite API",
    description="API de Inteligência Comercial para Comércio Exterior",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(geral.router)
app.include_router(empresas.router)
app.include_router(empresas_intl.router)
app.include_router(ranking.router)
app.include_router(crawlers.router)
app.include_router(scoring.router)
app.include_router(comex.router)
app.include_router(intel.router)
app.include_router(insights.router)
app.include_router(embarques.router)
app.include_router(tracking.router)
app.include_router(filtro.router)
app.include_router(alertas.router)
app.include_router(market_intel.router)
