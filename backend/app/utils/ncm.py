"""
Utilitário de classificação NCM/HS Code.
Fornece descrições e hierarquia para códigos NCM brasileiros.
Baseado no padrão do Sistema Harmonizado (HS) da OMA.
"""

# Capítulos HS (2 dígitos) — principais para Comex Brasil
CAPITULOS_HS = {
    "01": "Animais vivos",
    "02": "Carnes e miudezas comestíveis",
    "03": "Peixes e crustáceos, moluscos",
    "04": "Laticínios, ovos, mel",
    "05": "Outros produtos de origem animal",
    "06": "Plantas vivas e flores",
    "07": "Hortaliças, plantas, raízes",
    "08": "Frutas, nozes, cascas de frutas",
    "09": "Café, chá, especiarias",
    "10": "Cereais",
    "11": "Produtos da moagem",
    "12": "Oleaginosas e sementes",
    "13": "Gomas, resinas",
    "14": "Matérias para entrançar",
    "15": "Gorduras e óleos animais/vegetais",
    "16": "Preparações de carne, peixe",
    "17": "Açúcares e confeitaria",
    "18": "Cacau e suas preparações",
    "19": "Preparações de cereais",
    "20": "Preparações de legumes, frutas",
    "21": "Diversos alimentos preparados",
    "22": "Bebidas, líquidos alcoólicos",
    "23": "Resíduos da indústria alimentar",
    "24": "Tabaco e seus substitutos",
    "25": "Sal, enxofre, terras, pedras",
    "26": "Minérios, escórias e cinzas",
    "27": "Combustíveis minerais, óleos",
    "28": "Produtos químicos inorgânicos",
    "29": "Produtos químicos orgânicos",
    "30": "Produtos farmacêuticos",
    "31": "Adubos e fertilizantes",
    "32": "Corantes, tintas, vernizes",
    "33": "Óleos essenciais, perfumes",
    "34": "Sabões, detergentes",
    "35": "Albuminas, amidos, cola",
    "36": "Explosivos, fogos de artifício",
    "37": "Fotografia e cinematografia",
    "38": "Diversos produtos químicos",
    "39": "Plásticos e obras de plástico",
    "40": "Borracha e obras de borracha",
    "41": "Couro e peles curtidas",
    "42": "Obras de couro",
    "43": "Peles curtidas e pelo",
    "44": "Madeira e obras de madeira",
    "45": "Cortiça e obras de cortiça",
    "46": "Obras de esparto, fibras",
    "47": "Pastas de madeira",
    "48": "Papel e cartão",
    "49": "Livros, jornais, gravuras",
    "50": "Seda",
    "51": "Lã, pelos de animais",
    "52": "Algodão",
    "53": "Outras fibras têxteis",
    "54": "Fibras sintéticas",
    "55": "Fibras artificiais",
    "56": "Tecidos não tecidos",
    "57": "Tapetes e outros revestimentos",
    "58": "Tecidos especiais",
    "59": "Tecidos impregnados",
    "60": "Tecidos de malha",
    "61": "Vestuário de malha",
    "62": "Vestuário não de malha",
    "63": "Outros artefatos têxteis",
    "64": "Calçados, partes",
    "65": "Chapéus e partes",
    "66": "Guarda-chuas, bengalas",
    "67": "Penas e artigos de penas",
    "68": "Obras de pedra, cimento",
    "69": "Produtos cerâmicos",
    "70": "Vidro e obras de vidro",
    "71": "Pérolas, pedras preciosas, metais preciosos",
    "72": "Ferro e aço",
    "73": "Obras de ferro ou aço",
    "74": "Cobre e obras de cobre",
    "75": "Níquel e obras de níquel",
    "76": "Alumínio e obras de alumínio",
    "77": "Reservado",
    "78": "Chumbo e obras de chumbo",
    "79": "Zinco e obras de zinco",
    "80": "Estanho e obras de estanho",
    "81": "Outros metais",
    "82": "Ferramentas de metais",
    "83": "Obras diversas de metais",
    "84": "Máquinas, aparelhos mecânicos",
    "85": "Máquinas, aparelhos elétricos",
    "86": "Material para vias férreas",
    "87": "Veículos terrestres",
    "88": "Aeronaves, foguetes",
    "89": "Embarcações",
    "90": "Instrumentos ópticos, fotográficos",
    "91": "Relógios",
    "92": "Instrumentos musicais",
    "93": "Armas e munições",
    "94": "Móveis, colchões",
    "95": "Brinquedos, jogos, artigos esportivos",
    "96": "Obras diversas",
    "97": "Obras de arte, antiguidades",
}

# Posições NCM (4 dígitos) — principais para importação Brasil
POSICOES_MAIS_IMPORTADAS = {
    "8471": "Máquinas de processamento de dados (computadores)",
    "8703": "Automóveis de passageiros",
    "2709": "Petróleo cru",
    "8411": "Turbojatos, turbopropulsores",
    "8517": "Aparelhos telefônicos (smartphones)",
    "8467": "Ferramentas pneumáticas, hidráulicas",
    "8541": "Semicondutores, células fotovoltaicas",
    "8708": "Partes e acessórios de veículos",
    "3004": "Medicamentos preparados",
    "8473": "Partes de máquinas de processamento",
    "8528": "Aparelhos de recepção de TV",
    "3926": "Obras de plástico",
    "7318": "Parafusos, porcas de ferro/ aço",
    "8481": "Torrneiras, válvulas",
    "3917": "Tubos de plástico",
    "4011": "Pneumáticos novos de borracha",
    "7604": "Perfis de alumínio",
    "7304": "Tubos de aço sem costura",
    "8431": "Partes de máquinas de levantamento",
    "8483": "Transmissões, engrenagens",
}


def descricao_capitulo(ncm: str) -> str:
    """Retorna a descrição do capítulo HS (2 dígitos)."""
    if not ncm or len(ncm) < 2:
        return "Código NCM inválido"
    capitulo = ncm[:2]
    return CAPITULOS_HS.get(capitulo, f"Capítulo {capitulo} não mapeado")


def descricao_posicao(ncm: str) -> str:
    """Retorna a descrição da posição NCM (4 dígitos)."""
    if not ncm or len(ncm) < 4:
        return descricao_capitulo(ncm)
    posicao = ncm[:4]
    return POSICOES_MAIS_IMPORTADAS.get(posicao, descricao_capitulo(ncm))


def classificar_produto(ncm: str) -> dict:
    """Classifica um produto pelo código NCM."""
    if not ncm:
        return {"ncm": "", "capitulo": "", "posicao": "", "descricao": "Não informado"}

    ncm_clean = ncm.strip().zfill(8)[:10]
    return {
        "ncm": ncm_clean,
        "capitulo": ncm_clean[:2],
        "posicao": ncm_clean[:4],
        "descricao_capitulo": descricao_capitulo(ncm_clean),
        "descricao_posicao": descricao_posicao(ncm_clean),
    }


def calcular_rca(importacoes_pais: float, importacoes_mundo: float) -> float:
    """
    Calcula a Revealed Comparative Advantage (RCA / Índice de Balassa).
    RCA > 1 significa que o país tem vantagem comparativa no produto.
    """
    if importacoes_mundo == 0:
        return 0.0
    return round(importacoes_pais / importacoes_mundo, 4)


def ncm_todos_capitulos() -> list:
    """Retorna todos os capítulos HS com descrição."""
    return [{"codigo": k, "descricao": v} for k, v in sorted(CAPITULOS_HS.items())]


if __name__ == "__main__":
    # Teste
    print("=== Classificador NCM ===")
    testes = ["84713000", "8703", "4011", "9999"]
    for ncm in testes:
        r = classificar_produto(ncm)
        print(f"  {ncm}: {r['descricao_posicao']}")

    print(f"\nTotal de capítulos mapeados: {len(CAPITULOS_HS)}")
    print(f"Posições principais mapeadas: {len(POSICOES_MAIS_IMPORTADAS)}")
