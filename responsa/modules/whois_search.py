# -*- coding: utf-8 -*-
"""
whois_search.py
----------------
Consulta de registro de domínio via RDAP (Registration Data Access
Protocol), o sucessor moderno e padronizado do WHOIS tradicional.
Usa o serviço de bootstrap público rdap.org, que redireciona
automaticamente para o servidor RDAP correto de cada registro (TLD).
100% dado público — é literalmente a mesma informação que aparece
numa consulta "whois" convencional, só que em JSON estruturado.
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

    utils.info(f"Consultando registro RDAP de {domain}...")
    url = f"https://rdap.org/domain/{domain}"
    headers = dict(config.HEADERS)
    headers["Accept"] = "application/rdap+json"

    try:
        resp = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT, allow_redirects=True)
    except requests.RequestException as exc:
        utils.error(f"Falha ao consultar RDAP: {exc}")
        utils.pause()
        return

    if resp.status_code == 404:
        utils.warn("Domínio não encontrado no registro (pode não existir ou não estar registrado).")
        utils.pause()
        return
    if resp.status_code != 200:
        utils.error(f"Servidor RDAP retornou status {resp.status_code}.")
        utils.pause()
        return

    try:
        data = resp.json()
    except ValueError:
        utils.error("Resposta inesperada do servidor RDAP.")
        utils.pause()
        return

    table = Table(title=f"Registro de domínio — {domain}")
    table.add_column("Campo", style="bold cyan")
    table.add_column("Valor")

    table.add_row("Status", ", ".join(data.get("status", [])) or "—")

    nameservers = [ns.get("ldhName", "") for ns in data.get("nameservers", [])]
    if nameservers:
        table.add_row("Servidores DNS", "\n".join(nameservers))

    events = {e.get("eventAction"): e.get("eventDate") for e in data.get("events", [])}
    if events.get("registration"):
        table.add_row("Data de registro", events["registration"])
    if events.get("last changed"):
        table.add_row("Última alteração", events["last changed"])
    if events.get("expiration"):
        table.add_row("Data de expiração", events["expiration"])

    # Entidades (registrante, registrador etc.) — a maioria dos registros
    # modernos oculta dados pessoais do titular por privacidade (GDPR/LGPD),
    # então geralmente só o nome do registrador aparece de fato.
    for entity in data.get("entities", []):
        roles = ", ".join(entity.get("roles", []))
        name = None
        vcard = entity.get("vcardArray")
        if vcard and len(vcard) > 1:
            for item in vcard[1]:
                if item[0] == "fn":
                    name = item[3]
        if name and roles:
            table.add_row(f"Entidade ({roles})", name)

    utils.console.print(table)
    utils.info(
        "A maioria dos registros modernos oculta dados pessoais do titular "
        "(nome, e-mail, telefone) por privacidade — isso é o comportamento "
        "padrão dos registradores, não uma limitação desta ferramenta."
    )

    if utils.console.input(
        "\nDeseja exportar o resultado bruto (JSON completo)? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        path = utils.save_json(data, f"whois_{domain}")
        utils.success(f"Resultado salvo em: {path}")

    utils.pause()
