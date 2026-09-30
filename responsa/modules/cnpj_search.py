# -*- coding: utf-8 -*-
"""
cnpj_search.py
----------------
Consulta de dados cadastrais de empresas brasileiras via BrasilAPI
(https://brasilapi.com.br/api/cnpj/v1/{cnpj}), que espelha a base
pública da Receita Federal. Dado público — qualquer CNPJ ativo tem
razão social, situação cadastral, endereço e CNAE consultáveis
livremente, inclusive pelo site oficial da própria Receita.
"""
import re

import requests
from rich.table import Table

from .. import config, utils


def _clean_cnpj(cnpj: str) -> str:
    return re.sub(r"\D", "", cnpj)


def _valid_cnpj_format(cnpj: str) -> bool:
    return len(cnpj) == 14 and cnpj != cnpj[0] * 14 and _cnpj_digits_ok(cnpj)


def run(cnpj: str):
    clean = _clean_cnpj(cnpj)
    if not _valid_cnpj_format(clean):
        utils.error("CNPJ inválido: confira os 14 dígitos (formato ou dígito verificador incorreto).")
        utils.pause()
        return

    utils.info(f"Consultando CNPJ {clean} na BrasilAPI (base da Receita Federal)...")
    url = f"https://brasilapi.com.br/api/cnpj/v1/{clean}"

    try:
        resp = requests.get(url, headers=config.HEADERS, timeout=config.REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        utils.error(f"Falha ao consultar a API: {exc}")
        utils.pause()
        return

    if resp.status_code == 404:
        utils.warn("CNPJ não encontrado na base da Receita Federal.")
        utils.pause()
        return
    if resp.status_code != 200:
        utils.error(f"A API retornou status {resp.status_code}.")
        utils.pause()
        return

    data = resp.json()

    table = Table(title=f"Empresa — CNPJ {clean}")
    table.add_column("Campo", style="bold cyan")
    table.add_column("Valor")

    campos = [
        ("Razão social", data.get("razao_social")),
        ("Nome fantasia", data.get("nome_fantasia")),
        ("Situação cadastral", data.get("descricao_situacao_cadastral")),
        ("Data de abertura", data.get("data_inicio_atividade")),
        ("Porte", data.get("descricao_porte")),
        ("Natureza jurídica", data.get("descricao_natureza_juridica")),
        ("Atividade principal (CNAE)", data.get("cnae_fiscal_descricao")),
        ("E-mail", data.get("email")),
        ("Telefone", f"({data.get('ddd_telefone_1')})" if data.get("ddd_telefone_1") else None),
        ("Endereço", ", ".join(filter(None, [
            data.get("logradouro"), data.get("numero"), data.get("bairro"),
            data.get("municipio"), data.get("uf"),
        ])) or None),
        ("CEP", data.get("cep")),
        ("Capital social", data.get("capital_social")),
    ]
    for campo, valor in campos:
        if valor:
            table.add_row(campo, str(valor))

    utils.console.print(table)

    socios = data.get("qsa", [])
    if socios:
        utils.info("Quadro de sócios (QSA):")
        for s in socios[:10]:
            utils.console.print(f"  • {s.get('nome_socio', '—')} — {s.get('qualificacao_socio', '—')}")

    if utils.console.input(
        "\nDeseja exportar o resultado? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        path = utils.save_json(data, f"cnpj_{clean}")
        utils.success(f"Resultado salvo em: {path}")

    utils.pause()


def _cnpj_digits_ok(cnpj: str) -> bool:
    def dv(base, pesos):
        r = sum(int(d) * p for d, p in zip(base, pesos)) % 11
        return 0 if r < 2 else 11 - r

    d1 = dv(cnpj[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    d2 = dv(cnpj[:13], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return cnpj[12:] == f"{d1}{d2}"
