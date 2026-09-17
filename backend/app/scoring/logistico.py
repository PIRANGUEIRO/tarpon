"""
Score logístico: proximidade de portos e aeroportos.
"""
from app.schemas import ScoreResult, ScoreInput
from app.scoring.base import ScoreStrategy

class ScoreLogistico(ScoreStrategy):
    nome = "logistico"

    def calcular(self, dados: ScoreInput) -> ScoreResult:
        if not dados.geo or not dados.geo.distancia_porto_km:
            return ScoreResult(
                score_tipo=self.nome, score_valor=0, confianca=0,
                justificativa="Sem dados geográficos"
            )

        score = 0.0
        just = []

        d_porto = dados.geo.distancia_porto_km
        d_aero = dados.geo.distancia_aeroporto_km or 999

        if d_porto < 10:
            score += 40
            just.append(f"A {d_porto:.0f}km do porto")
        elif d_porto < 50:
            score += 25
            just.append(f"A {d_porto:.0f}km do porto")
        elif d_porto < 150:
            score += 15
            just.append(f"A {d_porto:.0f}km do porto")
        else:
            score += 5

        if d_aero and d_aero < 20:
            score += 20
            just.append(f"A {d_aero:.0f}km do aeroporto")
        elif d_aero and d_aero < 80:
            score += 10

        if d_porto < 100 and d_aero and d_aero < 50:
            score += 15
            just.append("Próximo de porto e aeroporto")

        conf = min(score / 75, 1.0)
        return ScoreResult(
            score_tipo=self.nome,
            score_valor=round(min(score, 100), 1),
            confianca=round(conf, 2),
            justificativa="; ".join(just),
        )
