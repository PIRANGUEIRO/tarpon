import math

PORTOS_BR = {
    "Santos": (-23.9650, -46.3169),
    "Paranaguá": (-25.5167, -48.5167),
    "Itajaí": (-26.9000, -48.6667),
    "Rio Grande": (-32.0333, -52.0833),
    "São Francisco do Sul": (-26.2500, -48.6333),
    "Suape": (-8.3833, -34.9667),
    "Salvador": (-12.9667, -38.5167),
    "Manaus": (-3.1333, -60.0167),
    "Rio de Janeiro": (-22.9000, -43.2000),
    "Vitória": (-20.3167, -40.3333),
}

AEROPORTOS_BR = {
    "GRU": (-23.4356, -46.4731),
    "GIG": (-22.8093, -43.2431),
    "BSB": (-15.8697, -47.9208),
    "VCP": (-23.0078, -47.1344),
    "CNF": (-19.6244, -43.9719),
    "POA": (-29.9944, -51.1714),
    "REC": (-8.1264, -34.9236),
    "FOR": (-3.7764, -38.5322),
    "CWB": (-25.5285, -49.1757),
    "FLN": (-27.6700, -48.5483),
}

def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)

def distancia_portos(lat, lon) -> dict:
    return {nome: haversine(lat, lon, *coord) for nome, coord in PORTOS_BR.items()}

def distancia_aeroportos(lat, lon) -> dict:
    return {cod: haversine(lat, lon, *coord) for cod, coord in AEROPORTOS_BR.items()}

def porto_mais_proximo(lat, lon) -> tuple[str, float]:
    dists = distancia_portos(lat, lon)
    nome = min(dists, key=dists.get)
    return nome, dists[nome]

def aeroporto_mais_proximo(lat, lon) -> tuple[str, float]:
    dists = distancia_aeroportos(lat, lon)
    cod = min(dists, key=dists.get)
    return cod, dists[cod]


def distancia_mais_proxima(lat: float, lon: float, tipo: str = "portos") -> tuple[float, str]:
    if tipo == "portos":
        dists = {nome: haversine(lat, lon, *coord) for nome, coord in PORTOS_BR.items()}
    else:
        dists = {cod: haversine(lat, lon, *coord) for cod, coord in AEROPORTOS_BR.items()}
    nome = min(dists, key=dists.get)
    return dists[nome], nome
