"""DynamoDB Streams -> GCP Pub/Sub -> BigQuery (analítica histórica)."""
import base64
import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError

_deser = TypeDeserializer()
_cfg, _session = None, None


def _default(o):
    if isinstance(o, Decimal):
        return float(o)
    if isinstance(o, set):
        return sorted(o)
    return str(o)


def _setup():
    global _cfg, _session
    if _cfg is None:
        from google.auth.transport.requests import AuthorizedSession
        from google.oauth2 import service_account

        raw = boto3.client("secretsmanager").get_secret_value(
            SecretId=os.environ["CLOUD_CREDS_SECRET"])["SecretString"]
        _cfg = json.loads(raw)
        creds = service_account.Credentials.from_service_account_info(
            _cfg["gcp_service_account"], scopes=["https://www.googleapis.com/auth/pubsub"])
        _session = AuthorizedSession(creds)
    return _cfg, _session


def handler(event, context):
    try:
        cfg, session = _setup()
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print("Secreto telecorp/cloud-creds aún no creado: se omite la exportación a GCP")
            return
        raise

    rows = []
    for rec in event["Records"]:
        img = rec["dynamodb"].get("NewImage")
        if img:
            row = {k: _deser.deserialize(v) for k, v in img.items()}
            row["_op"] = rec["eventName"]
            rows.append(row)
    if not rows:
        return

    url = (f"https://pubsub.googleapis.com/v1/projects/{cfg['gcp_project']}"
           f"/topics/{cfg['gcp_topic']}:publish")
    msgs = [{"data": base64.b64encode(json.dumps(r, default=_default).encode()).decode()} for r in rows]
    session.post(url, json={"messages": msgs}, timeout=20).raise_for_status()
    print(f"Exportados {len(msgs)} registros a GCP")
