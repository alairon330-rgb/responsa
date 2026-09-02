# -*- coding: utf-8 -*-
"""Funções utilitárias compartilhadas entre os módulos de busca."""
import csv
import json
import os
from datetime import datetime

from rich.console import Console

from . import config

console = Console()


def ensure_output_dir() -> str:
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    return config.OUTPUT_DIR


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_json(data, prefix: str) -> str:
    ensure_output_dir()
    path = os.path.join(config.OUTPUT_DIR, f"{prefix}_{timestamp()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def save_csv(rows, headers, prefix: str) -> str:
    ensure_output_dir()
    path = os.path.join(config.OUTPUT_DIR, f"{prefix}_{timestamp()}.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return path


def info(msg: str) -> None:
    console.print(f"[bold cyan][*][/bold cyan] {msg}")


def success(msg: str) -> None:
    console.print(f"[bold green][+][/bold green] {msg}")


def warn(msg: str) -> None:
    console.print(f"[bold yellow][!][/bold yellow] {msg}")


def error(msg: str) -> None:
    console.print(f"[bold red][x][/bold red] {msg}")


def pause() -> None:
    console.input("\n[dim]Pressione ENTER para voltar ao menu...[/dim]")
