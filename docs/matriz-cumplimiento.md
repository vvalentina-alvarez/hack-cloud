# Matriz de cumplimiento

| ID | Implementación | Evidencia |
|---|---|---|
| RF-01 | Métricas periódicas y API de reportes | EventBridge, `antennas/simulator.py`, `POST /reports` |
| RF-02 | Umbrales exactos y pruebas de frontera | `shared/common.py::classify`, `tests/test_core.py` |
| RF-03 | Validación completa | `api/create_report.py` |
| RF-04 | Estados e historial con marcas temporales | `api/router.py`, ítems `EVENT#` |
| RF-05 | Umbral por zona, tipo y usuario distinto | `workers/process_report.py::check_zone` |
| RF-06 | Evento de infraestructura y alerta NOC sin reportes | `antennas/evaluator.py`, `notifications/handler.py` |
| RF-07 | Avisos in-app y canales SES/SMS opcionales | `NotificationsTable`, `GET /notifications/{userId}` |
| RF-08 | Prioridad IA con impacto, antenas, imágenes y sitios críticos | `ai/summarize_zone.py` |
| RF-09 | Conteo de recurrencia y endpoint agregado | `failCount`, `GET /analytics/summary` |
| RF-10 | Fechas de resolución/cierre, zona, usuarios y agregados | `resolvedAt`, `closedAt`, endpoint analítico |
| RT-01 | Núcleo AWS serverless; Azure pendiente | Se declara honestamente como no cumplido |
| RT-02 | Flujo ejecutable y observable | Step Functions `CollectiveIncidentStateMachine` |
| RT-03 | Configuración y credenciales externas | Secrets Manager |
| RT-04 | Persistencia administrada y PITR | DynamoDB, S3, SQS/DLQ |
| RT-05 | Desacople, reintentos, idempotencia y prueba de ráfaga | SQS + `scripts/test-burst.mjs` |
| RT-06 | Resumen/prioridad, chatbot y análisis de imagen | Bedrock/Anthropic y Rekognition |
| RT-07 | Escalamiento y costo documentados | `docs/costos-y-escalabilidad.md` |
