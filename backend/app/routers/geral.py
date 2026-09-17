from fastapi import APIRouter
from connectors.brasilapi import BrasilAPIConnector
from connectors.comexstat import ComexStatConnector
from connectors.ibge import IBGESIDRAConnector
from connectors.nominatim import NominatimConnector
from connectors.bacen import BACENConnector
from connectors.viacep import ViaCEPConnector
from connectors.un_comtrade import UNComtradeConnector
from connectors.world_bank import WorldBankConnector
from connectors.opencorporates import OpenCorporatesConnector
from connectors.companies_house import CompaniesHouseConnector
from connectors.github import GitHubConnector
from connectors.cache import Cache

router = APIRouter(prefix="/api", tags=["Geral"])

cache = Cache()


@router.get("/")
def root():
    return {"status": "ok", "projeto": "Radar de Elite", "versao": "0.3.0", "modo": "sem_banco"}


@router.get("/health")
async def health():
    brasilapi = BrasilAPIConnector()
    comexstat = ComexStatConnector()
    ibge = IBGESIDRAConnector()
    nominatim = NominatimConnector()
    bacen = BACENConnector()
    un_comtrade = UNComtradeConnector()
    world_bank = WorldBankConnector()

    results = {}
    connectors = [
        ("brasilapi", brasilapi),
        ("comexstat", comexstat),
        ("ibge", ibge),
        ("nominatim", nominatim),
        ("bacen", bacen),
        ("un_comtrade", un_comtrade),
        ("world_bank", world_bank),
    ]

    for name, conn in connectors:
        try:
            ok = await conn.health_check()
            results[name] = "ok" if ok else "down"
        except Exception:
            results[name] = "error"
        finally:
            await conn.close()

    all_ok = all(v == "ok" for v in results.values())
    return {
        "status": "ok" if all_ok else "degraded",
        "connectors": results,
        "cache": cache.stats(),
    }
