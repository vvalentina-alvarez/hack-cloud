import json
import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from shared.common import TRANSITIONS, antennas_table, incidents_table, now_iso, put_event, response

s3 = boto3.client("s3")


def handler(event, context):
    route = event["routeKey"]
    p = event.get("pathParameters") or {}
    qs = event.get("queryStringParameters") or {}
    try:
        if route == "GET /incidents":
            return list_incidents(qs.get("status", "REGISTRADA"))
        if route == "GET /incidents/{id}":
            return get_incident(p["id"])
        if route == "PATCH /incidents/{id}/status":
            return change_status(p["id"], json.loads(event.get("body") or "{}"))
        if route == "POST /incidents/{id}/image-url":
            return image_upload_url(p["id"])
        if route == "GET /users/{userId}/incidents":
            return user_incidents(p["userId"])
        if route == "GET /antennas":
            return response(200, {"items": antennas_table.scan()["Items"]})
    except json.JSONDecodeError:
        return response(400, {"error": "JSON inválido"})
    return response(404, {"error": "Ruta no encontrada"})


def list_incidents(status):
    resp = incidents_table.query(
        IndexName="byStatus",
        KeyConditionExpression=Key("gsi1pk").eq(f"STATUS#{status}"),
        ScanIndexForward=False,
        Limit=50,
    )
    return response(200, {"items": resp["Items"]})


def user_incidents(user_id):
    resp = incidents_table.query(
        IndexName="byUser",
        KeyConditionExpression=Key("gsi2pk").eq(f"USER#{user_id}"),
        ScanIndexForward=False,
    )
    return response(200, {"items": resp["Items"]})


def get_incident(inc_id):
    items = incidents_table.query(KeyConditionExpression=Key("pk").eq(f"INC#{inc_id}"))["Items"]
    meta = next((i for i in items if i["sk"] == "META"), None)
    if not meta:
        return response(404, {"error": "Incidencia no encontrada"})
    history = sorted((i for i in items if i["sk"].startswith("EVENT#")), key=lambda i: i["sk"])
    return response(200, {"incident": meta, "history": history})


def change_status(inc_id, body):
    new, note = body.get("status"), body.get("note", "")
    key = {"pk": f"INC#{inc_id}", "sk": "META"}
    current = incidents_table.get_item(Key=key).get("Item")
    if not current:
        return response(404, {"error": "Incidencia no encontrada"})

    old = current["status"]
    allowed = TRANSITIONS.get(old, set())
    if new not in allowed:
        return response(409, {"error": f"Transición inválida {old} -> {new}", "allowed": sorted(allowed)})

    ts = now_iso()
    try:
        incidents_table.update_item(
            Key=key,
            UpdateExpression="SET #s = :new, gsi1pk = :g, updatedAt = :ts",
            ConditionExpression="#s = :old",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":new": new, ":g": f"STATUS#{new}", ":ts": ts, ":old": old},
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return response(409, {"error": "La incidencia cambió mientras se actualizaba, reintenta"})
        raise

    incidents_table.put_item(Item={
        "pk": key["pk"], "sk": f"EVENT#{ts}", "from": old, "status": new, "note": note, "at": ts,
    })
    put_event("telecorp.incidents", "IncidentStatusChanged", {
        "incidentId": inc_id, "from": old, "to": new, "zone": current.get("zone"),
        "email": current.get("email"), "phone": current.get("phone"),
    })
    return response(200, {"incidentId": inc_id, "from": old, "to": new})


def image_upload_url(inc_id):
    key = f"incidents/{inc_id}/{uuid.uuid4().hex}.jpg"
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": os.environ["UPLOADS_BUCKET"], "Key": key, "ContentType": "image/jpeg"},
        ExpiresIn=300,
    )
    return response(200, {"uploadUrl": url, "key": key})
