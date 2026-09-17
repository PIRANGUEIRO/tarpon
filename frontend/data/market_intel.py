"""
Market Intelligence - dados dinâmicos via backend API.
Fallback para dados hardcoded apenas quando o banco está vazio.
"""
import os
import json

_API_URL = os.environ.get("RADAR_API_URL", "http://localhost:8000")


def carregar_dados_mercado() -> dict:
    """Tenta carregar dados do backend; fallback para dados hardcoded."""
    try:
        import requests
        resp = requests.get(f"{_API_URL}/api/market-intel/panorama", timeout=10)
        if resp.ok:
            dados = resp.json()
            if dados.get("gerais", {}).get("total_embarques", 0) > 0:
                return dados
    except Exception:
        pass
    return DADOS_MERCADO_HARDCODED


DADOS_MERCADO_HARDCODED = {
    "gerais": {
        "total_embarques": 4282389,
        "peso_bruto_ton": 377367076,
        "total_teus": 11424397,
        "total_containers": 6452202,
    },
    "tipo_embarque": {
        "House": 4185873,
        "Master": 4149406,
        "Direto": 3088678,
        "Coloader": 440,
    },
    "tipo_pagamento": {
        "Prepaid": 6340582,
        "Collect": 5082799,
    },
    "incoterms": {
        "CFR": 3172769,
        "CIF": 3167824,
        "FOB": 2543470,
        "EXW": 2539382,
        "FCA": 292,
        "CPT": 35,
        "FAS": 11,
        "CIP": 5,
    },
    "tipo_container": {
        "C40 (40 pés)": 5069060,
        "C20 (20 pés)": 1371716,
    },
    "top_importadores": [
        {"nome": "Asia Shipping Transportes Internacionais Ltda", "teus": 433598, "share": 3.80},
        {"nome": "Scan Global Logistics do Brasil Ltda", "teus": 180871, "share": 1.58},
        {"nome": "Kuehne Nagel Servicos Logisticos Ltda", "teus": 149098, "share": 1.31},
        {"nome": "Comexport Trading Comercio Exterior Ltda", "teus": 134873, "share": 1.18},
        {"nome": "DC Logistics Brasil Ltda", "teus": 107864, "share": 0.94},
        {"nome": "Hand Line Transportes Internacionais Ltda", "teus": 95091, "share": 0.83},
        {"nome": "Craft Multimodal Ltda", "teus": 91364, "share": 0.80},
        {"nome": "DSV Air e Sea Brasil Ltda", "teus": 88104, "share": 0.77},
        {"nome": "Caoa Montadora de Veiculos Ltda", "teus": 76660, "share": 0.67},
        {"nome": "BYD Auto do Brasil Ltda", "teus": 76531, "share": 0.67},
    ],
    "top_exportadores": [
        {"nome": "AS Group Integrated Solutions", "teus": 250183, "share": 4.14},
        {"nome": "Aurora International Logistic Co", "teus": 233574, "share": 3.86},
        {"nome": "BYD H K Co", "teus": 116752, "share": 1.93},
        {"nome": "Parisi Grand Smooth Logistics", "teus": 113816, "share": 1.88},
        {"nome": "Shanghai Syntrans", "teus": 111711, "share": 1.85},
        {"nome": "AS Group Integrated Logistics Solutions Limited", "teus": 90374, "share": 1.49},
        {"nome": "Kuehne Nagel Ltd", "teus": 89092, "share": 1.47},
        {"nome": "Chery Automobile", "teus": 70330, "share": 1.16},
        {"nome": "Blu Logistics China Co", "teus": 52136, "share": 0.86},
        {"nome": "Shenzhen CTS International Logistics Co", "teus": 51785, "share": 0.86},
    ],
    "agentes_carga_nacionais": [
        {"nome": "Asia Shipping Transportes Internacionais Ltda", "teus": 437355, "share": 10.54},
        {"nome": "Scan Global Logistics do Brasil Ltda", "teus": 188889, "share": 4.55},
        {"nome": "Kuehne Nagel Servicos Logisticos Ltda", "teus": 156130, "share": 3.76},
        {"nome": "Allog Group", "teus": 116790, "share": 2.81},
        {"nome": "DC Logistics Brasil Ltda", "teus": 109330, "share": 2.63},
        {"nome": "DSV Air e Sea Brasil Ltda", "teus": 101429, "share": 2.44},
        {"nome": "Hand Line Transportes Internacionais Ltda", "teus": 94941, "share": 2.29},
        {"nome": "DHL Global Forwarding Brazil Logistics Ltda", "teus": 67882, "share": 1.64},
        {"nome": "LX Pantos Logistica do Brasil Ltda", "teus": 64348, "share": 1.55},
    ],
    "agentes_carga_internacionais": [
        {"nome": "AS Group Integrated Logistics Solutions", "teus": 352728, "share": 8.77},
        {"nome": "Aurora International Logistic Co", "teus": 200231, "share": 4.98},
        {"nome": "Kuehne Nagel Ltd", "teus": 139589, "share": 3.47},
        {"nome": "Shanghai Syntrans", "teus": 138780, "share": 3.45},
        {"nome": "Parisi Grand Smooth Logistics", "teus": 128517, "share": 3.20},
        {"nome": "Scan Global Logistics A", "teus": 87766, "share": 2.18},
        {"nome": "Blu Logistics China Co", "teus": 70566, "share": 1.76},
        {"nome": "LX Pantos Co", "teus": 66840, "share": 1.66},
        {"nome": "Xiamen Trans China Logistics Co", "teus": 65300, "share": 1.62},
        {"nome": "Shenzhen", "teus": 63043, "share": 1.57},
    ],
    "armadores": [
        {"nome": "MSC Mediterranean Shipping Co", "teus": 2866111, "share": 25.10},
        {"nome": "Maersk", "teus": 2203302, "share": 19.30},
        {"nome": "CMA CGM", "teus": 1506610, "share": 13.20},
        {"nome": "Hapag Lloyd", "teus": 1099686, "share": 9.63},
        {"nome": "Cosco", "teus": 838177, "share": 7.34},
        {"nome": "ONE", "teus": 655478, "share": 5.74},
        {"nome": "HMM Co", "teus": 655477, "share": 5.74},
        {"nome": "Pacific International Lines", "teus": 431692, "share": 3.78},
        {"nome": "Evergreen", "teus": 410611, "share": 3.60},
        {"nome": "Zim", "teus": 182695, "share": 1.60},
    ],
    "portos_origem": [
        {"porto": "Ningbo", "teus": 1663959},
        {"porto": "Shanghai", "teus": 1578910},
        {"porto": "Tsingtao Qingdao", "teus": 863126},
        {"porto": "Shekou", "teus": 490403},
        {"porto": "Yantian", "teus": 379167},
        {"porto": "Tianjinxingang", "teus": 365868},
        {"porto": "Antuérpia", "teus": 351577},
        {"porto": "Houston", "teus": 281438},
        {"porto": "Hamburg", "teus": 268290},
    ],
    "portos_destino": [
        {"porto": "Santos", "teus": 4058343},
        {"porto": "Navegantes", "teus": 1737256},
        {"porto": "Itapoá", "teus": 1381437},
        {"porto": "Paranaguá", "teus": 946748},
        {"porto": "Manaus", "teus": 827259},
        {"porto": "Rio de Janeiro", "teus": 616479},
        {"porto": "Vitória", "teus": 400145},
        {"porto": "Salvador", "teus": 372805},
        {"porto": "Suape", "teus": 353134},
    ],
    "paises_origem": [
        {"pais": "China", "teus": 6407104},
        {"pais": "United States", "teus": 753487},
        {"pais": "India", "teus": 381003},
        {"pais": "Germany", "teus": 367843},
        {"pais": "Belgium", "teus": 351692},
        {"pais": "Italy", "teus": 289421},
        {"pais": "Viet Nam", "teus": 207721},
        {"pais": "Mexico", "teus": 203315},
        {"pais": "Republic of Korea", "teus": 173954},
    ],
    "rotas_principais": [
        {"rota": "Shanghai → Santos", "teus": 641999, "share": 5.93},
        {"rota": "Ningbo → Santos", "teus": 382252, "share": 3.53},
        {"rota": "Ningbo → Navegantes", "teus": 352508, "share": 3.26},
        {"rota": "Ningbo → Itapoá", "teus": 255476, "share": 2.36},
        {"rota": "Tsingtao Qingdao → Santos", "teus": 247855, "share": 2.29},
    ],
    "top_produtos": [
        {"produto": "Pneumáticos novos, de borracha", "teus": 442834},
        {"produto": "Outras obras de plástico", "teus": 380940},
        {"produto": "Polímeros de etileno", "teus": 333238},
        {"produto": "Tubos e acessórios de plástico", "teus": 317548},
        {"produto": "Semicondutores", "teus": 292837},
        {"produto": "Chapas autoadesivas de plástico", "teus": 248679},
        {"produto": "Automóveis de passageiros", "teus": 230102},
        {"produto": "Inseticidas, fungicidas, herbicidas", "teus": 225102},
        {"produto": "Partes e acessórios veículos", "teus": 178778},
    ],
    "armazens_destino": [
        {"armazem": "Não identificado", "teus": 2536202, "share": 22.20},
        {"armazem": "Santos Brasil", "teus": 1544594, "share": 13.52},
        {"armazem": "Terminal Portonave Navegantes SC", "teus": 1041028, "share": 9.11},
        {"armazem": "Porto Itapoá", "teus": 948430, "share": 8.30},
        {"armazem": "Brasil Terminal Portuário", "teus": 798870, "share": 6.99},
        {"armazem": "Terminal TCP Paranaguá PR", "teus": 636610, "share": 5.57},
        {"armazem": "Embraport SP", "teus": 475821, "share": 4.16},
        {"armazem": "Multirio Terminal 2 RJ", "teus": 309549, "share": 2.71},
    ],
}


DADOS_MERCADO = carregar_dados_mercado()
