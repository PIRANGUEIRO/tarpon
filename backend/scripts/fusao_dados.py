#!/usr/bin/env python3
"""
Fusão de Dados - Radar de Elite
Cruza dados de múltiplas fontes para criar base completa de importadores/exportadores.

Fontes:
1. Receita Federal (CNPJ, CNAE, endereço, situação)
2. ComexStat (NCM, UF, valor FOB, peso)
3. DNA Paraguai (importadores paraguaios)
4. USASpending (manifestos EUA)
5. Dados internacionais (China, Índia, Malásia, Taiwan)

Cruzamento:
- RF + ComexStat: Empresas com atividade de comércio exterior
- RF + CNAE: Filtrar empresas potenciais importadoras/exportadoras
- ComexStat + NCM: Identificar produtos por estado
- Dados internacionais: Complementar com exportadores globais
"""

import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CNAEs compatíveis com comércio exterior
CNAES_IMPORTACAO = {
    "46": "Comércio atacadista",
    "47": "Comércio varejista",
    "29": "Fabricação de automóveis",
    "20": "Fabricação de produtos de metal",
    "21": "Fabricação de produtos farmacêuticos",
    "26": "Fabricação de equipamentos de informática",
    "28": "Fabricação de máquinas e equipamentos",
    "10": "Fabricação de produtos alimentícios",
    "11": "Fabricação de bebidas",
    "13": "Fabricação de têxteis",
    "14": "Confecção de artigos do vestuário",
    "22": "Fabricação de produtos de borracha e plástico",
    "23": "Fabricação de produtos de minério não metálico",
    "24": "Metalurgia",
    "25": "Fabricação de produtos de metal",
    "27": "Fabricação de máquinas e equipamentos",
    "31": "Fabricação de móveis",
    "32": "Outras indústrias",
    "33": "Manutenção e reparação",
    "52": "Armazenamento e atividades auxiliares do transporte",
    "53": "Atividades de entrega rápida",
    "49": "Transporte terrestre",
    "50": "Transporte aquaviário",
    "51": "Transporte aéreo",
    "61": "Transporte marítimo",
    "62": "Transporte ferroviário",
}

# Países de interesse (exportadores para Brasil)
PAISES_INTERESSE = {
    "156": "China",
    "699": "Índia",
    "458": "Malásia",
    "490": "Taiwan",
    "842": "EUA",
    "276": "Alemanha",
    "392": "Japão",
    "410": "Coreia do Sul",
    "826": "Reino Unido",
    "250": "França",
}


def carregar_empresas_rf(diretorio):
    """Carrega empresas da Receita Federal (CSVs Estabelecimentos)."""
    empresas = {}
    
    for csv_file in sorted(Path(diretorio).glob("Estabelecimentos*.csv")):
        print(f"  Carregando {csv_file.name}...")
        try:
            with open(csv_file, "r", encoding="latin-1") as f:
                reader = csv.reader(f, delimiter=";")
                for row in reader:
                    if len(row) < 20:
                        continue
                    
                    cnpj_basico = row[0].strip()
                    cnpj_ord = row[1].strip()
                    cnpj_dv = row[2].strip()
                    cnpj = f"{cnpj_basico}{cnpj_ord}{cnpj_dv}"
                    
                    # Identificador da matriz/filial
                    ident = row[3].strip()
                    
                    # Nome fantasia
                    nome_fantasia = row[4].strip() if len(row) > 4 else ""
                    
                    # Situação cadastral
                    situacao = row[5].strip() if len(row) > 5 else ""
                    
                    # Data situação cadastral
                    data_sit = row[6].strip() if len(row) > 6 else ""
                    
                    # Motivo situação
                    motivo = row[7].strip() if len(row) > 7 else ""
                    
                    # Nome da cidade no exterior
                    cidade_ext = row[8].strip() if len(row) > 8 else ""
                    
                    # País
                    pais = row[9].strip() if len(row) > 9 else ""
                    
                    # Atividade principal
                    atividade = row[10].strip() if len(row) > 10 else ""
                    
                    # Telefone 1
                    tel1 = row[11].strip() if len(row) > 11 else ""
                    
                    # Telefone 2
                    tel2 = row[12].strip() if len(row) > 12 else ""
                    
                    # Fax
                    fax = row[13].strip() if len(row) > 13 else ""
                    
                    # Email
                    email = row[14].strip() if len(row) > 14 else ""
                    
                    # Endereço
                    logradouro = row[15].strip() if len(row) > 15 else ""
                    numero = row[16].strip() if len(row) > 16 else ""
                    complemento = row[17].strip() if len(row) > 17 else ""
                    bairro = row[18].strip() if len(row) > 18 else ""
                    cep = row[19].strip() if len(row) > 19 else ""
                    
                    # Município
                    municipio = row[20].strip() if len(row) > 20 else ""
                    
                    # UF
                    uf = row[21].strip() if len(row) > 21 else ""
                    
                    # DDD 1
                    ddd1 = row[22].strip() if len(row) > 22 else ""
                    
                    # DDD 2
                    ddd2 = row[23].strip() if len(row) > 23 else ""
                    
                    # CNAE fiscal principal
                    cnae = row[24].strip() if len(row) > 24 else ""
                    
                    # CNAEs secundários
                    cnaes_sec = row[25].strip() if len(row) > 25 else ""
                    
                    # Capital social (da empresa, não do estabelecimento)
                    # Este campo não está no CSV de estabelecimentos
                    
                    empresas[cnpj] = {
                        "cnpj": cnpj,
                        "cnpj_basico": cnpj_basico,
                        "razao_social": "",  # Vem do CSV Empresas
                        "nome_fantasia": nome_fantasia,
                        "situacao_cadastral": situacao,
                        "data_abertura": "",
                        "cnae_principal": cnae,
                        "cnaes_secundarios": cnaes_sec,
                        "logradouro": logradouro,
                        "numero": numero,
                        "complemento": complemento,
                        "bairro": bairro,
                        "cep": cep,
                        "municipio": municipio,
                        "uf": uf,
                        "telefone": f"({ddd1}) {tel1}" if ddd1 and tel1 else tel1,
                        "email": email,
                        "capital_social": 0.0,
                        "porte": "",
                        "natureza_juridica": "",
                    }
        except Exception as e:
            print(f"  Erro ao ler {csv_file.name}: {e}")
    
    return empresas


def carregar_empresas_basicas(diretorio):
    """Carrega dados básicos das empresas (razão social, capital social, porte)."""
    empresas_basicas = {}
    
    for csv_file in sorted(Path(diretorio).glob("Empresas*.csv")):
        print(f"  Carregando {csv_file.name}...")
        try:
            with open(csv_file, "r", encoding="latin-1") as f:
                reader = csv.reader(f, delimiter=";")
                for row in reader:
                    if len(row) < 8:
                        continue
                    
                    cnpj_basico = row[0].strip()
                    razao_social = row[1].strip() if len(row) > 1 else ""
                    capital_social = row[4].strip() if len(row) > 4 else "0"
                    porte = row[5].strip() if len(row) > 5 else ""
                    natureza = row[6].strip() if len(row) > 6 else ""
                    data_abertura = row[7].strip() if len(row) > 7 else ""
                    
                    try:
                        capital = float(capital_social.replace(",", "."))
                    except:
                        capital = 0.0
                    
                    empresas_basicas[cnpj_basico] = {
                        "razao_social": razao_social,
                        "capital_social": capital,
                        "porte": porte,
                        "natureza_juridica": natureza,
                        "data_abertura": data_abertura,
                    }
        except Exception as e:
            print(f"  Erro ao ler {csv_file.name}: {e}")
    
    return empresas_basicas


def carregar_comexstat(diretorio):
    """Carrega dados do ComexStat."""
    comex = []
    
    for csv_file in sorted(Path(diretorio).glob("*.csv")):
        if "MUN" in csv_file.name:
            continue  # Pular arquivos por município por agora
        
        print(f"  Carregando {csv_file.name}...")
        try:
            with open(csv_file, "r", encoding="latin-1") as f:
                reader = csv.reader(f, delimiter=";")
                header = next(reader, None)  # Pular header
                
                for row in reader:
                    if len(row) < 10:
                        continue
                    
                    comex.append({
                        "ano": row[0].strip() if len(row) > 0 else "",
                        "mes": row[1].strip() if len(row) > 1 else "",
                        "ncm": row[2].strip() if len(row) > 2 else "",
                        "unidade": row[3].strip() if len(row) > 3 else "",
                        "pais": row[4].strip() if len(row) > 4 else "",
                        "uf": row[5].strip() if len(row) > 5 else "",
                        "via": row[6].strip() if len(row) > 6 else "",
                        "urf": row[7].strip() if len(row) > 7 else "",
                        "quantidade_estat": row[8].strip() if len(row) > 8 else "",
                        "peso_kg": row[9].strip() if len(row) > 9 else "",
                        "valor_fob": row[10].strip() if len(row) > 10 else "",
                        "frete": row[11].strip() if len(row) > 11 else "",
                        "seguro": row[12].strip() if len(row) > 12 else "",
                    })
        except Exception as e:
            print(f"  Erro ao ler {csv_file.name}: {e}")
    
    return comex


def cruzar_rf_comex(empresas, comex):
    """Cruza empresas RF com dados ComexStat por UF e CNAE."""
    # Agrupar comex por UF
    comex_por_uf = defaultdict(lambda: defaultdict(lambda: {"valor": 0, "peso": 0, "qtd": 0}))
    
    for reg in comex:
        uf = reg["uf"]
        ncm = reg["ncm"][:4]  # Posição SH (4 dígitos)
        
        try:
            valor = float(reg["valor_fob"].replace(",", "."))
            peso = float(reg["peso_kg"].replace(",", "."))
        except:
            continue
        
        comex_por_uf[uf][ncm]["valor"] += valor
        comex_por_uf[uf][ncm]["peso"] += peso
        comex_por_uf[uf][ncm]["qtd"] += 1
    
    # Enriquecer empresas com dados ComexStat
    empresas_enriquecidas = []
    
    for cnpj, emp in empresas.items():
        uf = emp["uf"]
        cnae = emp["cnae_principal"][:2] if emp["cnae_principal"] else ""
        
        # Verificar se CNAE é compatível com comércio exterior
        if cnae not in CNAES_IMPORTACAO:
            continue
        
        # Verificar se empresa está ativa
        if emp["situacao_cadastral"] not in ["02", "Ativa", "ATIVA", ""]:
            continue
        
        # Buscar dados ComexStat para a UF
        comex_uf = comex_por_uf.get(uf, {})
        
        # Calcular score baseado em dados reais
        score = 0
        if comex_uf:
            # Bonus por UF com atividade comex
            score += min(len(comex_uf) * 2, 30)  # Max 30 pontos
            
            # Bonus por capital social
            if emp.get("capital_social", 0) > 500000:
                score += 15
            elif emp.get("capital_social", 0) > 100000:
                score += 10
            
            # Bonus por ter email/site
            if emp.get("email"):
                score += 10
        
        empresas_enriquecidas.append({
            **emp,
            "score_potencial": min(score, 100),
            "comex_uf_ncms": len(comex_uf),
            "comex_uf_valor_total": sum(v["valor"] for v in comex_uf.values()),
        })
    
    # Ordenar por score
    empresas_enriquecidas.sort(key=lambda x: x["score_potencial"], reverse=True)
    
    return empresas_enriquecidas


def salvar_resultados(empresas, diretorio_saida):
    """Salva resultados da fusão."""
    os.makedirs(diretorio_saida, exist_ok=True)
    
    # Salvar CSV completo
    csv_path = os.path.join(diretorio_saida, "empresas_fusionadas.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        if empresas:
            writer = csv.DictWriter(f, fieldnames=empresas[0].keys())
            writer.writeheader()
            writer.writerows(empresas)
    
    # Salvar resumo JSON
    resumo = {
        "total_empresas": len(empresas),
        "empresas_por_uf": defaultdict(int),
        "empresas_por_cnae": defaultdict(int),
        "top_score": [e for e in empresas[:100]],
        "data_processamento": datetime.now().isoformat(),
    }
    
    for emp in empresas:
        resumo["empresas_por_uf"][emp["uf"]] += 1
        cnae = emp["cnae_principal"][:2] if emp["cnae_principal"] else ""
        resumo["empresas_por_cnae"][cnae] += 1
    
    json_path = os.path.join(diretorio_saida, "resumo_fusao.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resumo, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\nResultados salvos em:")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  Total: {len(empresas)} empresas")
    
    return resumo


def main():
    print("=" * 60)
    print("FUSÃO DE DADOS - RADAR DE ELITE")
    print("=" * 60)
    
    # Configurar caminhos
    base_dir = "/mnt/ssd120"
    rf_dir = os.path.join(base_dir, "receita_federal")
    comex_dir = os.path.join(base_dir, "comexstat")
    saida_dir = os.path.join(base_dir, "fusionados")
    
    # 1. Carregar dados RF
    print("\n[1/4] Carregando dados da Receita Federal...")
    empresas = carregar_empresas_rf(rf_dir)
    print(f"  Total de estabelecimentos: {len(empresas)}")
    
    # 2. Carregar dados básicos das empresas
    print("\n[2/4] Carregando dados básicos das empresas...")
    empresas_basicas = carregar_empresas_basicas(rf_dir)
    print(f"  Total de empresas básicas: {len(empresas_basicas)}")
    
    # Complementar dados
    for cnpj_basico, basicas in empresas_basicas.items():
        for cnpj, emp in empresas.items():
            if emp["cnpj_basico"] == cnpj_basico:
                emp["razao_social"] = basicas["razao_social"]
                emp["capital_social"] = basicas["capital_social"]
                emp["porte"] = basicas["porte"]
                emp["natureza_juridica"] = basicas["natureza_juridica"]
                emp["data_abertura"] = basicas["data_abertura"]
    
    # 3. Carregar ComexStat
    print("\n[3/4] Carregando dados ComexStat...")
    comex = carregar_comexstat(comex_dir)
    print(f"  Total de registros ComexStat: {len(comex)}")
    
    # 4. Cruzar dados
    print("\n[4/4] Cruzando dados...")
    empresas_fusionadas = cruzar_rf_comex(empresas, comex)
    print(f"  Empresas fusionadas: {len(empresas_fusionadas)}")
    
    # Salvar resultados
    resumo = salvar_resultados(empresas_fusionadas, saida_dir)
    
    print("\n" + "=" * 60)
    print("FUSÃO CONCLUÍDA!")
    print("=" * 60)
    
    return resumo


if __name__ == "__main__":
    main()
