# Guía de demostración y evidencias

## Preparación

1. Confirmar el correo de suscripción SNS.
2. Abrir el `FrontendUrl` del stack `red-telecorp`.
3. Abrir CloudFormation y Step Functions en `us-east-1`.

## Escenario A — telemetría proactiva

Invocar la función `AntennaSimulatorFunction` con:

```json
{"force":{"ANT-003":0,"ANT-004":20}}
```

Esperado: `ANT-003 = INHABILITADA`, `ANT-004 = CAIDA`, incremento de `failCount`, evento `AntennaStateChanged` y correo SNS al NOC.

## Escenario B — incidente colectivo

```powershell
node scripts/test-burst.mjs https://0rzsjdgx26.execute-api.us-east-1.amazonaws.com 10
```

Esperado: diez respuestas `202`, una ejecución de Step Functions, un único incidente colectivo para `zona + SIN_INTERNET`, notificaciones in-app para los diez usuarios y aviso al NOC.

## Escenario C — ciclo de vida

```http
PATCH /incidents/{id}/status
{"status":"EN_REVISION","note":"Validación automática"}
```

Repetir con `EN_ATENCION`, `SOLUCIONADA` y `CERRADA`. Consultar el detalle para mostrar eventos y `/notifications/{documentId}` para demostrar avisos.

## Escenario D — ráfaga

```powershell
node scripts/test-burst.mjs https://0rzsjdgx26.execute-api.us-east-1.amazonaws.com 50
```

Criterio: 50 aceptados, 50 identificadores únicos, mensajes procesados o pendientes en SQS y DLQ vacía al finalizar.

## Escenario E — IA

Enviar un mensaje desde el portal y mostrar una ejecución colectiva. Si Bedrock no está habilitado en Learner Lab, enseñar el `Catch` y fallback de Step Functions: el flujo sigue siendo ejecutable y observable.
