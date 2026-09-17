"""
Testes para o motor de scoring.
"""
import pytest
from app.scoring import ScoreEngine
from app.scoring.importacao import ScoreImportacao
from app.scoring.comercial import ScoreComercial
from app.scoring.logistico import ScoreLogistico
from app.scoring.internacionalizacao import ScoreInternacionalizacao
from app.scoring.compra_imediata import ScoreCompraImediata

def test_score_engine_register():
    engine = ScoreEngine()
    engine.registrar(ScoreImportacao())
    engine.registrar(ScoreComercial())
    assert len(engine.strategies) == 2

def test_score_engine_geral():
    from app.schemas import ScoreResult
    resultados = [
        ScoreResult(score_tipo="importacao", score_valor=80, confianca=0.8, justificativa=""),
        ScoreResult(score_tipo="comercial", score_valor=60, confianca=0.6, justificativa=""),
        ScoreResult(score_tipo="logistico", score_valor=40, confianca=0.4, justificativa=""),
        ScoreResult(score_tipo="internacionalizacao", score_valor=50, confianca=0.5, justificativa=""),
        ScoreResult(score_tipo="compra_imediata", score_valor=70, confianca=0.7, justificativa=""),
    ]
    engine = ScoreEngine()
    geral = engine.score_geral(resultados)
    assert 0 <= geral <= 100
