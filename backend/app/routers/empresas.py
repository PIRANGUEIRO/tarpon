from fastapi import APIRouter, Query
from typing import Optional
from connectors.brasilapi import BrasilAPIConnector
from connectors.receitaws import ReceitaWSConnector

router = APIRouter(prefix="/api/empresas", tags=["Empresas"])


def _normalize_cnpj(cnpj: str) -> str:
    return cnpj.replace(".", "").replace("/", "").replace("-", "").strip()


@router.get("/cnpj/{cnpj}")
async def get_by_cnpj(cnpj: str):
    cnpj_norm = _normalize_cnpj(cnpj)
    if len(cnpj_norm) != 14:
        return {"erro": "CNPJ inválido", "cnpj": cnpj}

    brasilapi = BrasilAPIConnector()
    try:
        data = await brasilapi.cached_fetch({"cnpj": cnpj_norm})
        if data:
            return {
                "fonte": "brasilapi",
                "cnpj": data.get("cnpj", cnpj_norm),
                "razao_social": data.get("razao_social", ""),
                "nome_fantasia": data.get("nome_fantasia", ""),
                "cnae_principal": data.get("cnae_fiscal_principal", ""),
                "cnae_descricao": data.get("cnae_fiscal_descricao", ""),
                "capital_social": data.get("capital_social"),
                "porte": data.get("porte", ""),
                "situacao_cadastral": data.get("situacao_cadastral", ""),
                "natureza_juridica": data.get("natureza_juridica", ""),
                "municipio": data.get("municipio", ""),
                "uf": data.get("uf", ""),
                "cep": data.get("cep", ""),
                "logradouro": data.get("logradouro", ""),
                "numero": data.get("numero", ""),
                "bairro": data.get("bairro", ""),
                "telefone": data.get("telefone1", ""),
                "email": data.get("email1", ""),
                "data_abertura": data.get("data_abertura", ""),
                "socios": data.get("qsa", []),
            }
    finally:
        await brasilapi.close()

    receitaws = ReceitaWSConnector()
    try:
        data = await receitaws.cached_fetch({"cnpj": cnpj_norm})
        if data:
            return {
                "fonte": "receitaws",
                "cnpj": data.get("cnpj", cnpj_norm),
                "razao_social": data.get("nome", ""),
                "nome_fantasia": data.get("fantasia", ""),
                "cnae_principal": data.get("cnae", ""),
                "capital_social": float(data.get("capital_social", 0) or 0),
                "porte": data.get("porte", ""),
                "situacao_cadastral": data.get("situacao", ""),
                "municipio": data.get("municipio", ""),
                "uf": data.get("uf", ""),
                "cep": data.get("cep", ""),
                "telefone": data.get("telefone", ""),
                "email": data.get("email", ""),
                "data_abertura": data.get("abertura", ""),
                "socios": data.get("qsa", []),
            }
    finally:
        await receitaws.close()

    return {"erro": "CNPJ não encontrado em nenhuma fonte", "cnpj": cnpj_norm}


@router.get("/busca")
async def buscar(
    q: Optional[str] = Query(None),
    uf: Optional[str] = Query(None, max_length=2),
):
    if not q:
        return {"erro": "Parâmetro 'q' obrigatório", "total": 0, "empresas": []}

    brasilapi = BrasilAPIConnector()
    try:
        data = await brasilapi.cached_fetch({"q": q, "uf": uf or ""})
        if data and isinstance(data, list):
            return {"total": len(data), "empresas": data}
    except Exception:
        pass
    finally:
        await brasilapi.close()

    return {"total": 0, "empresas": [], "nota": "Busca por nome requer BD local ou API de busca"}
