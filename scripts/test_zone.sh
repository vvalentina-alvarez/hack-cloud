#!/usr/bin/env bash
# Envía 10 reportes de 10 usuarios distintos en el mismo punto -> dispara el incidente colectivo.
# Uso: bash scripts/test_zone.sh https://xxxx.execute-api.us-east-1.amazonaws.com
set -euo pipefail
API="${1:?Pasa la ApiUrl como primer argumento}"

for i in $(seq 1 10); do
  curl -s -X POST "$API/reports" -H "Content-Type: application/json" \
    -d "{\"documentId\":\"7000000$i\",\"serviceNumber\":\"99900000$i\",\"lat\":-12.0464,\"lon\":-77.0428,\"occurredAt\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"problemType\":\"SIN_INTERNET\",\"description\":\"Sin conexion desde hace una hora\"}"
  echo
done

echo "Listo. Revisa Step Functions en la consola y tu correo del NOC."
