# -*- coding: utf-8 -*-
"""
name_search.py
---------------
Busca por nome completo. Faz duas coisas:

  1. Consulta o DuckDuckGo (via pacote duckduckgo_search) e mostra os
     principais resultados públicos de busca web para o nome.
  2. Gera links diretos para outros motores de busca e bases públicas
     brasileiras comumente usadas em pesquisas de nome (sem fazer
     scraping deles, apenas monta a URL para o usuário abrir).

Busca por nome tende a gerar muitos falsos positivos (nomes comuns) —
combine sempre com outros filtros (cidade, profissão etc.) para
resultados mais precisos.
"""
from urllib.parse import quote_plus

from rich.table import Table

from .. import utils

try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False


def _search_engine_links(name: str):
    q = quote_plus(name)
    return {
        "Google": f"https://www.google.com/search?q=%22{q}%22",
        "Bing": f"https://www.bing.com/search?q=%22{q}%22",
        "DuckDuckGo": f"https://duckduckgo.com/?q=%22{q}%22",
        "Google Imagens": f"https://www.google.com/search?tbm=isch&q=%22{q}%22",
        "Escavador (BR)": f"https://www.escavador.com/busca?q={q}",
        "JusBrasil (BR)": f"https://www.jusbrasil.com.br/busca?q={q}",
        "LinkedIn": f"https://www.linkedin.com/search/results/all/?keywords={q}",
        "Facebook": f"https://www.facebook.com/search/people/?q={q}",
    }


def run(name: str):
    name = name.strip()
    if len(name) < 3:
        utils.error("Digite um nome mais completo para melhores resultados.")
        utils.pause()
        return

    results = []
    if HAS_DDGS:
        utils.info(f"Buscando '{name}' no DuckDuckGo...")
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(f'"{name}"', region="br-pt", max_results=10):
                    results.append(r)
        except Exception as exc:
            utils.warn(f"Busca automática indisponível no momento ({exc}). "
                        "Use os links diretos abaixo.")
    else:
        utils.warn("Pacote duckduckgo_search não instalado — pulando busca automática.")

    if results:
        table = Table(title=f"Resultados de busca para '{name}'")
        table.add_column("Título", style="bold")
        table.add_column("URL", overflow="fold")
        for r in results[:10]:
            table.add_row(r.get("title", "—"), r.get("href", "—"))
        utils.console.print(table)
    else:
        utils.warn("Nenhum resultado automático — use os links diretos abaixo.")

    links = _search_engine_links(name)
    utils.info("Links diretos para pesquisa manual complementar:")
    for label, url in links.items():
        utils.console.print(f"  • {label}: {url}")

    if utils.console.input(
        "\nDeseja exportar o resultado? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        payload = {"nome": name, "resultados_busca": results, "links_diretos": links}
        path = utils.save_json(payload, f"nome_{name.replace(' ', '_')}")
        utils.success(f"Resultado salvo em: {path}")

    utils.pause()
