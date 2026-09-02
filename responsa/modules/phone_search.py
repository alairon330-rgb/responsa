# -*- coding: utf-8 -*-
"""
phone_search.py
----------------
Analisa um número de telefone usando a biblioteca `phonenumbers`
(port em Python da libphonenumber do Google). Retorna metadados
públicos e técnicos: validade, país, operadora, tipo de linha
(fixo/celular/VoIP) e fuso horário. Também gera links públicos
(WhatsApp "click to chat" e Telegram) para verificação manual —
o próprio programa NÃO acessa esses serviços automaticamente.
"""
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from rich.table import Table

from .. import utils


def run(phone: str):
    phone = phone.strip()
    if not phone.startswith("+"):
        utils.warn(
            "Nenhum código de país (+55, +1...) informado. "
            "Assumindo Brasil (+55)."
        )
        raw = phone.replace(" ", "").replace("-", "")
        phone = "+55" + raw if not raw.startswith("55") else "+" + raw

    try:
        parsed = phonenumbers.parse(phone, None)
    except phonenumbers.NumberParseException as exc:
        utils.error(f"Não foi possível interpretar o número: {exc}")
        utils.pause()
        return

    valid = phonenumbers.is_valid_number(parsed)
    possible = phonenumbers.is_possible_number(parsed)

    e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    intl = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    line_types = {
        0: "Fixo", 1: "Celular", 2: "Fixo ou Celular", 3: "Grátis (0800)",
        4: "Tarifa premium", 5: "Compartilhado", 6: "VoIP", 7: "Pager",
        8: "Serviço pessoal", 9: "UAN", 10: "Voicemail", 27: "Desconhecido",
    }
    num_type = line_types.get(phonenumbers.number_type(parsed), "Desconhecido")

    table = Table(title=f"Análise do número {intl}")
    table.add_column("Campo", style="bold cyan")
    table.add_column("Valor")

    table.add_row("Formato E.164", e164)
    table.add_row("Formato internacional", intl)
    table.add_row("Válido?", "Sim" if valid else "Não")
    table.add_row("Possível?", "Sim" if possible else "Não")
    table.add_row("País/região", geocoder.description_for_number(parsed, "pt") or "—")
    table.add_row("Operadora", carrier.name_for_number(parsed, "pt") or "Não identificada")
    table.add_row("Tipo de linha", num_type)
    tzs = timezone.time_zones_for_number(parsed)
    table.add_row("Fuso(s) horário(s)", ", ".join(tzs) if tzs else "—")

    utils.console.print(table)

    digits = e164.replace("+", "")
    utils.info("Links públicos para verificação manual (o programa não acessa isso automaticamente):")
    utils.console.print(f"  • WhatsApp: https://wa.me/{digits}")
    utils.console.print(f"  • Telegram: https://t.me/{digits}")

    if utils.console.input(
        "\nDeseja exportar o resultado? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        payload = {
            "e164": e164, "internacional": intl, "valido": valid,
            "possivel": possible, "pais": geocoder.description_for_number(parsed, "pt"),
            "operadora": carrier.name_for_number(parsed, "pt"),
            "tipo_linha": num_type, "fusos": tzs,
        }
        path = utils.save_json(payload, f"telefone_{digits}")
        utils.success(f"Resultado salvo em: {path}")

    utils.pause()
