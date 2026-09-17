"""
Runner para executar todos os crawlers em sequência.
Comandos:
  python -m crawlers.runner all       # Executa todos
  python -m crawlers.runner comextat  # Só Comex Stat
  python -m crawlers.runner geo       # Só OSM
  python -m crawlers.runner website   # Só websites
  python -m crawlers.runner vagas     # Só vagas
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.base import logger

def run_comexstat():
    logger.info("=== Iniciando Comex Stat ===")
    from crawlers.comexstat import ComexStatCrawler
    c = ComexStatCrawler()
    return c

def run_geo():
    logger.info("=== Iniciando OSM/Geo ===")
    from crawlers.osm import OSMCrawler
    return OSMCrawler()

def run_website():
    logger.info("=== Iniciando Websites ===")
    from crawlers.website import WebsiteCrawler
    return WebsiteCrawler()

def run_vagas():
    logger.info("=== Iniciando Vagas ===")
    from crawlers.vagas import VagasCrawler
    return VagasCrawler()

def run_ibge():
    logger.info("=== Iniciando IBGE ===")
    from crawlers.ibge import IBGECrawler
    return IBGECrawler()

RUNNERS = {
    "comexstat": run_comexstat,
    "geo": run_geo,
    "website": run_website,
    "vagas": run_vagas,
    "ibge": run_ibge,
}

if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else ["all"]

    if "all" in args:
        logger.info("Executando TODOS os crawlers...")
        for name, func in RUNNERS.items():
            logger.info(f"\n--- {name} ---")
            try:
                func()
            except Exception as e:
                logger.error(f"Erro em {name}: {e}")
            time.sleep(2)
        logger.info("Todos os crawlers finalizados.")
    else:
        for name in args:
            if name in RUNNERS:
                logger.info(f"\n--- {name} ---")
                RUNNERS[name]()
            else:
                logger.warning(f"Crawler desconhecido: {name}")
