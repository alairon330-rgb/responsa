# -*- coding: utf-8 -*-
"""
username_search.py
-------------------
Verifica a existência de um nome de usuário em ~130 sites (redes sociais
+ sites gerais), usando checagem por código de status HTTP em threads
paralelas. Arquitetura inspirada em ferramentas conhecidas do gênero
(Sherlock, WhatsMyName): a base de sites fica em data/sites.json e pode
ser mantida/expandida pela comunidade.

LIMITAÇÃO CONHECIDA: sites com front-end 100% JavaScript (SPA) às vezes
retornam HTTP 200 mesmo para perfis inexistentes, e alguns bloqueiam
requisições automatizadas (403/429). Nesses casos o resultado aparece
como "indefinido" em vez de um falso "encontrado".
"""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from rich.progress import (BarColumn, Progress, TextColumn,
                            TimeElapsedColumn)
from rich.table import Table

from .. import config, utils

USERNAME_RE = re.compile(r"^[A-Za-z0-9_\-.]{2,32}$")


def load_sites():
    with open(config.SITES_DB, "r", encoding="utf-8") as f:
        return json.load(f)["sites"]


def check_site(site: dict, username: str) -> dict:
    url = site["url"].format(username)
    result = {
        "site": site["name"],
        "category": site["category"],
        "url": url,
        "status": "erro",
    }
    try:
        resp = requests.get(
            url,
            headers=config.HEADERS,
            timeout=config.REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        if resp.status_code == 200:
            result["status"] = "encontrado"
        elif resp.status_code == 404:
            result["status"] = "nao_encontrado"
        else:
            result["status"] = "indefinido"
    except requests.RequestException:
        result["status"] = "erro"
    return result


def run(username: str):
    if not USERNAME_RE.match(username):
        utils.warn(
            "Username com formato incomum — a busca continuará, mas "
            "verifique manualmente se necessário."
        )

    sites = load_sites()
    utils.info(
        f"Verificando '{username}' em {len(sites)} sites "
        f"({sum(1 for s in sites if s['category']=='social')} redes sociais + "
        f"{sum(1 for s in sites if s['category']=='general')} sites gerais)...\n"
    )

    found, not_found, undefined, errors = [], [], [], []

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Escaneando...", total=len(sites))
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            futures = []
            for site in sites:
                futures.append(executor.submit(check_site, site, username))
                time.sleep(config.RATE_LIMIT_DELAY)

            for future in as_completed(futures):
                res = future.result()
                if res["status"] == "encontrado":
                    found.append(res)
                elif res["status"] == "nao_encontrado":
                    not_found.append(res)
                elif res["status"] == "indefinido":
                    undefined.append(res)
                else:
                    errors.append(res)
                progress.advance(task)

    table = Table(title=f"Resultados para '{username}' — possíveis perfis encontrados")
    table.add_column("Site", style="bold")
    table.add_column("Categoria")
    table.add_column("URL", overflow="fold")

    for r in sorted(found, key=lambda x: (x["category"], x["site"])):
        table.add_row(r["site"], r["category"], r["url"])

    utils.console.print(table)
    utils.success(f"{len(found)} perfil(is) provavelmente encontrado(s).")
    utils.info(f"{len(not_found)} não encontrado(s).")
    utils.info(
        f"{len(undefined)} indefinido(s) (site bloqueou/exige verificação manual)."
    )
    if errors:
        utils.warn(f"{len(errors)} com erro de conexão/timeout.")

    if utils.console.input(
        "\nDeseja exportar os resultados? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        payload = {
            "username": username,
            "encontrados": found,
            "nao_encontrados": not_found,
            "indefinidos": undefined,
            "erros": errors,
        }
        path = utils.save_json(payload, f"username_{username}")
        utils.success(f"Resultados salvos em: {path}")

    utils.pause()
