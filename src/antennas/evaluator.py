import json

from shared.common import antennas_table, classify, geohash, put_event, to_dec

FAILURE_STATES = {"CAIDA", "INHABILITADA"}


def handler(event, context):
    failures = []
    for record in event["Records"]:
        try:
            evaluate(json.loads(record["body"]))
        except Exception as e:
            print(f"ERROR {record['messageId']}: {e}")
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures}


def evaluate(m):
    new_state = classify(m["gbPerMin"])
    zone = geohash(m["lat"], m["lon"])
    key = {"antennaId": m["antennaId"]}

    old = antennas_table.update_item(
        Key=key,
        UpdateExpression="SET #st = :st, #gb = :gb, #lat = :lat, #lon = :lon, #z = :z, #ls = :at",
        ExpressionAttributeNames={"#st": "state", "#gb": "gbPerMin", "#lat": "lat",
                                  "#lon": "lon", "#z": "zone", "#ls": "lastSeen"},
        ExpressionAttributeValues={":st": new_state, ":gb": to_dec(m["gbPerMin"]),
                                   ":lat": to_dec(m["lat"]), ":lon": to_dec(m["lon"]),
                                   ":z": zone, ":at": m["at"]},
        ReturnValues="UPDATED_OLD",
    ).get("Attributes", {})

    old_state = old.get("state")
    if old_state == new_state:
        return  #sin cambio, no hay evento

    #falla nueva : pasar de un estado sano (NORMAL/SATURADA/desconocido) a uno de falla
    #CAIDA -> INHABILITADA es la misma falla que empeora, no se cuenta dos veces
    #INHABILITADA/CAIDA -> NORMAL es una recuperación, emite evento, pero no suma
    if new_state in FAILURE_STATES and old_state not in FAILURE_STATES:
        antennas_table.update_item(
            Key=key,
            UpdateExpression="ADD failCount :one",
            ExpressionAttributeValues={":one": 1},
        )

    put_event("telecorp.antennas", "AntennaStateChanged", {
        "antennaId": m["antennaId"], "from": old_state or "DESCONOCIDO", "to": new_state,
        "gbPerMin": m["gbPerMin"], "zone": zone, "at": m["at"],
        "recovered": old_state in FAILURE_STATES and new_state not in FAILURE_STATES,
    })
