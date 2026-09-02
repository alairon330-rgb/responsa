# -*- coding: utf-8 -*-
"""
hash_identify.py
------------------
Identifica o(s) possível(is) algoritmo(s) de um hash com base no seu
comprimento e formato — útil em forense digital, CTFs e análise de
vazamentos de credenciais (pra saber o que se está olhando antes de
tentar quebrar/comparar). 100% offline, não faz nenhuma requisição de
rede nem tenta quebrar o hash.
"""
import re

from rich.table import Table

from .. import utils

# (regex, [algoritmos possíveis])
PATTERNS = [
    (re.compile(r"^[a-f0-9]{32}$", re.I), ["MD5", "NTLM", "MD4"]),
    (re.compile(r"^[a-f0-9]{40}$", re.I), ["SHA-1", "MySQL5 (SHA-1)"]),
    (re.compile(r"^[a-f0-9]{56}$", re.I), ["SHA-224", "SHA3-224"]),
    (re.compile(r"^[a-f0-9]{64}$", re.I), ["SHA-256", "SHA3-256"]),
    (re.compile(r"^[a-f0-9]{96}$", re.I), ["SHA-384", "SHA3-384"]),
    (re.compile(r"^[a-f0-9]{128}$", re.I), ["SHA-512", "SHA3-512", "Whirlpool"]),
    (re.compile(r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$"), ["bcrypt"]),
    (re.compile(r"^\$1\$[./A-Za-z0-9]{0,8}\$[./A-Za-z0-9]{22}$"), ["MD5 crypt (Unix)"]),
    (re.compile(r"^\$5\$"), ["SHA-256 crypt (Unix)"]),
    (re.compile(r"^\$6\$"), ["SHA-512 crypt (Unix)"]),
    (re.compile(r"^\$argon2(id|i|d)\$"), ["Argon2"]),
    (re.compile(r"^[A-Za-z0-9+/]{27}=$"), ["SHA-1 (Base64)"]),
    (re.compile(r"^[A-Za-z0-9+/]{43}=$"), ["SHA-256 (Base64)"]),
    (re.compile(r"^[A-Za-z0-9./]{13}$"), ["DES crypt (Unix, legado)"]),
]


def run(value: str):
    value = value.strip()
    if not value:
        utils.error("Digite um hash pra identificar.")
        utils.pause()
        return

    matches = []
    for pattern, algos in PATTERNS:
        if pattern.match(value):
            matches.extend(algos)

    table = Table(title="Identificação de hash")
    table.add_column("Campo", style="bold cyan")
    table.add_column("Valor")
    table.add_row("Hash informado", value)
    table.add_row("Comprimento", str(len(value)))

    if matches:
        table.add_row("Algoritmo(s) provável(is)", ", ".join(dict.fromkeys(matches)))
    else:
        table.add_row("Algoritmo(s) provável(is)", "Não identificado — formato incomum")

    utils.console.print(table)
    utils.info(
        "Hashes de mesmo comprimento (ex: MD5/NTLM, ou SHA-256/SHA3-256) são "
        "indistinguíveis só pelo formato — o contexto de onde ele veio "
        "geralmente resolve a ambiguidade."
    )

    if utils.console.input(
        "\nDeseja exportar o resultado? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        payload = {"hash": value, "comprimento": len(value), "algoritmos_provaveis": list(dict.fromkeys(matches))}
        path = utils.save_json(payload, "hash_identify")
        utils.success(f"Resultado salvo em: {path}")

    utils.pause()
