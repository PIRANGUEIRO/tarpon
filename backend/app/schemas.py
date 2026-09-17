from datetime import datetime, date
from pydantic import BaseModel, Field
from typing import Optional

# ─── Empresa ───────────────────────────────────────────────────────

class EmpresaBase(BaseModel):
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnae_principal: Optional[str] = None
    cnaes_secundarios: Optional[list] = None
    capital_social: Optional[float] = None
    porte: Optional[str] = None
    situacao_cadastral: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    data_abertura: Optional[date] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    bairro: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaResponse(EmpresaBase):
    id: int
    score_importacao: Optional[float] = None
    score_comercial: Optional[float] = None
    score_logistico: Optional[float] = None
    score_internacionalizacao: Optional[float] = None
    score_compra_imediata: Optional[float] = None
    pib_per_capita: Optional[float] = None
    populacao: Optional[int] = None
    website_produtos: Optional[str] = None
    website_marcas: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class EmpresaBusca(BaseModel):
    total: int
    empresas: list[EmpresaResponse]

# ─── Comex Stat ────────────────────────────────────────────────────

class ComexStatBase(BaseModel):
    ncm: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    pais: Optional[str] = None
    valor_fob: Optional[float] = None
    peso_kg: Optional[float] = None
    ano: Optional[int] = None
    mes: Optional[int] = None
    via: Optional[str] = None

class ComexStatResponse(ComexStatBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

# ─── Geo ───────────────────────────────────────────────────────────

class GeoResponse(BaseModel):
    municipio: Optional[str] = None
    uf: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    distancia_porto_km: Optional[float] = None
    porto_mais_proximo: Optional[str] = None
    distancia_aeroporto_km: Optional[float] = None
    aeroporto_mais_proximo: Optional[str] = None
    enriquecido: bool = False

# ─── Website ───────────────────────────────────────────────────────

class WebsiteResponse(BaseModel):
    empresa_id: int
    url: Optional[str] = None
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    produtos: Optional[str] = None
    marcas: Optional[str] = None
    keywords: Optional[str] = None
    termos_importacao: Optional[str] = None
    e_importador: Optional[bool] = None
    score_heuristica: Optional[float] = None

# ─── Scoring ───────────────────────────────────────────────────────

class ScoreInput(BaseModel):
    empresa_id: int
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cnae_principal: Optional[str] = None
    cnaes_secundarios: Optional[list] = None
    capital_social: Optional[float] = None
    porte: Optional[str] = None
    situacao_cadastral: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    website_url: Optional[str] = None
    geo: Optional[GeoResponse] = None
    website: Optional[WebsiteResponse] = None
    comexstat: Optional[list[ComexStatResponse]] = None

class ScoreResult(BaseModel):
    score_tipo: str
    score_valor: float
    confianca: float
    justificativa: str

class ScoreBatchResult(BaseModel):
    empresa_id: int
    scores: list[ScoreResult]
    score_geral: float

# ─── Embarques ─────────────────────────────────────────────────────

class EmbarqueResponse(BaseModel):
    id: int
    empresa_id: Optional[int] = None
    cnpj_consignatario: Optional[str] = None
    consignatario: Optional[str] = None
    ncm: str
    descricao_mercadoria: Optional[str] = None
    pais_origem: str
    pais_destino: str
    porto_origem: Optional[str] = None
    porto_destino: Optional[str] = None
    tipo_embarque: str
    tipo_pagamento: str
    incoterm: str
    peso_kg: float
    volume_m3: Optional[float] = None
    teus: Optional[float] = None
    containers: Optional[int] = None
    tipo_container: Optional[str] = None
    tipo_carga: Optional[str] = None
    agente_carga: Optional[str] = None
    armador: Optional[str] = None
    linha_aerea: Optional[str] = None
    aeroporto_destino: Optional[str] = None
    aeroporto_origem: Optional[str] = None
    data_embarque: date
    valor_fob: Optional[float] = None
    modal: str

    model_config = {"from_attributes": True}

class EmbarqueResumo(BaseModel):
    total_embarques: int
    peso_bruto_ton: float
    total_teus: float
    total_containers: int
    valor_fob_total: float
    direto: int = 0
    house: int = 0
    coloader: int = 0
    master: int = 0
    collect: int = 0
    prepaid: int = 0
    fob: int = 0
    exw: int = 0
    cfr: int = 0
    cif: int = 0
    por_modal: dict = {}

class EmbarqueTipoEmbarque(BaseModel):
    tipo: str
    quantidade: int
    percentual: float

class EmbarquePagamento(BaseModel):
    tipo: str
    quantidade: int
    percentual: float

class EmbarqueIncoterm(BaseModel):
    incoterm: str
    quantidade: int
    percentual: float

class EmbarqueMes(BaseModel):
    mes: str
    quantidade: int
    peso_ton: float
    teus: float

# ─── Crawler Runner ────────────────────────────────────────────────

class CrawlerRunResult(BaseModel):
    status: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    mensagem: Optional[str] = None
