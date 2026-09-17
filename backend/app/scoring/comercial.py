"""
Score comercial: atividade, presença digital, telefone/email ativos.
"""
from app.schemas import ScoreResult, ScoreInput
from app.scoring.base import ScoreStrategy

class ScoreComercial(ScoreStrategy):
    nome = "comercial"

    def calcular(self, dados: ScoreInput) -> ScoreResult:
        score = 0.0
        just = []

        if dados.email:
            score += 25
            just.append("Email cadastrado")

        if dados.telefone:
            score += 20
            just.append("Telefone cadastrado")

        if dados.website_url:
            score += 25
            just.append("Website ativo")

        if dados.nome_fantasia:
            score += 10
            just.append("Nome fantasia registrado")

        if dados.situacao_cadastral == "ATIVA":
            score += 20
            just.append("Situação cadastral ativa")

        conf = min(score / 100, 1.0)
        return ScoreResult(
            score_tipo=self.nome,
            score_valor=round(min(score, 100), 1),
            confianca=round(conf, 2),
            justificativa="; ".join(just),
        )
