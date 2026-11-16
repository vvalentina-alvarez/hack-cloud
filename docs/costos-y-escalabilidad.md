# Escalabilidad y costo operativo

| Componente | Cómo escala | Principal impulsor de costo | Control aplicado |
|---|---|---|---|
| API Gateway | Solicitudes concurrentes administradas | Número de llamadas | Validación temprana y respuestas 202 |
| Lambda | Instancias por concurrencia | Invocaciones, duración y memoria | Timeouts acotados y concurrencia SQS máxima 2 en el lab |
| SQS/DLQ | Mensajes almacenados y procesados | Solicitudes y retención | Lotes de 10 y máximo 3 intentos |
| DynamoDB | On-demand | Lecturas, escrituras, Streams y almacenamiento | Índices dirigidos; analítica de demo usa scans limitados |
| Step Functions | Ejecuciones independientes | Transiciones de estado | Una ejecución activa por zona y tipo durante 24 h |
| Bedrock/Rekognition | Por solicitud/tokens/imagen | Tokens y análisis | IA solo en incidentes colectivos; límites de salida |
| API Gateway/Lambda | Portal estático y API | Solicitudes e invocaciones | Archivos pequeños y caché del navegador |
| SNS/SES | Por mensaje | Destinatarios y canal | Solo cambios de estado o alertas relevantes |

Para producción se reemplazan scans analíticos por agregados incrementales o exportación a un almacén analítico, se ajusta la concurrencia según `ApproximateAgeOfOldestMessage` y se configuran presupuestos/alertas de AWS.
