import json
from datetime import datetime, timedelta, timezone

from boto3.dynamodb.conditions import Attr, Key

from shared.common import antennas_table, dumps, incidents_table
from shared.llm import get_client, model_id

SYSTEM = """Eres analista del NOC de una empresa de telecomunicaciones. Recibes los reportes de
usuarios de una zona en las últimas 24 h y el estado de las antenas cercanas. Responde SOLO con un
objeto JSON con estas claves:
"resumen" (máx. 3 frases), "causa_probable", "accion_recomendada",
"prioridad" (entero 1-5; 5 = crítica: muchos afectados, antenas caídas, daño físico en fotos,
o zona con hospitales/colegios/industria), "mensaje_usuarios" (máx. 300 caracteres, tono cordial,
sin prometer plazos)."""

DEFAULT = {
    "resumen": "Sin resumen de IA",
    "causa_probable": "Por determinar",
    "accion_recomendada": "Verificar infraestructura de la zona",
    "prioridad": 3,
    "mensaje_usuarios": "Detectamos una incidencia en tu zona y ya la estamos evaluando.",
}


def handler(event, context):
    zone, count = event["zone"], event["count"]
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    items = incidents_table.query(
        IndexName="byZone",
        KeyConditionExpression=Key("gsi3pk").eq(f"ZONE#{zone}") & Key("gsi3sk").gte(since),
    )["Items"]
    reports = [{"tipo": i.get("problemType"), "descripcion": i.get("description"),
                "hora": i.get("occurredAt"), "etiquetas_foto": i.get("imageLabels", [])}
               for i in items if i.get("type") == "USER_REPORT"][:100]

    antennas = antennas_table.scan(FilterExpression=Attr("zone").begins_with(zone[:5]))["Items"]
    antennas = [{"id": a["antennaId"], "estado": a.get("state"), "gb_min": a.get("gbPerMin"),
                 "fallas": a.get("failCount", 0)} for a in antennas]

    prompt = (f"Zona (geohash): {zone}\nUsuarios distintos afectados: {count}\n"
              f"Reportes:\n{dumps(reports)}\nAntenas cercanas:\n{dumps(antennas)}")

    resp = get_client().messages.create(
        model=model_id(),
        max_tokens=4000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        output_config={"effort": "low"},
    )
    if resp.stop_reason == "refusal":
        return DEFAULT

    text = "".join(b.text for b in resp.content if b.type == "text")
    try:
        data = json.loads(text[text.find("{"): text.rfind("}") + 1])
    except ValueError:
        return {**DEFAULT, "resumen": text[:500] or DEFAULT["resumen"]}

    out = {**DEFAULT, **{k: str(data[k]) for k in DEFAULT if k in data and k != "prioridad"}}
    try:
        out["prioridad"] = max(1, min(5, int(data.get("prioridad", 3))))
    except (TypeError, ValueError):
        out["prioridad"] = 3
    return out
