import os
import time
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from shared.common import incidents_table, notifications_table, now_iso

sns = boto3.client("sns")
ses = boto3.client("sesv2")

STATUS_TEXT = {
    "REGISTRADA": "Tu incidencia fue registrada.",
    "EN_REVISION": "Estamos evaluando tu incidencia.",
    "EN_ATENCION": "El equipo tecnico esta atendiendo tu incidencia.",
    "SOLUCIONADA": "El servicio fue restablecido. Gracias por tu paciencia.",
    "CERRADA": "Tu incidencia fue cerrada.",
}


def handler(event, context):
    detail_type = event.get("detail-type")
    detail = event.get("detail", event)
    if detail_type == "IncidentStatusChanged":
        message = STATUS_TEXT.get(detail.get("to"), f"Nuevo estado: {detail.get('to')}")
        notify_one(detail, message, detail.get("to", "ACTUALIZADA"))
        return {"notified": 1}
    if detail_type == "AntennaStateChanged":
        return proactive_antenna_alert(detail)
    if detail.get("mode") == "zone":
        return notify_zone(detail)
    return {"ignored": True}


def save_notification(user_id, incident_id, status, message, channels):
    if not user_id:
        return
    ts = now_iso()
    notifications_table.put_item(Item={
        "userId": str(user_id),
        "createdAt": f"{ts}#{uuid.uuid4().hex[:8]}",
        "incidentId": incident_id or "ZONE",
        "status": status,
        "message": message,
        "channels": channels,
        "expiresAt": int(time.time()) + 90 * 86400,
    })


def deliver(email, phone, subject, message):
    channels = []
    sender = os.environ.get("NOTIFICATION_FROM_EMAIL", "").strip()
    if email and sender:
        try:
            ses.send_email(
                FromEmailAddress=sender,
                Destination={"ToAddresses": [email]},
                Content={"Simple": {"Subject": {"Data": subject}, "Body": {"Text": {"Data": message}}}},
            )
            channels.append("EMAIL")
        except ClientError as exc:
            print(f"SES omitido para {email}: {exc.response['Error']['Code']}")
    if phone and str(phone).startswith("+"):
        try:
            sns.publish(PhoneNumber=str(phone), Message=message)
            channels.append("SMS")
        except ClientError as exc:
            print(f"SMS omitido para {phone[-4:]}: {exc.response['Error']['Code']}")
    return channels or ["IN_APP"]


def notify_one(detail, message, status):
    channels = deliver(detail.get("email"), detail.get("phone"),
                       f"Red TeleCorp: {status}", message)
    save_notification(detail.get("userId"), detail.get("incidentId"), status, message, channels)


def notify_zone(detail):
    zone = detail["zone"]
    problem_type = detail.get("problemType")
    result = incidents_table.query(
        IndexName="byZone",
        KeyConditionExpression=Key("gsi3pk").eq(f"ZONE#{zone}"),
        ScanIndexForward=False,
    )
    seen, notified = set(), 0
    for item in result.get("Items", []):
        user_id = item.get("userId")
        if (item.get("type") != "USER_REPORT" or not user_id or user_id in seen
                or (problem_type and item.get("problemType") != problem_type)):
            continue
        seen.add(user_id)
        notify_one({**item, "incidentId": detail.get("incidentId", item.get("incidentId"))},
                   detail["message"], detail.get("status", "EN_REVISION"))
        notified += 1
    return {"notified": notified}


def proactive_antenna_alert(detail):
    state = detail.get("to")
    if state not in {"CAIDA", "INHABILITADA"} and not detail.get("recovered"):
        return {"ignored": True}
    recovered = bool(detail.get("recovered"))
    subject = ("RECUPERADA" if recovered else "ALERTA PROACTIVA") + f": {detail.get('antennaId')}"
    message = (f"Antena {detail.get('antennaId')} en zona {detail.get('zone')}: "
               f"{detail.get('from')} -> {state}. Trafico: {detail.get('gbPerMin')} GB/min.")
    sns.publish(TopicArn=os.environ["ALERTS_TOPIC_ARN"], Subject=subject[:100], Message=message)
    return {"alerted": True, "recovered": recovered}
