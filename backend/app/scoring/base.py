"""
Base para o motor de scoring.
Cada score implementa a interface ScoreStrategy.
"""
from abc import ABC, abstractmethod
from app.schemas import ScoreResult, ScoreInput

class ScoreStrategy(ABC):
    nome: str = ""

    @abstractmethod
    def calcular(self, dados: ScoreInput) -> ScoreResult:
        ...

class ScoreEngine:
    def __init__(self):
        self.strategies: list[ScoreStrategy] = []

    def registrar(self, strategy: ScoreStrategy):
        self.strategies.append(strategy)

    def calcular_todos(self, dados: ScoreInput) -> list[ScoreResult]:
        resultados = []
        for s in self.strategies:
            try:
                resultados.append(s.calcular(dados))
            except Exception as e:
                resultados.append(ScoreResult(
                    score_tipo=s.nome,
                    score_valor=0.0,
                    confianca=0.0,
                    justificativa=f"Erro: {e}",
                ))
        return resultados

    def score_geral(self, resultados: list[ScoreResult]) -> float:
        if not resultados:
            return 0.0
        from app.config import SCORE_WEIGHTS
        total = 0.0
        for r in resultados:
            peso = SCORE_WEIGHTS.get(r.score_tipo, 0.2)
            total += r.score_valor * peso
        return round(total, 2)
