# -*- coding: utf-8 -*-
"""
email_search.py
----------------
Analisa um endereço de e-mail combinando vários sinais, todos baseados
em dados públicos ou em APIs de OSINT desenhadas de propósito para
esse tipo de consulta (não em sondagem de formulários de terceiros):

  1. Validação de formato (regex)
  2. Existência de registro MX no domínio, via consulta DNS pública
  3. Domínio de e-mail descartável/temporário (mailinator, yopmail etc.)
  4. Existência de foto de perfil no Gravatar
  5. Busca pública na API de commits do GitHub (e-mail exposto pelo
     próprio autor no histórico de commits de repositórios públicos)
  6. EmailRep.io — reputação do e-mail, indícios de vazamento e lista
     de redes sociais/plataformas onde o e-mail tem presença conhecida
     (funciona sem chave, com limite baixo; com chave gratuita, sobe
     pra 250 consultas/mês, 10/dia)
  7. Hunter.io — verificação de entregabilidade mais precisa que o
     MX sozinho (exige chave própria, tier grátis de ~100 verificações/mês)
  8. HaveIBeenPwned — vazamentos de dados (exige chave própria, paga)

Chaves de API são 100% opcionais e configuradas via variável de
ambiente (nunca hardcoded no código):
  export RESPONSA_EMAILREP_KEY="sua_chave"   # grátis em emailrep.io/free
  export RESPONSA_HUNTER_KEY="sua_chave"     # grátis em hunter.io
  export RESPONSA_HIBP_KEY="sua_chave"       # paga, haveibeenpwned.com/API/Key
  export RESPONSA_GITHUB_TOKEN="seu_token"   # grátis, github.com/settings/tokens

O QUE NÃO É FEITO, DE PROPÓSITO: não sondamos formulários de
cadastro/"esqueci minha senha" de redes sociais e outros sites pra
adivinhar na marra se um e-mail tem conta lá. Diferente da busca de
username (que verifica páginas de perfil genuinamente públicas), isso
exigiria abusar de sistemas de autenticação de terceiros — a maioria
bloqueia esse tipo de sondagem, geralmente viola termos de uso, e é a
mesma técnica usada em reconhecimento antes de ataques de phishing/
credential stuffing direcionado. As APIs de reputação (EmailRep) já
cobrem a pergunta "esse e-mail tem presença em redes sociais?" de um
jeito que respeita os termos de uso de cada serviço envolvido.
"""
import hashlib
import os
import re

import dns.resolver
import requests
from rich.table import Table

from .. import config, utils

EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Lista curada de domínios de e-mail descartável/temporário mais comuns.
DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "guerrillamail.info", "10minutemail.com",
    "10minutemail.net", "tempmail.com", "temp-mail.org", "throwawaymail.com",
    "yopmail.com", "yopmail.fr", "trashmail.com", "sharklasers.com", "getnada.com",
    "fakeinbox.com", "dispostable.com", "maildrop.cc", "mohmal.com",
    "emailondeck.com", "moakt.com", "inboxkitten.com", "mailnesia.com",
    "mintemail.com", "mytemp.email", "spambog.com", "mailcatch.com",
    "tempinbox.com", "discard.email", "spam4.me", "burnermail.io",
    "temp-mail.io", "emailfake.com", "fakemailgenerator.com",
}


def _check_format(email: str) -> bool:
    return bool(EMAIL_RE.match(email))


def _check_mx(domain: str):
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=6)
        return True, [str(r.exchange).rstrip(".") for r in answers]
    except Exception:
        return False, []


def _check_disposable(domain: str) -> bool:
    return domain.lower() in DISPOSABLE_DOMAINS


def _check_gravatar(email: str):
    h = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
    url = f"https://www.gravatar.com/avatar/{h}?d=404"
    try:
        resp = requests.get(url, headers=config.HEADERS, timeout=config.REQUEST_TIMEOUT)
        return resp.status_code == 200, f"https://www.gravatar.com/{h}"
    except requests.RequestException:
        return None, None


def _check_github_commits(email: str):
    """Busca pública de commits do GitHub associados ao e-mail.
    Dado já público (aparece no histórico de repositórios públicos).

    NOTA TÉCNICA: o campo 'total_count' da API de busca do GitHub é uma
    ESTIMATIVA aproximada para resultados grandes e pode vir muito
    inflada/instável (comportamento documentado pelo próprio GitHub).
    Por isso contamos apenas os commits retornados cujo e-mail do autor
    bate exatamente com o buscado, em vez de usar total_count."""
    url = "https://api.github.com/search/commits"
    headers = dict(config.HEADERS)
    headers["Accept"] = "application/vnd.github+json"
    token = os.environ.get("RESPONSA_GITHUB_TOKEN", "").strip() or None
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.get(
            url,
            params={"q": f"author-email:{email}", "per_page": 20},
            headers=headers,
            timeout=config.REQUEST_TIMEOUT,
        )
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            return "rate_limit", []
        if resp.status_code != 200:
            return None, []

        data = resp.json()
        matched_repos = []
        matched_count = 0
        for item in data.get("items", []):
            author_email = (item.get("commit", {}).get("author", {}) or {}).get("email", "")
            if author_email.lower() == email.lower():
                matched_count += 1
                repo_url = item.get("html_url", "")
                if repo_url and len(matched_repos) < 5:
                    matched_repos.append(repo_url)
        return matched_count, matched_repos
    except (requests.RequestException, ValueError):
        return None, []


def _check_emailrep(email: str):
    """EmailRep.io — reputação do e-mail + plataformas conhecidas onde
    ele tem presença. Funciona sem chave (rate limit bem baixo) ou com
    chave gratuita (250/mês, 10/dia) via RESPONSA_EMAILREP_KEY.
    Requer User-Agent (já incluso em config.HEADERS)."""
    url = f"https://emailrep.io/{email}"
    headers = dict(config.HEADERS)
    api_key = os.environ.get("RESPONSA_EMAILREP_KEY", "").strip() or None
    if api_key:
        headers["Key"] = api_key

    try:
        resp = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
        if resp.status_code == 401:
            return "chave_invalida", None
        if resp.status_code == 429:
            return "rate_limit", None
        if resp.status_code != 200:
            return None, None
        return "ok", resp.json()
    except (requests.RequestException, ValueError):
        return None, None


def _check_hunter(email: str):
    """Hunter.io — verificação de entregabilidade mais precisa que o MX
    isolado. Exige chave própria (RESPONSA_HUNTER_KEY), tier grátis
    disponível em hunter.io sem cartão de crédito."""
    api_key = os.environ.get("RESPONSA_HUNTER_KEY", "").strip() or None
    if not api_key:
        return "sem_chave", None

    url = "https://api.hunter.io/v2/email-verifier"
    try:
        resp = requests.get(
            url,
            params={"email": email, "api_key": api_key},
            headers=config.HEADERS,
            timeout=config.REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            return "erro", None
        return "ok", resp.json().get("data", {})
    except (requests.RequestException, ValueError):
        return "erro", None


def _check_hibp(email: str):
    """Consulta opcional ao HaveIBeenPwned. Exige chave de API própria
    (RESPONSA_HIBP_KEY), pois é um serviço pago desde 2024. Sem chave,
    apenas retorna o link para checagem manual gratuita."""
    api_key = os.environ.get("RESPONSA_HIBP_KEY", "").strip() or None
    if not api_key:
        return None, "sem_chave"

    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {"hibp-api-key": api_key, "User-Agent": config.HEADERS["User-Agent"]}
    try:
        resp = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
        if resp.status_code == 200:
            breaches = [b["Name"] for b in resp.json()]
            return True, breaches
        elif resp.status_code == 404:
            return False, []
        else:
            return None, "erro"
    except requests.RequestException:
        return None, "erro"


def run(email: str):
    email = email.strip()

    if not _check_format(email):
        utils.error("Formato de e-mail inválido.")
        utils.pause()
        return

    domain = email.split("@", 1)[1]

    utils.info(f"Analisando {email}...")
    has_mx, mx_records = _check_mx(domain)
    is_disposable = _check_disposable(domain)
    has_gravatar, gravatar_url = _check_gravatar(email)
    gh_total, gh_repos = _check_github_commits(email)
    rep_status, rep_data = _check_emailrep(email)
    hunter_status, hunter_data = _check_hunter(email)
    hibp_found, hibp_data = _check_hibp(email)

    table = Table(title=f"Análise do e-mail {email}")
    table.add_column("Verificação", style="bold cyan")
    table.add_column("Resultado")

    table.add_row("Formato válido", "Sim")
    table.add_row("Domínio possui MX (recebe e-mail)", "Sim" if has_mx else "Não")
    if mx_records:
        table.add_row("Servidores MX", ", ".join(mx_records[:3]))
    table.add_row(
        "E-mail descartável/temporário",
        "⚠️  Sim (mailinator, yopmail e similares)" if is_disposable else "Não",
    )

    if has_gravatar is None:
        table.add_row("Perfil Gravatar", "Erro ao consultar")
    else:
        table.add_row(
            "Perfil Gravatar (avatar público)",
            f"Encontrado → {gravatar_url}" if has_gravatar else "Não encontrado",
        )

    if gh_total is None:
        table.add_row("Commits públicos no GitHub", "Erro ao consultar")
    elif gh_total == "rate_limit":
        table.add_row("Commits públicos no GitHub", "Limite de requisições atingido, tente novamente em instantes")
    elif gh_total == 0:
        table.add_row("Commits públicos no GitHub", "Nenhum encontrado")
    else:
        table.add_row("Commits públicos no GitHub", f"{gh_total} encontrado(s)")

    # --- EmailRep.io ---
    emailrep_profiles = []
    if rep_status == "ok" and rep_data:
        reputation = rep_data.get("reputation", "desconhecida")
        suspicious = rep_data.get("suspicious", False)
        details = rep_data.get("details", {})
        emailrep_profiles = details.get("profiles", []) or []

        table.add_row("Reputação do e-mail (EmailRep)", reputation)
        table.add_row("Marcado como suspeito (EmailRep)", "⚠️  Sim" if suspicious else "Não")
        if details.get("credentials_leaked"):
            table.add_row("Credenciais vazadas em algum momento", "⚠️  Sim")
        if details.get("data_breach"):
            table.add_row("Presente em vazamento de dados", "⚠️  Sim")
        if details.get("days_since_domain_creation") is not None:
            table.add_row("Idade do domínio (dias)", str(details.get("days_since_domain_creation")))
        table.add_row(
            "Redes sociais/plataformas com presença conhecida",
            ", ".join(emailrep_profiles) if emailrep_profiles else "Nenhuma detectada",
        )
    elif rep_status == "rate_limit":
        table.add_row("EmailRep", "Limite de requisições atingido — configure RESPONSA_EMAILREP_KEY")
    elif rep_status == "chave_invalida":
        table.add_row("EmailRep", "Chave de API inválida")
    else:
        table.add_row("EmailRep", "Erro ao consultar")

    # --- Hunter.io ---
    if hunter_status == "ok" and hunter_data:
        table.add_row("Entregabilidade (Hunter.io)", hunter_data.get("status", "desconhecido"))
        table.add_row("Confiança da verificação (Hunter.io)", f"{hunter_data.get('score', '—')}%")
    elif hunter_status == "sem_chave":
        table.add_row("Entregabilidade (Hunter.io)", "Não verificado (sem chave de API)")
    else:
        table.add_row("Entregabilidade (Hunter.io)", "Erro ao consultar")

    # --- HaveIBeenPwned ---
    if hibp_data == "sem_chave":
        table.add_row("Vazamentos de dados (HaveIBeenPwned)", "Não verificado (sem chave de API)")
    elif hibp_data == "erro":
        table.add_row("Vazamentos de dados (HaveIBeenPwned)", "Erro ao consultar")
    elif hibp_found:
        table.add_row(
            "Vazamentos de dados (HaveIBeenPwned)",
            f"⚠️  Encontrado em {len(hibp_data)} vazamento(s)",
        )
    elif hibp_found is False:
        table.add_row("Vazamentos de dados (HaveIBeenPwned)", "Nenhum vazamento encontrado")

    utils.console.print(table)

    if gh_repos:
        utils.info("Repositórios públicos com commits desse e-mail:")
        for r in gh_repos:
            utils.console.print(f"  • {r}")

    if hibp_found:
        utils.warn("Vazamentos: " + ", ".join(hibp_data[:8]))

    tips = []
    if rep_status is None or rep_status == "rate_limit":
        tips.append(
            "EmailRep: crie sua chave gratuita em https://emailrep.io/free "
            "e defina RESPONSA_EMAILREP_KEY para um limite maior."
        )
    if hunter_status == "sem_chave":
        tips.append(
            "Hunter.io: crie sua chave gratuita em https://hunter.io "
            "e defina RESPONSA_HUNTER_KEY para checagem de entregabilidade mais precisa."
        )
    if hibp_data == "sem_chave":
        tips.append(
            "HaveIBeenPwned: gere sua chave (paga) em https://haveibeenpwned.com/API/Key "
            "e defina RESPONSA_HIBP_KEY, ou confira manualmente em "
            f"https://haveibeenpwned.com/account/{email}"
        )
    if tips:
        utils.info("Dicas para resultados mais completos:")
        for t in tips:
            utils.console.print(f"  • {t}")

    if utils.console.input(
        "\nDeseja exportar o resultado? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        payload = {
            "email": email, "dominio": domain, "mx_valido": has_mx,
            "servidores_mx": mx_records, "descartavel": is_disposable,
            "gravatar_encontrado": has_gravatar,
            "gravatar_url": gravatar_url if has_gravatar else None,
            "github_commits_total": gh_total, "github_repos": gh_repos,
            "emailrep": rep_data if rep_status == "ok" else None,
            "emailrep_profiles": emailrep_profiles,
            "hunter": hunter_data if hunter_status == "ok" else None,
            "hibp_encontrado": hibp_found if hibp_data != "sem_chave" else None,
            "hibp_vazamentos": hibp_data if isinstance(hibp_data, list) else None,
        }
        path = utils.save_json(payload, f"email_{domain}")
        utils.success(f"Resultado salvo em: {path}")

    utils.pause()
