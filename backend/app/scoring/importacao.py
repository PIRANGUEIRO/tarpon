"""
Score de potencial importador.
Base: CNAE compatível, capital social, porte, presença de website.
"""
from app.schemas import ScoreResult, ScoreInput
from app.scoring.base import ScoreStrategy

class ScoreImportacao(ScoreStrategy):
    nome = "importacao"

    def calcular(self, dados: ScoreInput) -> ScoreResult:
        score = 0.0
        justificativas = []

        cnaes_importacao = ["46", "47", "29", "20", "21", "26", "28"]
        cnae_div = (dados.cnae_principal or "")[:2]
        if cnae_div in cnaes_importacao:
            score += 30
            justificativas.append(f"CNAE {cnae_div} compatível com importação")

        if dados.capital_social and dados.capital_social > 500000:
            score += 15
            justificativas.append("Capital social elevado")
        elif dados.capital_social and dados.capital_social > 100000:
            score += 5

        if dados.porte in ["DEMAIS", "MEDIO", "GRANDE"]:
            score += 10
            justificativas.append(f"Porte {dados.porte}")

        if dados.website_url:
            score += 10
            justificativas.append("Possui website")

        if dados.website and dados.website.termos_importacao:
            score += 25
            justificativas.append("Site com termos de importação")

        confianca = min(score / 100, 1.0)
        return ScoreResult(
            score_tipo=self.nome,
            score_valor=round(min(score, 100), 1),
            confianca=round(confianca, 2),
            justificativa="; ".join(justificativas),
        )
