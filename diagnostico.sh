#!/bin/bash
# diagnostico.sh — checagem rápida de conectividade pro RESPONSA
# Uso: bash diagnostico.sh

echo "=== 1. Internet básica (ping 8.8.8.8) ==="
ping -c 3 8.8.8.8

echo ""
echo "=== 2. DNS resolvendo nomes (ping google.com) ==="
ping -c 3 google.com

echo ""
echo "=== 3. HTTPS funcionando (viacep.com.br) ==="
curl -Is https://viacep.com.br | head -1

echo ""
echo "=== 4. HTTPS funcionando (ipinfo.io) ==="
curl -Is https://ipinfo.io | head -1

echo ""
echo "Diagnóstico concluído."
