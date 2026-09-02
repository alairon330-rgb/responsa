# -*- coding: utf-8 -*-
"""
ip_search.py
------------
Consulta informações públicas de geolocalização/rede de um endereço IP
usando a API ipinfo.io — 100% HTTPS, sem exigir chave para uso básico
(chave gratuita opcional aumenta o limite de 50 mil consultas/mês via
RESPONSA_IPINFO_KEY).

HISTÓRICO: a versão anterior deste módulo usava ip-api.com, que no
plano grátis só aceita HTTP puro (porta 80) — algumas redes/roteadores
bloqueiam essa porta por padrão, causando timeout mesmo com internet
funcionando normalmente. Trocamos para uma API HTTPS-only por isso.
"""
import ipaddress
import os

import requests
from rich.table import Table

from .. import config, utils


def _valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def run(ip: str):
    ip = ip.strip()
    if not _valid_ip(ip):
        utils.error("Endereço IP inválido.")
        utils.pause()
        return

    if ipaddress.ip_address(ip).is_private:
        utils.warn(
            "Esse é um IP privado/local (da sua própria rede) — não existe "
            "geolocalização pública pra ele. Tente um IP público, tipo 8.8.8.8."
        )
        utils.pause()
        return

    utils.info(f"Consultando informações públicas do IP {ip} (ipinfo.io, HTTPS)...")
    url = f"https://ipinfo.io/{ip}/json"
    params = {}
    token = os.environ.get("RESPONSA_IPINFO_KEY", "").strip() or None
    if token:
        params["token"] = token

    try:
        resp = requests.get(url, params=params, headers=config.HEADERS, timeout=config.REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        utils.error(f"Falha ao consultar a API: {exc}")
        utils.pause()
        return

    if resp.status_code == 429:
        utils.warn(
            "Limite de requisições sem chave atingido. Crie uma chave gratuita "
            "em https://ipinfo.io/signup e defina RESPONSA_IPINFO_KEY."
        )
        utils.pause()
        return
    if resp.status_code != 200:
        utils.error(f"A API retornou status {resp.status_code}.")
        utils.pause()
        return

    try:
        data = resp.json()
    except ValueError:
        utils.error("Resposta inesperada da API.")
        utils.pause()
        return

    if data.get("bogon"):
        utils.warn("Esse IP é reservado/não roteável publicamente (bogon) — sem dado de geolocalização.")
        utils.pause()
        return

    lat, lon = None, None
    if data.get("loc"):
        try:
            lat, lon = data["loc"].split(",")
        except ValueError:
            pass

    table = Table(title=f"Informações públicas do IP {ip}")
    table.add_column("Campo", style="bold cyan")
    table.add_column("Valor")

    campos = [
        ("País", data.get("country")),
        ("Região", data.get("region")),
        ("Cidade", data.get("city")),
        ("CEP/ZIP aprox.", data.get("postal")),
        ("Latitude", lat),
        ("Longitude", lon),
        ("Fuso horário", data.get("timezone")),
        ("Organização/ISP", data.get("org")),
        ("Hostname (rDNS)", data.get("hostname")),
    ]
    for campo, valor in campos:
        if valor:
            table.add_row(campo, str(valor))

    utils.console.print(table)
    utils.warn(
        "A geolocalização por IP é aproximada (geralmente reflete o "
        "provedor, não o endereço exato da pessoa)."
    )

    if utils.console.input(
        "\nDeseja exportar o resultado? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        path = utils.save_json(data, f"ip_{ip.replace(':', '_')}")
        utils.success(f"Resultado salvo em: {path}")

    utils.pause()
