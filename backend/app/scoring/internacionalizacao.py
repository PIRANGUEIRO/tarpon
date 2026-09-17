"""
Score de internacionalização: nome sugestivo, presença em múltiplos estados/NCMs.
"""
from app.schemas import ScoreResult, ScoreInput
from app.scoring.base import ScoreStrategy

class ScoreInternacionalizacao(ScoreStrategy):
    nome = "internacionalizacao"

    def calcular(self, dados: ScoreInput) -> ScoreResult:
        score = 0.0
        just = []
        nome = (dados.razao_social or "").upper()

        termos_internacional = [
            "IMPORT", "EXPORT", "INTERNACION", "GLOBAL",
            "TRADE", "COMEX", "INTERNATIONAL", "WORLD",
        ]
        for t in termos_internacional:
            if t in nome:
                score += 10
                just.append(f"Nome contém '{t}'")
                break

        if dados.cnaes_secundarios and len(dados.cnaes_secundarios) > 3:
            score += 10
            just.append("Diversidade de CNAEs")

        if dados.capital_social and dados.capital_social > 1000000:
            score += 10

        if dados.comexstat:
            score += 15
            just.append("Município com atividade de importação")

        conf = min(score / 55, 1.0)
        return ScoreResult(
            score_tipo=self.nome,
            score_valor=round(min(score, 100), 1),
            confianca=round(conf, 2),
            justificativa="; ".join(just),
        )
