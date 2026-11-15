# Red TeleCorp: incidencias serverless multinube

AWS (núcleo + IA) · GCP (analítica en BigQuery) · Azure (respaldo geo-redundante)

## Despliegue (AWS Learner Lab)

```bash
aws iam get-role --role-name LabRole --query Role.Arn --output text
sam build
sam deploy --guided
```

## Pruebas

```bash
bash scripts/test_zone.sh <ApiUrl>
bash scripts/test_chat.sh <ApiUrl>
```

## Endpoints

| Método | Ruta |
|---|---|
| POST | /reports |
| POST | /chat |
| GET | /incidents?status= |
| GET | /incidents/{id} |
| PATCH | /incidents/{id}/status |
| POST | /incidents/{id}/image-url |
| GET | /users/{userId}/incidents |
| GET | /antennas |
