"""DynamoDB Streams -> Azure Blob Storage (respaldo geo-redundante / DR)."""
import json
import os
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError

_deser = TypeDeserializer()
_container = None


def _default(o):
    if isinstance(o, Decimal):
        return float(o)
    if isinstance(o, set):
        return sorted(o)
    return str(o)


def _get_container():
    global _container
    if _container is None:
        from azure.storage.blob import BlobServiceClient

        cfg = json.loads(boto3.client("secretsmanager").get_secret_value(
            SecretId=os.environ["CLOUD_CREDS_SECRET"])["SecretString"])
        if not cfg.get("azure_connection_string"):
            return None  # Azure aún no configurado (solo GCP en el secreto)
        _container = BlobServiceClient.from_connection_string(
            cfg["azure_connection_string"]).get_container_client(cfg["azure_container"])
    return _container


def handler(event, context):
    try:
        container = _get_container()
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print("Secreto telecorp/cloud-creds aún no creado: se omite el respaldo en Azure")
            return
        raise
    if container is None:
        print("Azure aún no configurado en telecorp/cloud-creds: se omite el respaldo")
        return

    rows = []
    for rec in event["Records"]:
        img = rec["dynamodb"].get("NewImage")
        if img:
            row = {k: _deser.deserialize(v) for k, v in img.items()}
            row["_op"] = rec["eventName"]
            rows.append(row)
    if not rows:
        return

    #si el lote se reintenta, se sobrescribe (sin duplicados)
    first_seq = event["Records"][0]["dynamodb"]["SequenceNumber"]
    name = f"incidents/{datetime.now(timezone.utc):%Y/%m/%d}/{first_seq}.jsonl"
    body = "\n".join(json.dumps(r, default=_default) for r in rows)
    container.upload_blob(name=name, data=body, overwrite=True)
    print(f"Respaldados {len(rows)} registros en Azure: {name}")
