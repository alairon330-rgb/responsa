# -*- coding: utf-8 -*-
"""
cpf_validate.py
------------------
Validador de CPF. Confere se um número é MATEMATICAMENTE válido pelo
algoritmo oficial de dígitos verificadores (módulo 11) usado pela
Receita Federal — 100% offline, nenhuma consulta de rede, nenhum dado
pessoal envolvido ou revelado.

IMPORTANTE — o que este módulo NÃO faz, de propósito: não consulta se
o CPF existe de fato, não retorna nome do titular, situação cadastral
ou qualquer outro dado pessoal. CPF é dado protegido pela LGPD, e
diferente do CNPJ (que é público por natureza), não existe uma API
legítima que resolva "CPF → identidade". A única consulta oficial
(Receita Federal) exige CPF + data de nascimento e ainda assim só
devolve situação cadastral com nome mascarado — automatizar aquele
serviço violaria os termos de uso dele (tem captcha de propósito).
Este validador serve só pra checar se o número está bem formado,
como qualquer validação de formulário faria.
"""
import re

from rich.table import Table

from .. import utils


def _clean(cpf: str) -> str:
    return re.sub(r"\D", "", cpf)


def _format(cpf: str) -> str:
    return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"


def is_valid_cpf(cpf: str, check_repeated: bool = True) -> bool:
    cpf = _clean(cpf)
    if len(cpf) != 11:
        return False
    if check_repeated and cpf == cpf[0] * 11:  # todos os dígitos iguais (000.000.000-00 etc.) — inválido por regra
        return False

    def _digit(base: str) -> int:
        weights = list(range(len(base) + 1, 1, -1))
        total = sum(int(d) * w for d, w in zip(base, weights))
        resto = (total * 10) % 11
        return 0 if resto == 10 else resto

    d1 = _digit(cpf[:9])
    d2 = _digit(cpf[:9] + str(d1))
    return cpf[-2:] == f"{d1}{d2}"


def run(cpf: str):
    clean = _clean(cpf)

    table = Table(title="Validação de CPF (offline)")
    table.add_column("Campo", style="bold cyan")
    table.add_column("Valor")

    if len(clean) != 11:
        utils.error(f"CPF deve ter 11 dígitos — você informou {len(clean)}.")
        utils.pause()
        return

    digitos_ok = is_valid_cpf(clean, check_repeated=False)
    repetido = clean == clean[0] * 11
    valido = digitos_ok and not repetido

    table.add_row("CPF formatado", _format(clean))
    table.add_row("Dígitos verificadores corretos", "✅ Sim" if digitos_ok else "❌ Não")
    table.add_row("Conclusão", "Formato matematicamente válido" if valido else ("CPF inválido (todos os dígitos iguais)" if repetido else "CPF inválido (dígito verificador não bate)"))

    utils.console.print(table)
    utils.info(
        "Isso confirma só se o número é matematicamente possível, não se "
        "existe uma pessoa real com esse CPF nem quem seria — essa "
        "informação é protegida pela LGPD e não está disponível publicamente."
    )

    if utils.console.input(
        "\nDeseja exportar o resultado? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        payload = {"cpf_formatado": _format(clean), "valido": valido}
        path = utils.save_json(payload, "cpf_validate")
        utils.success(f"Resultado salvo em: {path}")

    utils.pause()
