from fastapi import APIRouter, Query
from connectors.opencorporates import OpenCorporatesConnector
from connectors.companies_house import CompaniesHouseConnector
from connectors.github import GitHubConnector

router = APIRouter(prefix="/api/empresas", tags=["Empresas Internacionais"])


@router.get("/intl/busca")
async def busca_empresa_intl(
    q: str = Query(..., description="Nome da empresa"),
    pais: str = Query(None, description="Código jurisdição (gb, us, de...)"),
    limit: int = Query(10),
):
    oc = OpenCorporatesConnector()
    try:
        query = {"q": q, "limit": limit}
        if pais:
            query["jurisdiction"] = pais
        data = await oc.cached_fetch(query)
        return {"fonte": "opencorporates", "dados": data}
    finally:
        await oc.close()


@router.get("/intl/uk/{company_number}")
async def empresa_uk(company_number: str):
    ch = CompaniesHouseConnector()
    try:
        data = await ch.cached_fetch({"number": company_number})
        return {"fonte": "companies_house", "dados": data}
    finally:
        await ch.close()


@router.get("/intl/uk/busca")
async def busca_empresa_uk(
    q: str = Query(..., description="Nome da empresa"),
    limit: int = Query(10),
):
    ch = CompaniesHouseConnector()
    try:
        data = await ch.cached_fetch({"name": q})
        return {"fonte": "companies_house", "dados": data}
    finally:
        await ch.close()


@router.get("/github/{org}")
async def github_org(org: str):
    gh = GitHubConnector()
    try:
        data = await gh.cached_fetch({"org": org})
        return {"fonte": "github", "dados": data}
    finally:
        await gh.close()


@router.get("/github/busca")
async def busca_github(q: str = Query(..., description="Termo de busca")):
    gh = GitHubConnector()
    try:
        data = await gh.cached_fetch({"q": q})
        return {"fonte": "github", "dados": data}
    finally:
        await gh.close()
