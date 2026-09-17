"""
Crawler do Comex Stat (API pública do Governo Federal)
Baixa dados de comércio exterior por NCM/município/UF.
Estratégia: usa a API pública MDIC ou carrega CSV.
"""

import httpx
import pandas as pd
import os

from crawlers.base import BaseCrawler, logger

URL_MDIC_API = "https://api.exemplo.com/mdic/comercio-exterior"

class ComexStatCrawler(BaseCrawler):
    fonte = "comex_stat"

    def buscar_dados_uf(self, uf: str, ano: int = 2025, tipo: str = "importacao") -> list[dict]:
        """Busca dados de importação/exportação por UF."""
        try:
            url = f"{URL_MDIC_API}/{tipo}/uf/{uf}/ano/{ano}"
            r = httpx.get(url, timeout=30,
                headers={"User-Agent": "RadarElite/1.0", "Accept": "application/json"})
            if r.status_code == 200:
                dados = r.json()
                return dados
            logger.warning(f"API MDIC sem dados para {uf}/{ano}: {r.status_code}")
            return []
        except Exception as e:
            logger.error(f"Erro MDIC {uf}/{ano}: {e}")
            return []

    def carregar_csv(self, arquivo_csv: str, tipo: str = "importacao") -> list[dict]:
        """Carrega CSV do MDIC e retorna lista de registros."""
        if not os.path.exists(arquivo_csv):
            logger.error(f"Arquivo não encontrado: {arquivo_csv}")
            return []

        logger.info(f"Carregando {tipo}: {arquivo_csv}")
        df = pd.read_csv(arquivo_csv, sep=";", encoding="latin1", dtype=str)

        mapeamento = {
            "CO_NCM": "ncm", "co_ncm": "ncm",
            "NO_MUN_POR": "municipio", "no_mun_por": "municipio",
            "SG_UF_MUN": "uf", "sg_uf_mun": "uf",
            "NO_PAIS": "pais", "no_pais": "pais",
            "VL_FOB": "valor_fob", "vl_fob": "valor_fob",
            "VL_PESO_LIQ": "peso_kg", "vl_peso_liq": "peso_kg",
            "CO_ANO": "ano", "co_ano": "ano",
            "CO_MES": "mes", "co_mes": "mes",
        }

        df.columns = [c.strip() for c in df.columns]
        df = df.rename(columns={k: v for k, v in mapeamento.items() if k in df.columns})

        registros = []
        for _, row in df.iterrows():
            try:
                if pd.isna(row.get("ncm")):
                    continue

                ncm = str(row["ncm"]).strip().zfill(8)[:10]
                uf = str(row.get("uf", "")).strip().upper()[:2] if pd.notna(row.get("uf")) else None

                if uf and len(uf) != 2:
                    uf = None

                registros.append({
                    "ncm": ncm,
                    "municipio": str(row.get("municipio", "")).strip() if pd.notna(row.get("municipio")) else None,
                    "uf": uf,
                    "pais": str(row.get("pais", "")).strip()[:100] if pd.notna(row.get("pais")) else None,
                    "valor_fob": float(row["valor_fob"]) if pd.notna(row.get("valor_fob")) else None,
                    "peso_kg": float(row["peso_kg"]) if pd.notna(row.get("peso_kg")) else None,
                    "ano": int(row["ano"]) if pd.notna(row.get("ano")) else None,
                    "mes": int(row["mes"]) if pd.notna(row.get("mes")) else None,
                })
            except (ValueError, KeyError):
                continue

        logger.info(f"Total: {len(registros)} registros de {tipo}")
        return registros


if __name__ == "__main__":
    c = ComexStatCrawler()
    print("ComexStat Crawler pronto.")
