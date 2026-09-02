# -*- coding: utf-8 -*-
"""
cep_search.py
-------------
Consulta de CEP (Código de Endereçamento Postal) usando a API pública
e gratuita ViaCEP (https://viacep.com.br). Dado 100% público e oficial
dos Correios, sem qualquer restrição de uso para consultas pontuais.
"""
import re

import requests
from rich.table import Table

from .. import config, utils

CEP_RE = re.compile(r"^\d{8}$")


def run(cep: str):
    clean = re.sub(r"\D", "", cep)
    if not CEP_RE.match(clean):
        utils.error("CEP inválido. Use o formato 00000000 ou 00000-000.")
        utils.pause()
        return

    utils.info(f"Consultando CEP {clean} na base ViaCEP...")
    url = f"https://viacep.com.br/ws/{clean}/json/"

    try:
        resp = requests.get(url, headers=config.HEADERS, timeout=config.REQUEST_TIMEOUT)
        data = resp.json()
    except requests.RequestException as exc:
        utils.error(f"Falha ao consultar a API: {exc}")
        utils.pause()
        return

    if data.get("erro"):
        utils.warn("CEP não encontrado na base dos Correios.")
        utils.pause()
        return

    table = Table(title=f"Endereço referente ao CEP {clean}")
    table.add_column("Campo", style="bold cyan")
    table.add_column("Valor")

    campos = [
        ("Logradouro", data.get("logradouro")),
        ("Complemento", data.get("complemento")),
        ("Bairro", data.get("bairro")),
        ("Cidade", data.get("localidade")),
        ("UF", data.get("uf")),
        ("Código IBGE", data.get("ibge")),
        ("DDD", data.get("ddd")),
    ]
    for campo, valor in campos:
        if valor:
            table.add_row(campo, str(valor))

    utils.console.print(table)

    if utils.console.input(
        "\nDeseja exportar o resultado? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        path = utils.save_json(data, f"cep_{clean}")
        utils.success(f"Resultado salvo em: {path}")

    utils.pause()
