from fastapi import APIRouter, Query
from connectors.comexstat import ComexStatConnector
from app.geo_data import PORTOS, AEROPORTOS
from app.utils.sea_routes import ROTAS_MARITIMAS, todas_rotas

router = APIRouter(prefix="/api/market-intel", tags=["Market Intelligence"])


@router.get("/panorama")
async def panorama_market(
    uf: str | None = None,
    ncm: str | None = None,
    ano: int = Query(2025),
):
    conn = ComexStatConnector()
    try:
        imp = await conn.cached_fetch({"flow": "import", "ano_inicio": ano, "ano_fim": ano, "uf": uf, "ncm": ncm})
        exp = await conn.cached_fetch({"flow": "export", "ano_inicio": ano, "ano_fim": ano, "uf": uf, "ncm": ncm})

        imp_ok = imp and not imp.get("erro")
        exp_ok = exp and not exp.get("erro")

        total_fob = (imp.get("total_fob_usd", 0) if imp_ok else 0) + (exp.get("total_fob_usd", 0) if exp_ok else 0)
        total_kg = (imp.get("total_kg", 0) if imp_ok else 0) + (exp.get("total_kg", 0) if exp_ok else 0)
        total_reg = (imp.get("total", 0) if imp_ok else 0) + (exp.get("total", 0) if exp_ok else 0)
        teus = max(1, total_kg // 14000) if total_kg else 0

        imp_records = imp.get("records", []) if imp_ok else []
        exp_records = exp.get("records", []) if exp_ok else []

        paises_imp_agg = {}
        for r in imp_records:
            pais = r.get("country", "")
            fob = int(r.get("metricFOB", 0) or 0)
            if pais:
                if pais not in paises_imp_agg:
                    paises_imp_agg[pais] = {"pais": pais, "fob": 0}
                paises_imp_agg[pais]["fob"] += fob
        paises_imp = sorted(paises_imp_agg.values(), key=lambda x: x["fob"], reverse=True)[:15]

        paises_exp_agg = {}
        for r in exp_records:
            pais = r.get("country", "")
            fob = int(r.get("metricFOB", 0) or 0)
            if pais:
                if pais not in paises_exp_agg:
                    paises_exp_agg[pais] = {"pais": pais, "fob": 0}
                paises_exp_agg[pais]["fob"] += fob
        paises_exp = sorted(paises_exp_agg.values(), key=lambda x: x["fob"], reverse=True)[:15]

        portos_br_list = []
        for nome, info in PORTOS.items():
            portos_br_list.append({
                "porto": nome,
                "uf": info.get("uf", ""),
                "tipo": info.get("tipo", ""),
                "lat": info.get("lat", 0),
                "lon": info.get("lon", 0),
            })
        portos_br_list.sort(key=lambda x: x["porto"])

        portos_internacionais = [
            {"porto": "Shanghai", "pais": "China", "tipo": "container"},
            {"porto": "Ningbo", "pais": "China", "tipo": "container"},
            {"porto": "Shenzhen", "pais": "China", "tipo": "container"},
            {"porto": "Qingdao", "pais": "China", "tipo": "container"},
            {"porto": "Xiamen", "pais": "China", "tipo": "container"},
            {"porto": "Busan", "pais": "Coreia do Sul", "tipo": "container"},
            {"porto": "Singapura", "pais": "Singapura", "tipo": "container"},
            {"porto": "Colombo", "pais": "Sri Lanka", "tipo": "container"},
            {"porto": "Hamburg", "pais": "Alemanha", "tipo": "container"},
            {"porto": "Antuérpia", "pais": "Bélgica", "tipo": "container"},
            {"porto": "Rotterdam", "pais": "Holanda", "tipo": "container"},
            {"porto": "Houston", "pais": "EUA", "tipo": "container"},
            {"porto": "New York", "pais": "EUA", "tipo": "container"},
            {"porto": "Savannah", "pais": "EUA", "tipo": "container"},
            {"porto": "Miami", "pais": "EUA", "tipo": "container"},
        ]

        rotas_list = []
        for (origem, destino), milhas in ROTAS_MARITIMAS.items():
            rotas_list.append({
                "rota": f"{origem} → {destino}",
                "origem": origem,
                "destino": destino,
                "distancia_milhas": milhas,
                "distancia_km": round(milhas * 1.852, 0),
            })
        rotas_list.sort(key=lambda x: x["distancia_milhas"])

        armadores_nota = "Dados de armador requerem BL via Siscomex (certificado digital)"
        agentes_nota = "Dados de agente de carga requerem BL via Siscomex (certificado digital)"

        return {
            "gerais": {
                "total_embarques": total_reg,
                "peso_bruto_ton": round(total_kg / 1000, 1),
                "total_teus": float(teus),
                "total_containers": max(1, teus // 2) if teus else 0,
                "total_fob_usd": total_fob,
            },
            "armadores": [],
            "armadores_nota": armadores_nota,
            "portos_origem": [],
            "portos_destino": [],
            "portos_brasileiros": portos_br_list,
            "portos_internacionais": portos_internacionais,
            "paises_origem": paises_imp,
            "paises_destino": paises_exp,
            "top_importadores": [{"nome": p["pais"], "fob": p["fob"]} for p in paises_imp],
            "top_exportadores": [{"nome": p["pais"], "fob": p["fob"]} for p in paises_exp],
            "top_produtos": [],
            "rotas_principais": rotas_list[:20],
            "tipo_embarque": {"importacao": imp.get("total", 0) if imp_ok else 0, "exportacao": exp.get("total", 0) if exp_ok else 0},
            "tipo_pagamento": {},
            "incoterm": {},
            "tipo_container": {},
            "agentes_carga_nacionais": [],
            "agentes_carga_internacionais": [],
            "agentes_nota": agentes_nota,
            "armazens_destino": [],
            "fonte": "comexstat",
        }
    finally:
        await conn.close()
