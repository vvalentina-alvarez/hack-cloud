# Pitch de 5 minutos — Red TeleCorp

## 0:00–0:40 · Problema

“Una operadora suele enterarse de una falla cuando ya tiene decenas de clientes reclamando. Los reportes llegan aislados, la telemetría vive separada y el equipo no sabe qué atender primero. Red TeleCorp convierte esas señales dispersas en incidentes accionables.”

Mostrar el portal: estado de red, antenas monitoreadas e incidencias.

## 0:40–1:35 · Ingesta resiliente y detección proactiva

“Cada antena reporta tráfico en GB por minuto. Clasificamos los límites exactos del caso y publicamos un evento solo cuando cambia el estado. Si una antena cae, EventBridge alerta al NOC antes del primer reclamo. Los reportes de clientes entran por API Gateway y SQS absorbe ráfagas, reintenta y protege contra pérdidas.”

Mostrar `/antennas` y una ejecución del simulador con una antena forzada.

## 1:35–2:35 · Correlación y Step Functions

“Cada reporte se agrupa por geohash, tipo de problema y usuario. Diez usuarios distintos en menos de 24 horas activan una única ejecución. Step Functions hace visible cada etapa: analizar con IA, aplicar fallback, crear el incidente y notificar.”

Ejecutar `node scripts/test-burst.mjs <ApiUrl> 10` y abrir el historial de Step Functions.

## 2:35–3:25 · IA con propósito

“La IA no decide a ciegas. Recibe reportes reales de la zona, estado de antenas, evidencia fotográfica y servicios críticos cercanos. Produce resumen, causa probable, acción, mensaje y prioridad del 1 al 5. Si Bedrock no responde, el flujo continúa con una respuesta segura.”

Mostrar un incidente colectivo y el chatbot.

## 3:25–4:10 · Seguimiento y comunicación

“La incidencia conserva todo su historial: registrada, en revisión, en atención, solucionada y cerrada. Cada cambio crea un aviso in-app y puede enviarse por SES o SMS. Operaciones consulta zonas frecuentes, tipos repetidos, duración y antenas recurrentes.”

Mostrar “Mis incidencias”, notificaciones y el bloque de analítica.

## 4:10–4:45 · Arquitectura y costo

“No mantenemos servidores. Lambda, DynamoDB on-demand, SQS, EventBridge, Step Functions, API Gateway y S3 escalan por demanda. Pagamos por solicitudes, ejecuciones, almacenamiento y transferencia; las cuotas y concurrencia se pueden controlar.”

Mostrar `docs/arquitectura.md`.

## 4:45–5:00 · Cierre

“Red TeleCorp pasa de reaccionar tarde a detectar, correlacionar, priorizar y comunicar en minutos. El resultado es menor tiempo de diagnóstico, atención basada en impacto y clientes informados.”
