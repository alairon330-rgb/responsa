# -*- coding: utf-8 -*-
"""
Testes básicos e 100% offline (não fazem requisições de rede),
focados em validação de dados e lógica pura.
"""
import json
import re
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from responsa import config
from responsa.modules import cep_search, email_search, phone_search, ip_search


def test_sites_json_structure():
    with open(config.SITES_DB, "r", encoding="utf-8") as f:
        data = json.load(f)
    sites = data["sites"]
    assert len(sites) >= 100, "Base deve ter pelo menos 100 sites"
    social = [s for s in sites if s["category"] == "social"]
    assert len(social) >= 20, "Deve haver pelo menos 20 redes sociais"
    for s in sites:
        assert "{}" in s["url"], f"URL sem placeholder: {s['id']}"


def test_cep_regex():
    assert cep_search.CEP_RE.match("01310100")
    assert not cep_search.CEP_RE.match("abc")


def test_email_format():
    assert email_search._check_format("teste@exemplo.com")
    assert not email_search._check_format("nao-e-email")


def test_ip_validation():
    assert ip_search._valid_ip("8.8.8.8")
    assert not ip_search._valid_ip("999.999.999.999")
    assert ip_search._valid_ip("2001:4860:4860::8888")


def test_phone_parsing_offline():
    import phonenumbers
    parsed = phonenumbers.parse("+5511987654321", None)
    assert phonenumbers.is_valid_number(parsed)


def test_hash_regex_patterns():
    from responsa.modules import hash_identify
    md5 = "5d41402abc4b2a76b9719d911017c592"
    matched = [algos for pattern, algos in hash_identify.PATTERNS if pattern.match(md5)]
    assert matched, "MD5 de teste deveria ser identificado"
    assert "MD5" in matched[0]


def test_domain_regex():
    from responsa.modules import whois_search
    assert whois_search.DOMAIN_RE.match("exemplo.com.br")
    assert not whois_search.DOMAIN_RE.match("dominio invalido")


def test_cnpj_clean_and_validate():
    from responsa.modules import cnpj_search
    assert cnpj_search._clean_cnpj("00.000.000/0001-91") == "00000000000191"
    assert cnpj_search._valid_cnpj_format("00000000000191")
    assert not cnpj_search._valid_cnpj_format("123")


def test_virustotal_url_id_encoding():
    from responsa.modules import link_analysis
    encoded = link_analysis._encode_url_id("http://example.com")
    assert isinstance(encoded, str) and len(encoded) > 0


def test_cpf_validator():
    from responsa.modules import cpf_validate
    assert cpf_validate.is_valid_cpf("11144477735")
    assert not cpf_validate.is_valid_cpf("11144477736")
    assert not cpf_validate.is_valid_cpf("00000000000")
    assert not cpf_validate.is_valid_cpf("123")


def test_image_search_links():
    from responsa.modules import image_search
    assert image_search._is_url("https://exemplo.com/foto.jpg")
    assert not image_search._is_url("/home/user/foto.jpg")
    links = image_search._reverse_search_links("https://exemplo.com/foto.jpg")
    assert "Google Lens" in links and "TinEye" in links


if __name__ == "__main__":
    test_sites_json_structure()
    test_cep_regex()
    test_email_format()
    test_ip_validation()
    test_phone_parsing_offline()
    test_hash_regex_patterns()
    test_domain_regex()
    test_cnpj_clean_and_validate()
    test_virustotal_url_id_encoding()
    test_cpf_validator()
    test_image_search_links()
    print("Todos os testes passaram!")
