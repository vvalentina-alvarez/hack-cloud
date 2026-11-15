import json
import os
import time
import uuid

from boto3.dynamodb.conditions import Key

from api.create_report import PROBLEM_TYPES, build_report, enqueue
from shared.common import dumps, dynamodb, incidents_table, response
from shared.llm import get_client, model_id

chat_table = dynamodb.Table(os.environ["CHAT_TABLE"])

SYSTEM = """Eres el asistente de soporte de Red TeleCorp. Ayudas a los clientes a:
1) registrar una incidencia de su servicio (internet, señal, llamadas, SMS),
2) consultar el estado de sus incidencias.
Para registrar necesitas: número de documento, número de servicio, ubicación (lat/lon; si no
llegó la ubicación del dispositivo, pide al cliente que pulse "Compartir ubicación"), fecha y
hora aproximada del problema, tipo de problema y una descripción breve. Pide email y/o celular
para avisarle del avance; si no quiere darlos, usa cadena vacía.
Pide solo los datos que falten. Antes de registrar, resume los datos y espera la confirmación
del cliente. Responde en español, breve y cordial. No inventes estados ni plazos: usa solo lo que
devuelven las herramientas."""

TOOLS = [
    {
        "name": "registrar_incidencia",
        "description": "Registra la incidencia del cliente. Úsala solo cuando el cliente haya confirmado los datos.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "documentId": {"type": "string"},
                "serviceNumber": {"type": "string"},
                "lat": {"type": "number"},
                "lon": {"type": "number"},
                "occurredAt": {"type": "string", "description": "Fecha y hora en ISO 8601"},
                "problemType": {"type": "string", "enum": PROBLEM_TYPES},
                "description": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
            },
            "required": ["documentId", "serviceNumber", "lat", "lon", "occurredAt",
                         "problemType", "description", "email", "phone"],
        },
    },
    {
        "name": "consultar_incidencia",
        "description": "Devuelve el estado actual y el historial de una incidencia por su ID (ej. INC-1a2b3c4d5e).",
        "strict": True,
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {"incidentId": {"type": "string"}},
            "required": ["incidentId"],
        },
    },
    {
        "name": "listar_mis_incidencias",
        "description": "Lista las incidencias registradas por un número de documento.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {"documentId": {"type": "string"}},
            "required": ["documentId"],
        },
    },
]


def run_tool(name, args):
    if name == "registrar_incidencia":
        report, error = build_report(args)
        if error:
            return {"ok": False, "error": error}
        enqueue(report)
        return {"ok": True, "incidentId": report["reportId"], "status": "REGISTRADA"}

    if name == "consultar_incidencia":
        items = incidents_table.query(
            KeyConditionExpression=Key("pk").eq(f"INC#{args['incidentId']}"))["Items"]
        meta = next((i for i in items if i["sk"] == "META"), None)
        if not meta:
            return {"ok": False, "error": "No existe esa incidencia (puede tardar unos segundos en aparecer)"}
        history = [{"estado": i["status"], "nota": i.get("note", ""), "fecha": i["at"]}
                   for i in sorted(items, key=lambda i: i["sk"]) if i["sk"].startswith("EVENT#")]
        return {"ok": True, "estado": meta["status"], "tipo": meta.get("problemType"), "historial": history}

    if name == "listar_mis_incidencias":
        # TODO con Cognito: tomar el documentId del token, no del modelo
        items = incidents_table.query(
            IndexName="byUser",
            KeyConditionExpression=Key("gsi2pk").eq(f"USER#{args['documentId']}"),
            ScanIndexForward=False,
            Limit=10,
        )["Items"]
        return {"ok": True, "incidencias": [
            {"id": i["incidentId"], "estado": i["status"], "tipo": i.get("problemType"), "fecha": i["createdAt"]}
            for i in items]}

    return {"ok": False, "error": f"Herramienta desconocida: {name}"}


def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {"error": "JSON inválido"})
    text = (body.get("message") or "").strip()
    if not text:
        return response(400, {"error": "message es obligatorio"})
    loc = body.get("location")
    if loc:
        text += f"\n[Ubicación del dispositivo: lat={loc['lat']}, lon={loc['lon']}]"

    session_id = body.get("sessionId") or uuid.uuid4().hex
    saved = chat_table.get_item(Key={"sessionId": session_id}).get("Item")
    messages = json.loads(saved["messages"]) if saved else []
    messages.append({"role": "user", "content": text})

    client = get_client()
    reply = "Lo siento, no pude completar tu solicitud. Intenta nuevamente."
    for _ in range(5):  # máximo 5 vueltas de herramientas por mensaje
        resp = client.messages.create(
            model=model_id(),
            max_tokens=16000,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
            output_config={"effort": "low"},  # chat: respuestas rápidas
        )
        if resp.stop_reason == "refusal":
            return response(200, {"sessionId": session_id,
                                  "reply": "No puedo ayudarte con eso. ¿Tienes algún problema con tu servicio?"})

        # Se guarda el contenido completo (incluye bloques de thinking) sin modificarlo
        messages.append({"role": "assistant",
                         "content": [b.model_dump(exclude_none=True) for b in resp.content]})

        if resp.stop_reason != "tool_use":
            reply = "".join(b.text for b in resp.content if b.type == "text")
            break

        results = [{"type": "tool_result", "tool_use_id": b.id, "content": dumps(run_tool(b.name, b.input))}
                   for b in resp.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})

    chat_table.put_item(Item={"sessionId": session_id, "messages": json.dumps(messages),
                              "expiresAt": int(time.time()) + 86400})
    return response(200, {"sessionId": session_id, "reply": reply})
