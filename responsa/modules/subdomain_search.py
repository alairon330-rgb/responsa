# -*- coding: utf-8 -*-
"""
subdomain_search.py
---------------------
Mapeia subdomínios de um domínio usando os logs públicos de
Certificate Transparency (CT), agregados pelo crt.sh. Toda vez que um
certificado SSL/TLS é emitido para um domínio, ele é publicado
permanentemente nesses logs (exigência do RFC 6962, aplicada por
todos os navegadores modernos) — ou seja, é dado público por design,
sem necessidade de chave de API.

Uso típico: mapear a infraestrutura de um domínio (subdomínios de
homologação, painéis administrativos esquecidos etc.) — uma das
técnicas mais usadas em pentest/bug bounty por ser 100% passiva
(não faz nenhuma requisição ao domínio alvo em si).
"""
import re

import requests
from rich.table import Table

from .. import config, utils

DOMAIN_RE = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9-]{1,63})+$")


def run(domain: str):
    domain = domain.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]

    if not DOMAIN_RE.match(domain):
        utils.error("Domínio inválido. Use algo como 'exemplo.com.br'.")
        utils.pause()
        return

    utils.info(f"Consultando logs de Certificate Transparency (crt.sh) para %.{domain}...")
    url = "https://crt.sh/"

    try:
        resp = requests.get(
            url,
            params={"q": f"%.{domain}", "output": "json"},
            headers=config.HEADERS,
            timeout=20,
        )
    except requests.RequestException as exc:
        utils.error(f"Falha ao consultar crt.sh: {exc}")
        utils.pause()
        return

    if resp.status_code != 200:
        utils.warn(f"crt.sh retornou status {resp.status_code} (o serviço às vezes fica instável).")
        utils.pause()
        return

    try:
        certs = resp.json()
    except ValueError:
        utils.warn("Nenhum certificado encontrado ou resposta vazia.")
        utils.pause()
        return

    if not certs:
        utils.warn("Nenhum subdomínio encontrado nos logs de Certificate Transparency.")
        utils.pause()
        return

    subdomains = set()
    for cert in certs:
        name_value = cert.get("name_value", "")
        for sub in name_value.split("\n"):
            sub = sub.strip().lower()
            if sub and "*" not in sub and sub.endswith(domain):
                subdomains.add(sub)

    sorted_subs = sorted(subdomains)

    table = Table(title=f"Subdomínios de {domain} ({len(sorted_subs)} encontrado(s))")
    table.add_column("Subdomínio", style="bold")
    for sub in sorted_subs[:100]:
        table.add_row(sub)

    utils.console.print(table)
    if len(sorted_subs) > 100:
        utils.info(f"Mostrando 100 de {len(sorted_subs)} — exporte o resultado para ver a lista completa.")

    utils.info(
        "Isso é uma consulta passiva a certificados já emitidos, não um scan "
        "ativo no domínio. Alguns subdomínios listados podem estar inativos hoje."
    )

    if utils.console.input(
        "\nDeseja exportar o resultado? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        path = utils.save_json({"dominio": domain, "subdominios": sorted_subs}, f"subdominios_{domain}")
        utils.success(f"Resultado salvo em: {path}")

    utils.pause()
