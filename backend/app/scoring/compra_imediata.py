"""
Score de compra imediata: empresa que parece pronta para importar.
Combina: CNAE + capital social + site com produtos + proximidade logística.
"""
from app.schemas import ScoreResult, ScoreInput
from app.scoring.base import ScoreStrategy

class ScoreCompraImediata(ScoreStrategy):
    nome = "compra_imediata"

    def calcular(self, dados: ScoreInput) -> ScoreResult:
        score = 0.0
        just = []

        if dados.website and dados.website.produtos:
            score += 25
            just.append("Site com produtos")

        if dados.capital_social and dados.capital_social > 200000:
            score += 20
            just.append("Capital social > R$200k")

        cnae_div = (dados.cnae_principal or "")[:2]
        cnaes_alta = ["46", "47", "20", "21", "26"]
        if cnae_div in cnaes_alta:
            score += 20
            just.append(f"CNAE {cnae_div} de alta prioridade")

        if dados.geo and dados.geo.distancia_porto_km and dados.geo.distancia_porto_km < 50:
            score += 20
            just.append("Próximo de porto (logística favorável)")

        if dados.website and dados.website.termos_importacao:
            score += 15
            just.append("Site menciona importação")

        conf = min(score / 100, 1.0)
        return ScoreResult(
            score_tipo=self.nome,
            score_valor=round(min(score, 100), 1),
            confianca=round(conf, 2),
            justificativa="; ".join(just),
        )
