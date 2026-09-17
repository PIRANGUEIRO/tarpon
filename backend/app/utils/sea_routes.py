"""
Utilitário de rotas marítimas reais.
Fornece distâncias reais entre portos usando dados PUB151 (distâncias marítimas).
Baseado em: https://github.com/kaklin/sea-routes e https://github.com/genthalili/searoute-py
"""

import math

# Distâncias marítimas reais entre portos principais (em milhas náuticas)
# Fonte: Distâncias Marítimas PUB151 / MarineTraffic / Sea-distances.org
ROTAS_MARITIMAS = {
    # Rotas Asia → Brasil
    ("Shanghai", "Santos"): 10522,
    ("Shanghai", "Navegantes"): 10789,
    ("Shanghai", "Paranaguá"): 10654,
    ("Shanghai", "Rio de Janeiro"): 10450,
    ("Ningbo", "Santos"): 10445,
    ("Ningbo", "Navegantes"): 10712,
    ("Ningbo", "Itapoá"): 10690,
    ("Shenzhen", "Santos"): 10290,
    ("Shenzhen", "Navegantes"): 10556,
    ("Qingdao", "Santos"): 10680,
    ("Xiamen", "Santos"): 10350,
    ("Busan", "Santos"): 11200,
    ("Singapura", "Santos"): 8720,
    ("Singapura", "Navegantes"): 8986,
    ("Colombo", "Santos"): 8150,

    # Rotas Europa → Brasil
    ("Hamburg", "Santos"): 6250,
    ("Hamburg", "Paranaguá"): 6180,
    ("Antuérpia", "Santos"): 6100,
    ("Rotterdam", "Santos"): 6050,
    ("Rotterdam", "Navegantes"): 6316,

    # Rotas EUA → Brasil
    ("Houston", "Santos"): 5200,
    ("Houston", "Rio de Janeiro"): 5050,
    ("New York", "Santos"): 4780,
    ("New York", "Paranaguá"): 4710,
    ("Savannah", "Santos"): 4350,
    ("Miami", "Santos"): 4100,
    ("Miami", "Manaus"): 2800,

    # Rotas intra-Brasil (costeiras)
    ("Santos", "Navegantes"): 500,
    ("Santos", "Paranaguá"): 280,
    ("Santos", "Rio de Janeiro"): 210,
    ("Santos", "Vitória"): 520,
    ("Santos", "Salvador"): 1160,
    ("Santos", "Suape"): 1620,
    ("Santos", "Manaus"): 2700,
    ("Navegantes", "Paranaguá"): 220,
    ("Rio de Janeiro", "Salvador"): 950,
    ("Salvador", "Suape"): 580,
    ("Salvador", "Manaus"): 1900,
}

# Velocidade média de navio porta-contêiner (nós)
VELOCIDADE_MEDIA_NO = 15.0

# Fator de conversão: 1 milha náutica = 1.852 km
KM_POR_MILHA = 1.852


def distancia_milhas(porto_origem: str, porto_destino: str) -> float | None:
    """Retorna a distância em milhas náutimas entre dois portos."""
    # Tentar direto
    distancia = ROTAS_MARITIMAS.get((porto_origem, porto_destino))
    if distancia:
        return distancia
    # Tentar reverso
    distancia = ROTAS_MARITIMAS.get((porto_destino, porto_origem))
    if distancia:
        return distancia
    return None


def distancia_km(porto_origem: str, porto_destino: str) -> float | None:
    """Retorna a distância em km entre dois portos."""
    milhas = distancia_milhas(porto_origem, porto_destino)
    if milhas:
        return round(milhas * KM_POR_MILHA, 1)
    return None


def tempo_viagem_dias(porto_origem: str, porto_destino: str, velocidade_no: float = VELOCIDADE_MEDIA_NO) -> float | None:
    """Estima o tempo de viagem em dias entre dois portos."""
    milhas = distancia_milhas(porto_origem, porto_destino)
    if milhas:
        horas = milhas / velocidade_no
        return round(horas / 24, 1)
    return None


def estimar_custo_frete(porto_origem: str, porto_destino: str, teus: float = 1.0) -> dict | None:
    """Estima o custo de frete marítimo entre dois portos."""
    milhas = distancia_milhas(porto_origem, porto_destino)
    if not milhas:
        return None

    # Custo médio por TEU por milha náutica (estimativa conservadora)
    # Baseado em: ~$0.05-0.15 por TEU por milha (varia muito)
    custo_por_teu_por_milha = 0.08  # USD
    custo_frete = round(milhas * custo_por_teu_por_milha * teus, 2)

    tempo_dias = tempo_viagem_dias(porto_origem, porto_destino)
    # Custo diário de operação portuária (~$150-300/dia por TEU)
    custo_operacao = round((tempo_dias or 0) * 200 * teus, 2) if tempo_dias else 0

    return {
        "porto_origem": porto_origem,
        "porto_destino": porto_destino,
        "distancia_milhas": milhas,
        "distancia_km": round(milhas * KM_POR_MILHA, 1),
        "tempo_viagem_dias": tempo_dias,
        "custo_frete_usd": custo_frete,
        "custo_operacao_usd": custo_operacao,
        "custo_total_usd": round(custo_frete + custo_operacao, 2),
        "teus": teus,
    }


def rotas_disponiveis(porto: str) -> list:
    """Lista todas as rotas disponíveis para um porto."""
    rotas = []
    for (origem, destino), milhas in ROTAS_MARITIMAS.items():
        if origem == porto or destino == porto:
            outro = destino if origem == porto else origem
            rotas.append({
                "porto": outro,
                "direcao": "origem" if destino == porto else "destino",
                "distancia_milhas": milhas,
                "distancia_km": round(milhas * KM_POR_MILHA, 1),
                "tempo_viagem_dias": tempo_viagem_dias(origem, destino),
            })
    return sorted(rotas, key=lambda x: x["distancia_milhas"])


def todas_rotas() -> list:
    """Lista todas as rotas marítimas com detalhes."""
    resultado = []
    for (origem, destino), milhas in sorted(ROTAS_MARITIMAS.items(), key=lambda x: x[1]):
        resultado.append({
            "origem": origem,
            "destino": destino,
            "distancia_milhas": milhas,
            "distancia_km": round(milhas * KM_POR_MILHA, 1),
            "tempo_viagem_dias": tempo_viagem_dias(origem, destino),
        })
    return resultado


if __name__ == "__main__":
    print("=== Rotas Marítimas ===")
    print(f"Total de rotas mapeadas: {len(ROTAS_MARITIMAS)}")

    testes = [
        ("Shanghai", "Santos"),
        ("Ningbo", "Navegantes"),
        ("Hamburg", "Paranaguá"),
        ("Santos", "Manaus"),
    ]
    for origem, destino in testes:
        info = estimar_custo_frete(origem, destino, teus=1)
        if info:
            print(f"\n  {origem} → {destino}:")
            print(f"    Distância: {info['distancia_milhas']} milhas ({info['distancia_km']} km)")
            print(f"    Tempo: ~{info['tempo_viagem_dias']} dias")
            print(f"    Custo frete: US${info['custo_frete_usd']:,.2f}")
