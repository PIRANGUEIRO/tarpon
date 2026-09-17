from fastapi import APIRouter, Query
from app.geo_data import PORTOS

router = APIRouter(prefix="/api/tracking", tags=["Tracking"])


@router.get("/")
def listar_tracking(
    empresa_id: int | None = None,
    data_inicio=None,
    data_fim=None,
    status: str | None = None,
    limit: int = 50,
):
    return {
        "total": 0,
        "resultados": [],
        "nota": "Rastreamento de containers requer BL via Siscomex (certificado digital e-CPF/e-CNPJ). "
                "Dados indisponíveis sem certificado.",
    }


@router.get("/stats")
def tracking_stats(empresa_id: int | None = None):
    return {
        "total": 0,
        "embarcados": 0,
        "em_transito": 0,
        "desembaracando": 0,
        "retirado": 0,
        "atrasados": 0,
        "total_armadores": 0,
        "armadores": 0,
        "ativos_30d": 0,
        "concluidos": 0,
        "por_armador": {},
        "nota": "Sem BL do Siscomex, rastreamento indisponível",
    }


@router.get("/rotas-completas")
def rotas_completas(armador: str | None = None):
    from app.utils.sea_routes import todas_rotas
    rotas_db = todas_rotas()

    portos_map = {}
    for nome, info in PORTOS.items():
        portos_map[nome] = info

    armadores_data = {}
    for rota in rotas_db:
        armador_nome = "Operadoras Marítimas"
        if armador and armador != armadores_data.get("armador"):
            continue
        if armador_nome not in armadores_data:
            armadores_data[armador_nome] = {"armador": armador_nome, "rotas": [], "total_rotas": 0}

        origem_info = portos_map.get(rota["origem"], {})
        destino_info = portos_map.get(rota["destino"], {})

        armadores_data[armador_nome]["rotas"].append({
            "origem": rota["origem"],
            "destino": rota["destino"],
            "distancia_milhas": rota["distancia_milhas"],
            "distancia_km": rota["distancia_km"],
            "tempo_dias": rota.get("tempo_dias", 0),
            "modal": "maritimo",
            "total_viagens": 0,
            "vessels": [],
            "escalas": [],
            "origem_lat": origem_info.get("lat"),
            "origem_lon": origem_info.get("lon"),
            "destino_lat": destino_info.get("lat"),
            "destino_lon": destino_info.get("lon"),
        })
        armadores_data[armador_nome]["total_rotas"] += 1

    resultado = list(armadores_data.values())
    return {
        "armadores": [a["armador"] for a in resultado],
        "dados": resultado,
        "nota": "Rotas baseadas em-distâncias reais entre portos (sem BL/Siscomex)",
    }


@router.get("/calendario")
def calendario_armadores(armador: str | None = None):
    return {
        "armadores": [],
        "eventos": [],
        "nota": "Calendário de partidas/chegadas requer dados de BL via Siscomex",
    }


@router.get("/schedules")
def schedules_por_armador(armador: str | None = None):
    return {
        "armadores": [],
        "schedules": [],
        "nota": "Schedules requerem dados de BL via Siscomex",
    }


@router.get("/{tracking_id}")
def detalhe_tracking(tracking_id: int):
    return {
        "erro": "Detalhes de tracking requerem BL via Siscomex (certificado digital)",
        "tracking_id": tracking_id,
    }
