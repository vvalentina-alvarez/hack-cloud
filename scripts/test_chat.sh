#!/usr/bin/env bash
# Prueba el chatbot. Uso: bash scripts/test_chat.sh https://xxxx.execute-api.us-east-1.amazonaws.com
set -euo pipefail
API="${1:?Pasa la ApiUrl como primer argumento}"

curl -s -X POST "$API/chat" -H "Content-Type: application/json" \
  -d '{"message":"Hola, no tengo internet desde hace una hora","location":{"lat":-12.0464,"lon":-77.0428}}'
echo
echo "Para continuar la conversación, envía el sessionId devuelto en el siguiente mensaje."
