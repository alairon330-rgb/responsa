# -*- coding: utf-8 -*-
"""Configurações e constantes globais do RESPONSA."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SITES_DB = os.path.join(DATA_DIR, "sites.json")

# Pasta onde os resultados exportados são salvos (criada em tempo de execução)
OUTPUT_DIR = os.path.join(os.getcwd(), "responsa_resultados")

# Cabeçalhos HTTP usados nas requisições (identifica o bot de forma honesta)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ResponsaOSINT/1.0; "
        "+https://github.com/alairon330-rgb/responsa)"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

REQUEST_TIMEOUT = 8          # segundos por requisição
MAX_WORKERS = 25             # threads simultâneas na busca de username
RATE_LIMIT_DELAY = 0.05      # pequeno respiro entre disparos de thread

VERSION = "1.0.0"
