import re

def validar_cnpj(cnpj: str) -> bool:
    cnpj = re.sub(r"\D", "", cnpj)
    if len(cnpj) != 14:
        return False

    def calc_digito(digs, pesos):
        soma = sum(int(d) * p for d, p in zip(digs, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    if cnpj == cnpj[0] * 14:
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1

    d1 = calc_digito(cnpj[:12], pesos1)
    if int(cnpj[12]) != d1:
        return False

    d2 = calc_digito(cnpj[:13], pesos2)
    return int(cnpj[13]) == d2

def formatar_cnpj(cnpj: str) -> str:
    cnpj = re.sub(r"\D", "", cnpj)
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

def extrair_cnae_divisao(cnae: str) -> str:
    return cnae[:2] if cnae else ""
