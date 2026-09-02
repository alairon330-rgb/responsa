# -*- coding: utf-8 -*-
"""menu.py — Menu interativo exibido logo abaixo do banner do olho de coruja."""
from rich.panel import Panel
from rich.table import Table

from . import banner, utils
from .modules import (cep_search, cnpj_search, cpf_validate, email_search,
                       hash_identify, image_search, ip_search, link_analysis,
                       name_search, phone_search, subdomain_search,
                       username_search, whois_search)

OPTIONS = {
    "1": ("Busca por nome de usuário", username_search, "Informe o username"),
    "2": ("Busca por e-mail", email_search, "Informe o e-mail"),
    "3": ("Busca por CEP", cep_search, "Informe o CEP"),
    "4": ("Busca por telefone", phone_search, "Informe o telefone (com DDD)"),
    "5": ("Busca por nome completo", name_search, "Informe o nome completo"),
    "6": ("Busca por IP", ip_search, "Informe o endereço IP"),
    "7": ("WHOIS / registro de domínio", whois_search, "Informe o domínio (ex: exemplo.com)"),
    "8": ("Subdomínios (Certificate Transparency)", subdomain_search, "Informe o domínio (ex: exemplo.com)"),
    "9": ("Consulta de CNPJ", cnpj_search, "Informe o CNPJ"),
    "10": ("Análise de link suspeito (VirusTotal)", link_analysis, "Informe a URL"),
    "11": ("Identificador de hash", hash_identify, "Informe o hash"),
    "12": ("Busca reversa de imagem / EXIF", image_search, "Informe a URL da imagem ou o caminho de um arquivo local"),
    "13": ("Validador de CPF (offline)", cpf_validate, "Informe o CPF"),
}


def show_menu() -> None:
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold yellow", justify="right")
    table.add_column(style="white")
    for key, (label, _, _) in OPTIONS.items():
        table.add_row(f"[{key}]", label)
    table.add_row("[0]", "Sair")

    utils.console.print(Panel(table, title="Menu de Buscas — RESPONSA", border_style="cyan"))


def main_loop() -> None:
    banner.print_banner()
    while True:
        show_menu()
        choice = utils.console.input("\n[bold cyan]Escolha uma opção:[/bold cyan] ").strip()

        if choice == "0":
            utils.console.print("\n[bold magenta]Até a próxima! 🦉[/bold magenta]\n")
            break

        option = OPTIONS.get(choice)
        if not option:
            utils.error("Opção inválida.")
            continue

        label, module, prompt = option
        value = utils.console.input(f"[bold cyan]{prompt}:[/bold cyan] ").strip()
        if not value:
            utils.error("Valor não pode ser vazio.")
            continue

        utils.console.print()
        try:
            module.run(value)
        except KeyboardInterrupt:
            utils.warn("\nBusca interrompida pelo usuário.")
        except Exception as exc:  # pragma: no cover - proteção geral do menu
            utils.error(f"Erro inesperado: {exc}")

        banner.print_banner()
