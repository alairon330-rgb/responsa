# -*- coding: utf-8 -*-
"""
image_search.py
------------------
Pesquisa reversa de imagem, em duas frentes:

  1. Se a entrada for uma URL de imagem já hospedada: gera links diretos
     para os principais motores de busca reversa (Google Lens, Yandex,
     Bing, TinEye), usando o padrão de URL "buscar por imagem" que cada
     um já expõe publicamente. Não fazemos scraping nem automação —
     é o mesmo link que você abriria manualmente no navegador.

  2. Se a entrada for um caminho de arquivo local: extraímos os
     metadados EXIF (câmera, data, e principalmente coordenadas GPS,
     se presentes) usando a biblioteca Pillow, 100% offline — nenhuma
     rede envolvida. É uma técnica clássica de forense digital em
     OSINT: muita gente esquece de apagar o GPS embutido em fotos
     tiradas com celular antes de publicar.

NÃO integramos motores de busca reversa baseados em reconhecimento
facial (tipo PimEyes) — esses são desenhados especificamente pra
rastrear o rosto de uma pessoa por múltiplos sites, o que é um vetor
de perseguição/stalking muito mais direto do que uma busca reversa de
imagem comum, e ficou de fora por design.
"""
import os
from urllib.parse import quote

from rich.table import Table

from .. import utils

try:
    from PIL import ExifTags, Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def _is_url(value: str) -> bool:
    return value.strip().lower().startswith(("http://", "https://"))


def _reverse_search_links(image_url: str) -> dict:
    encoded = quote(image_url, safe="")
    return {
        "Google Lens": f"https://lens.google.com/uploadbyurl?url={encoded}",
        "Yandex Images": f"https://yandex.com/images/search?url={encoded}&rpt=imageview",
        "Bing Visual Search": f"https://www.bing.com/images/search?q=imgurl:{encoded}&view=detailv2&iss=sbi",
        "TinEye": f"https://tineye.com/search?url={encoded}",
    }


def _dms_to_decimal(dms, ref):
    degrees, minutes, seconds = dms
    decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    if ref in ("S", "W"):
        decimal = -decimal
    return round(decimal, 6)


def _extract_exif(path: str):
    if not HAS_PIL:
        return None, "Pillow não instalado — rode 'pip install pillow'."

    try:
        image = Image.open(path)
        exif_raw = image.getexif()
    except Exception as exc:
        return None, f"Não foi possível abrir a imagem: {exc}"

    if not exif_raw:
        return {}, None

    exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_raw.items()}

    gps_info = {}
    gps_ifd = exif_raw.get_ifd(0x8825) if hasattr(exif_raw, "get_ifd") else {}
    for key, val in gps_ifd.items():
        gps_info[ExifTags.GPSTAGS.get(key, key)] = val

    result = {
        "camera_fabricante": exif.get("Make"),
        "camera_modelo": exif.get("Model"),
        "data_hora_original": exif.get("DateTimeOriginal") or exif.get("DateTime"),
        "software": exif.get("Software"),
    }

    if gps_info.get("GPSLatitude") and gps_info.get("GPSLongitude"):
        try:
            lat = _dms_to_decimal(gps_info["GPSLatitude"], gps_info.get("GPSLatitudeRef", "N"))
            lon = _dms_to_decimal(gps_info["GPSLongitude"], gps_info.get("GPSLongitudeRef", "E"))
            result["gps_latitude"] = lat
            result["gps_longitude"] = lon
            result["gps_maps_url"] = f"https://www.google.com/maps?q={lat},{lon}"
        except Exception:
            pass

    return result, None


def run(image_input: str):
    image_input = image_input.strip()

    if _is_url(image_input):
        utils.info(f"Gerando links de busca reversa para: {image_input}")
        links = _reverse_search_links(image_input)

        table = Table(title="Busca reversa de imagem — links diretos")
        table.add_column("Motor", style="bold cyan")
        table.add_column("Link", overflow="fold")
        for nome, link in links.items():
            table.add_row(nome, link)
        utils.console.print(table)
        utils.info(
            "Cada motor tem um jeito diferente de indexar/comparar imagens — "
            "vale abrir mais de um pra comparar os resultados."
        )

        if utils.console.input(
            "\nDeseja exportar os links? [green](s/n)[/green]: "
        ).strip().lower() == "s":
            path = utils.save_json({"imagem": image_input, "links": links}, "busca_imagem")
            utils.success(f"Resultado salvo em: {path}")

        utils.pause()
        return

    # Caminho de arquivo local
    if not os.path.isfile(image_input):
        utils.error(
            "Não encontrei esse arquivo. Informe uma URL pública de imagem "
            "(https://...) ou o caminho de um arquivo existente no seu computador."
        )
        utils.pause()
        return

    utils.info(f"Lendo metadados EXIF de {image_input} (100% local, sem rede)...")
    exif_data, err = _extract_exif(image_input)

    if err:
        utils.error(err)
        utils.pause()
        return

    if not exif_data:
        utils.warn("Nenhum metadado EXIF encontrado nesta imagem (comum em prints, imagens editadas ou já limpas).")
        utils.pause()
        return

    table = Table(title=f"Metadados EXIF — {os.path.basename(image_input)}")
    table.add_column("Campo", style="bold cyan")
    table.add_column("Valor")

    campos_visiveis = [
        ("Fabricante da câmera", exif_data.get("camera_fabricante")),
        ("Modelo da câmera", exif_data.get("camera_modelo")),
        ("Data/hora original", exif_data.get("data_hora_original")),
        ("Software usado", exif_data.get("software")),
    ]
    for campo, valor in campos_visiveis:
        if valor:
            table.add_row(campo, str(valor))

    if exif_data.get("gps_latitude") is not None:
        table.add_row("Latitude GPS", str(exif_data["gps_latitude"]))
        table.add_row("Longitude GPS", str(exif_data["gps_longitude"]))
        table.add_row("Ver no mapa", exif_data["gps_maps_url"])

    if not any(v for _, v in campos_visiveis) and exif_data.get("gps_latitude") is None:
        utils.warn("A imagem tem dados EXIF, mas nenhum dos campos comuns (câmera, data, GPS) estava presente.")
    else:
        utils.console.print(table)

    utils.info(
        "Se a imagem foi baixada de rede social, provavelmente o EXIF já foi "
        "removido — a maioria das plataformas apaga esses metadados no upload."
    )

    if utils.console.input(
        "\nDeseja exportar os metadados? [green](s/n)[/green]: "
    ).strip().lower() == "s":
        path = utils.save_json(exif_data, f"exif_{os.path.basename(image_input)}")
        utils.success(f"Resultado salvo em: {path}")

    utils.pause()
