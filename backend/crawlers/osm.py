# Mock APIs — troque via .env para endpoints reais
"""
Crawler de geolocalização (OpenStreetMap + Overpass API)
Calcula distância até portos, aeroportos e rodovias principais.
"""

import httpx
import time
import math

from crawlers.base import BaseCrawler, logger

NOMINATIM_URL = "https://api.exemplo.com/nominatim/search"

PORTOS = {
    "Santos": {"lat": -23.9608, "lon": -46.3336},
    "Paranaguá": {"lat": -25.5205, "lon": -48.5063},
    "Itajaí": {"lat": -26.9078, "lon": -48.6618},
    "Rio Grande": {"lat": -32.0350, "lon": -52.0986},
    "Salvador": {"lat": -12.9714, "lon": -38.5124},
    "Suape": {"lat": -8.3950, "lon": -34.9739},
    "Fortaleza": {"lat": -3.7319, "lon": -38.5267},
    "Manaus": {"lat": -3.1190, "lon": -60.0217},
    "Belém": {"lat": -1.4558, "lon": -48.5024},
    "Natal": {"lat": -5.7945, "lon": -35.2110},
    "Maceió": {"lat": -9.6658, "lon": -35.7353},
    "Aracaju": {"lat": -10.9091, "lon": -37.0677},
    "Vitória": {"lat": -20.3233, "lon": -40.3356},
    "São Francisco do Sul": {"lat": -26.2433, "lon": -48.6378},
    "Navegantes": {"lat": -26.8983, "lon": -48.6544},
}

AEROPORTOS = {
    "GRU": {"lat": -23.4356, "lon": -46.4731},
    "CGH": {"lat": -23.6261, "lon": -46.6564},
    "VCP": {"lat": -23.0074, "lon": -47.1344},
    "SDU": {"lat": -22.8090, "lon": -43.1696},
    "GIG": {"lat": -22.8090, "lon": -43.2506},
    "CNF": {"lat": -19.6244, "lon": -43.9719},
    "POA": {"lat": -29.9933, "lon": -51.1711},
    "FLN": {"lat": -27.6703, "lon": -48.5525},
    "REC": {"lat": -8.1320, "lon": -34.9267},
    "SSA": {"lat": -12.9086, "lon": -38.3225},
    "FOR": {"lat": -3.8178, "lon": -38.5200},
    "NAT": {"lat": -5.7681, "lon": -35.3667},
    "CWB": {"lat": -25.5285, "lon": -49.1714},
    "BRA": {"lat": -15.8711, "lon": -47.9186},
    "BSB": {"lat": -15.8711, "lon": -47.9186},
    "MAO": {"lat": -3.0386, "lon": -60.0497},
    "BEL": {"lat": -1.3848, "lon": -48.4778},
    "VIX": {"lat": -20.2528, "lon": -40.2844},
    "AJU": {"lat": -10.9840, "lon": -37.0704},
    "MCZ": {"lat": -9.5108, "lon": -35.7919},
}


class OSMCrawler(BaseCrawler):
    fonte = "osm"

    def geocode(self, municipio: str, uf: str) -> tuple | None:
        """Converte município/UF em coordenadas (lat, lon)."""
        try:
            r = httpx.get(
                NOMINATIM_URL,
                params={
                    "q": f"{municipio}, {uf}, Brasil",
                    "format": "json",
                    "limit": 1,
                },
                headers={"User-Agent": "RadarElite/1.0"},
                timeout=15,
            )
            time.sleep(1)
            if r.status_code == 200 and r.json():
                data = r.json()[0]
                lat, lon = float(data["lat"]), float(data["lon"])
                return lat, lon
        except Exception as e:
            logger.error(f"Erro geocode {municipio}/{uf}: {e}")
        return None, None

    def calcular_distancia(self, lat1, lon1, lat2, lon2) -> float:
        """Distância em km usando Haversine."""
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def enriquecer_empresa(self, municipio: str, uf: str) -> dict | None:
        """Calcula distâncias para portos e aeroportos."""
        lat, lon = self.geocode(municipio, uf)
        if not lat:
            return None

        dist_portos = {}
        for nome, coord in PORTOS.items():
            dist_portos[nome] = round(self.calcular_distancia(lat, lon, coord["lat"], coord["lon"]), 1)

        dist_aeroportos = {}
        for cod, coord in AEROPORTOS.items():
            dist_aeroportos[cod] = round(self.calcular_distancia(lat, lon, coord["lat"], coord["lon"]), 1)

        porto_mais_prox = min(dist_portos, key=dist_portos.get)
        aeroporto_mais_prox = min(dist_aeroportos, key=dist_aeroportos.get)

        return {
            "lat": lat,
            "lon": lon,
            "distancia_porto_mais_proximo_km": dist_portos[porto_mais_prox],
            "porto_mais_proximo": porto_mais_prox,
            "distancia_aeroporto_mais_proximo_km": dist_aeroportos[aeroporto_mais_prox],
            "aeroporto_mais_proximo": aeroporto_mais_prox,
            "distancias_portos": dist_portos,
            "distancias_aeroportos": dist_aeroportos,
        }


if __name__ == "__main__":
    crawler = OSMCrawler()
    resultado = crawler.enriquecer_empresa("Santos", "SP")
    if resultado:
        print(f"  Porto mais próximo: {resultado['porto_mais_proximo']} ({resultado['distancia_porto_mais_proximo_km']} km)")
        print(f"  Aeroporto mais próximo: {resultado['aeroporto_mais_proximo']} ({resultado['distancia_aeroporto_mais_proximo_km']} km)")
