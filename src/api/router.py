import json
import os
import uuid
from collections import Counter
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from shared.common import (TRANSITIONS, antennas_table, incidents_table, notifications_table,
                           now_iso, put_event, response)

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
        if route == "GET /analytics/summary":
            return analytics_summary()
        if route == "GET /notifications/{userId}":
            return user_notifications(p["userId"])
    except json.JSONDecodeError:
        return response(400, {"error": "JSON inválido"})
    return response(404, {"error": "Ruta no encontrada"})


def list_incidents(status):
    if not status or status.upper() == "ALL":
        items = incidents_table.scan(
            FilterExpression="#sk = :meta",
            ExpressionAttributeNames={"#sk": "sk"},
            ExpressionAttributeValues={":meta": "META"},
        )["Items"]
        items.sort(key=lambda item: item.get("createdAt", ""), reverse=True)
        return response(200, {"items": items[:50]})
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
        update = "SET #s = :new, gsi1pk = :g, updatedAt = :ts"
        values = {":new": new, ":g": f"STATUS#{new}", ":ts": ts, ":old": old}
        if new == "SOLUCIONADA":
            update += ", resolvedAt = :ts"
        if new == "CERRADA":
            update += ", closedAt = :ts"
        incidents_table.update_item(
            Key=key,
            UpdateExpression=update,
            ConditionExpression="#s = :old",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues=values,
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
        "userId": current.get("userId"), "problemType": current.get("problemType"),
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


def user_notifications(user_id):
    result = notifications_table.query(
        KeyConditionExpression=Key("userId").eq(str(user_id)),
        ScanIndexForward=False,
        Limit=50,
    )
    return response(200, {"items": result.get("Items", [])})


def _hours_between(start, end):
    try:
        return round((datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() / 3600, 2)
    except (TypeError, ValueError):
        return None


def analytics_summary():
    items = incidents_table.scan(
        FilterExpression="#sk = :meta",
        ExpressionAttributeNames={"#sk": "sk"},
        ExpressionAttributeValues={":meta": "META"},
    )["Items"]
    reports = [item for item in items if item.get("type") == "USER_REPORT"]
    collective = [item for item in items if item.get("type") == "COLLECTIVE"]
    durations = [
        value for value in (_hours_between(item.get("createdAt"), item.get("resolvedAt") or item.get("closedAt"))
                            for item in items) if value is not None
    ]
    antennas = antennas_table.scan()["Items"]
    recurrent = sorted(
        ({"antennaId": item["antennaId"], "failCount": int(item.get("failCount", 0)),
          "state": item.get("state"), "zone": item.get("zone")} for item in antennas),
        key=lambda item: item["failCount"], reverse=True,
    )[:5]
    return response(200, {
        "totals": {"reports": len(reports), "collectiveIncidents": len(collective),
                   "affectedUsers": len({item.get("userId") for item in reports if item.get("userId")})},
        "byStatus": dict(Counter(item.get("status", "DESCONOCIDO") for item in items)),
        "byProblemType": dict(Counter(item.get("problemType", "OTRO") for item in reports)),
        "topZones": [{"zone": zone, "count": count}
                     for zone, count in Counter(item.get("zone") for item in reports if item.get("zone")).most_common(5)],
        "recurrentAntennas": recurrent,
        "averageResolutionHours": round(sum(durations) / len(durations), 2) if durations else None,
    })
