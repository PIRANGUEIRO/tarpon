import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class BaseCrawler:
    fonte: str = ""

    def rate_limit(self, segundos: float = 1.0):
        time.sleep(segundos)
