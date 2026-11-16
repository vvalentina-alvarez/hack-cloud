# Red TeleCorp — detección y gestión serverless de incidencias

Plataforma desplegada en AWS para recibir telemetría de antenas y reportes de usuarios, detectar incidentes colectivos, priorizar su atención con IA y mantener informados a clientes y operadores.

## Arquitectura

- API Gateway HTTP API para reportes, incidencias, analítica, notificaciones y chat.
- Lambda + SQS/DLQ para absorber ráfagas sin perder eventos.
- DynamoDB on-demand con PITR para estados, historial, ventanas de zona, chat y notificaciones.
- EventBridge para correlación y alertas proactivas.
- Step Functions para verificar incidentes colectivos, aplicar IA, persistir y notificar.
- Bedrock/Rekognition para resumen, prioridad, chatbot y evidencias fotográficas.
- API Gateway + Lambda para publicar el portal dentro de las restricciones de Learner Lab.
- El alcance entregado es AWS; el requisito multinube con Azure queda declarado como no implementado.

El diagrama y las decisiones están en [docs/arquitectura.md](docs/arquitectura.md).

## API desplegada

```text
https://0rzsjdgx26.execute-api.us-east-1.amazonaws.com
```

| Método | Ruta | Propósito |
|---|---|---|
| POST | `/reports` | Registrar un reporte |
| POST | `/chat` | Asistente IA |
| GET | `/incidents?status=` | Listar incidencias |
| GET | `/incidents/{id}` | Detalle e historial |
| PATCH | `/incidents/{id}/status` | Cambiar estado |
| POST | `/incidents/{id}/image-url` | URL firmada para evidencia |
| GET | `/users/{userId}/incidents` | Incidencias del usuario |
| GET | `/notifications/{userId}` | Avisos del usuario |
| GET | `/antennas` | Estado de antenas |
| GET | `/analytics/summary` | Resumen histórico y recurrencia |

## Despliegue

```powershell
sam build
sam deploy --stack-name red-telecorp --region us-east-1 --resolve-s3 `
  --capabilities CAPABILITY_IAM `
  --parameter-overrides `
    LabRoleArn=arn:aws:iam::<cuenta>:role/LabRole `
    AlertEmail=correo@ejemplo.com `
    NotificationFromEmail=correo-verificado-en-ses@ejemplo.com
```

`NotificationFromEmail` puede quedar vacío: los avisos siempre se guardan en DynamoDB y se muestran en el portal; SES solo se usa cuando existe una identidad verificada. Los SMS se intentan únicamente con números E.164 (`+51...`).

## Pruebas

```powershell
# Unitarias
python -m unittest discover -s tests -v

# Ráfaga real contra AWS
node scripts/test-burst.mjs https://0rzsjdgx26.execute-api.us-east-1.amazonaws.com 50
```

La guía completa de demo está en [docs/demo.md](docs/demo.md).

## Seguridad

- Nunca guardar claves en el repositorio.
- Configuración global y credenciales de integraciones en Secrets Manager.
- S3 de evidencias privado y frontend servido por una Lambda sin almacenamiento de credenciales.
- Para una fase productiva se debe añadir Cognito/WAF y reemplazar `LabRole` por roles mínimos por función.
