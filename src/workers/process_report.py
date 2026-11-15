import json
import time

from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

from shared.common import geohash, get_config, incidents_table, now_iso, put_event, to_dec, zone_table


def handler(event, context):
    failures = []
    for record in event["Records"]:
        try:
            process(json.loads(record["body"]))
        except Exception as e:  #el mensaje vuelve a la cola (y luego a la DLQ)
            print(f"ERROR {record['messageId']}: {e}")
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures}


def process(r):
    cfg = get_config()
    zone = geohash(r["lat"], r["lon"])
    ts = r["receivedAt"]
    pk = f"INC#{r['reportId']}"

    item = {
        "pk": pk, "sk": "META",
        "incidentId": r["reportId"],
        "type": "USER_REPORT",
        "status": "REGISTRADA",
        "zone": zone,
        "userId": r["userId"],
        "serviceNumber": r["serviceNumber"],
        "email": r.get("email"),
        "phone": r.get("phone"),
        "lat": to_dec(r["lat"]), "lon": to_dec(r["lon"]),
        "occurredAt": r["occurredAt"],
        "problemType": r["problemType"],
        "description": r["description"],
        "createdAt": ts, "updatedAt": ts,
        "gsi1pk": "STATUS#REGISTRADA", "gsi1sk": ts,
        "gsi2pk": f"USER#{r['userId']}", "gsi2sk": ts,
        "gsi3pk": f"ZONE#{zone}", "gsi3sk": ts,
    }
    item = {k: v for k, v in item.items() if v is not None}

    try:
        incidents_table.put_item(Item=item, ConditionExpression="attribute_not_exists(pk)")
        incidents_table.put_item(Item={
            "pk": pk, "sk": f"EVENT#{ts}",
            "status": "REGISTRADA", "note": "Reporte recibido", "at": ts,
        })
    except ClientError as e:
        if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise

    check_zone(zone, r["userId"], cfg)


def check_zone(zone, user_id, cfg):
    now = int(time.time())
    window = int(cfg["zone_window_hours"]) * 3600
    zpk = f"ZONE#{zone}"

    #1 item por usuario y zona -> cuenta usuarios DISTINTOS
    zone_table.put_item(Item={"pk": zpk, "sk": f"USER#{user_id}", "expiresAt": now + window})

    count = zone_table.query(
        KeyConditionExpression=Key("pk").eq(zpk) & Key("sk").begins_with("USER#"),
        FilterExpression=Attr("expiresAt").gt(now),
        Select="COUNT",
    )["Count"]

    if count < int(cfg["zone_threshold"]):
        return


    try:
        zone_table.put_item(
            Item={"pk": zpk, "sk": "ACTIVE_INCIDENT", "expiresAt": now + window},
            ConditionExpression="attribute_not_exists(pk) OR expiresAt < :now",
            ExpressionAttributeValues={":now": now},
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return
        raise

    put_event("telecorp.reports", "ZoneThresholdReached",
              {"zone": zone, "count": count, "detectedAt": now_iso()})
