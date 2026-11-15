import urllib.parse

import boto3

from shared.common import incidents_table, now_iso, put_event

rek = boto3.client("rekognition")

INFRA = {"Antenna", "Utility Pole", "Tower", "Cable", "Wire", "Electrical Device"}
HAZARD = {"Fire", "Smoke", "Flood", "Explosion", "Rubble", "Storm"}


def handler(event, context):
    for rec in event["Records"]:
        bucket = rec["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(rec["s3"]["object"]["key"])  # incidents/{id}/{uuid}.jpg
        incident_id = key.split("/")[1]
        image = {"S3Object": {"Bucket": bucket, "Name": key}}
        db_key = {"pk": f"INC#{incident_id}", "sk": "META"}

        if rek.detect_moderation_labels(Image=image, MinConfidence=80)["ModerationLabels"]:
            incidents_table.update_item(
                Key=db_key,
                UpdateExpression="SET imageStatus = :s",
                ExpressionAttributeValues={":s": "RECHAZADA"},
            )
            continue

        labels = {l["Name"] for l in rek.detect_labels(Image=image, MaxLabels=20, MinConfidence=75)["Labels"]}
        texts = [t["DetectedText"] for t in rek.detect_text(Image=image)["TextDetections"]
                 if t["Type"] == "LINE"][:10]
        hazard, infra = sorted(labels & HAZARD), sorted(labels & INFRA)

        # Si el META aún no existe (llega por SQS), falla y S3 reintenta la invocación
        incidents_table.update_item(
            Key=db_key,
            UpdateExpression=("SET imageKey = :k, imageStatus = :s, imageLabels = :l, imageText = :t, "
                              "physicalDamage = :d, updatedAt = :ts"),
            ConditionExpression="attribute_exists(pk)",
            ExpressionAttributeValues={":k": key, ":s": "ANALIZADA", ":l": sorted(labels), ":t": texts,
                                       ":d": bool(hazard), ":ts": now_iso()},
        )

        if hazard:
            put_event("telecorp.ai", "PhysicalDamageDetected",
                      {"incidentId": incident_id, "hazard": hazard, "infra": infra})
