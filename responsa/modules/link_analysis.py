# -*- coding: utf-8 -*-
"""
link_analysis.py
------------------
Verifica se uma URL é conhecida como phishing/malware/maliciosa,
usando a API pública do VirusTotal (v3), que agrega o veredito de
mais de 70 motores de antivírus e listas de bloqueio.

Exige chave de API própria (gratuita, sem cartão de crédito), definida
via variável de ambiente RESPONSA_VT_KEY. Sem chave, o módulo apenas
explica como criar uma e como consultar manualmente.

Tier gratuito: 4 requisições/minuto, ~500/dia — suficiente para uso
pessoal e checagens pontuais.
"""
import base64
import os
import re

import requests
from rich.table import Table

from .. import config, utils

URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def _encode_url_id(url: str) -> str:
    return base64.urlsafe_b64encode(url.encode()).decode().strip("=")


def run(url: str):
    url = url.strip()
    if not URL_RE.match(url):
        url = "http://" + url  # o VirusTotal aceita, mas normalizamos pra consistência

    api_key = os.environ.get("RESPONSA_VT_KEY", "").strip() or None
    if not api_key:
        utils.warn("Nenhuma chave de API configurada para o VirusTotal.")
        utils.info(
            "Crie uma chave gratuita (sem cartão) em https://www.virustotal.com/gui/join-us "
            "e defina a variável de ambiente RESPONSA_VT_KEY antes de rodar o programa:\n"
            "  export RESPONSA_VT_KEY=\"sua_chave\"\n"
            f"Enquanto isso, você pode checar manualmente em "
            f"https://www.virustotal.com/gui/url/{_encode_url_id(url)}"
        )
        utils.pause()
        return

    utils.info(f"Consultando reputação de {url} no VirusTotal...")
    url_id = _encode_url_id(url)
    headers = dict(config.HEADERS)
    headers["x-apikey"] = api_key

    try:
        resp = requests.get(
            f"https://www.virustotal.com/api/v3/urls/{url_id}",
            headers=headers,
            timeout=config.REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        utils.error(f"Falha ao consultar a API: {exc}")
        utils.pause()
        return

    if resp.status_code == 404:
        # URL ainda não foi analisada antes — envia para análise.
        utils.info("Essa URL ainda não tinha sido analisada. Enviando para análise agora...")
        try:
            submit = requests.post(
                "https://www.virustotal.com/api/v3/urls",
                headers=headers,
                data={"url": url},
                timeout=config.REQUEST_TIMEOUT,
            )
            if submit.status_code in (200, 201):
                utils.success(
                    "Enviado com sucesso! A análise leva de alguns segundos a poucos minutos — "
                    "rode a busca de novo daqui a pouco pra ver o resultado."
                )
            else:
                utils.error(f"Falha ao enviar para análise (status {submit.status_code}).")
        except requests.RequestException as exc:
            utils.error(f"Falha ao enviar para análise: {exc}")
        utils.pause()
        return

    if resp.status_code == 401:
        utils.error("Chave de API inválida.")
        utils.pause()
        return
    if resp.status_code == 429:
        utils.warn("Limite de requisições do VirusTotal atingido (tier grátis: 4/min). Tente novamente em instantes.")
        utils.pause()
        return
    if resp.status_code != 200:
        utils.error(f"A API retornou status {resp.status_code}.")
        utils.pause()
        return

    data = resp.json().get("data", {}).get("attributes", {})
    stats = data.get("last_analysis_stats", {})
    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)
    harmless = stats.get("harmless", 0)
    undetected = stats.get("undetected", 0)
    total = malicious + suspicious + harmless + undetected

    table = Table(title=f"Análise de reputação — {url}")
    table.add_column("Campo", style="bold cyan")
    table.add_column("Valor")

    veredito = "⚠️  MALICIOSA" if malicious > 0 else ("⚠️  Suspeita" if suspicious > 0 else "Sem detecções")
    table.add_row("Veredito geral", veredito)
    table.add_row("Motores que marcaram como maliciosa", f"{malicious} de {total}")
    table.add_row("Motores que marcaram como suspeita", f"{suspicious} de {total}")
    table.add_row("Categoria (se houver)", ", ".join(set(data.get("categories", {}).values())) or "—")
    table.add_row("Título da página", data.get("title", "—") or "—")
    table.add_row("Última análise", str(data.get("last_analysis_date", "—")))

    utils.console.print(table)

    if utils.console.input(
        "\nDeseja exportar o resultado? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        payload = {"url": url, "veredito": veredito, "stats": stats, "detalhes": data}
        path = utils.save_json(payload, "link_analysis")
        utils.success(f"Resultado salvo em: {path}")

    utils.pause()
