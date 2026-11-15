import json
import os

import boto3

from shared.common import new_id, now_iso, response

sqs = boto3.client("sqs")

REQUIRED = ["documentId", "serviceNumber", "lat", "lon", "occurredAt", "problemType", "description"]
PROBLEM_TYPES = ["SIN_INTERNET", "SIN_SENAL", "LLAMADAS", "SMS", "LENTITUD", "OTRO"]


def build_report(body):
    missing = [f for f in REQUIRED if body.get(f) in (None, "")]
    if missing:
        return None, f"Faltan campos: {', '.join(missing)}"
    if body["problemType"] not in PROBLEM_TYPES:
        return None, f"problemType inválido. Válidos: {', '.join(PROBLEM_TYPES)}"
    try:
        lat, lon = float(body["lat"]), float(body["lon"])
    except (TypeError, ValueError):
        return None, "lat/lon deben ser numéricos"
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None, "Coordenadas fuera de rango"
    return {
        "reportId": new_id("INC"),
        "userId": str(body["documentId"]),
        "serviceNumber": str(body["serviceNumber"]),
        "email": body.get("email") or None,
        "phone": body.get("phone") or None,
        "lat": lat,
        "lon": lon,
        "occurredAt": str(body["occurredAt"]),
        "problemType": body["problemType"],
        "description": str(body["description"])[:1000],
        "receivedAt": now_iso(),
    }, None


def enqueue(report):
    sqs.send_message(QueueUrl=os.environ["REPORTS_QUEUE_URL"], MessageBody=json.dumps(report))


def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {"error": "JSON inválido"})
    report, error = build_report(body)
    if error:
        return response(400, {"error": error})
    enqueue(report)
    return response(202, {"reportId": report["reportId"], "status": "REGISTRADA"})
