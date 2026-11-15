"""Genera docs/arquitectura.drawio (ábrelo en draw.io / diagrams.net para editarlo).

Uso: python docs/generar_diagrama.py
"""
import html
from pathlib import Path

cells = []
_n = [0]


def _id(prefix):
    _n[0] += 1
    return f"{prefix}{_n[0]}"


def esc(s):
    return html.escape(s, quote=True)


def vertex(label, x, y, w, h, style, cid=None):
    cid = cid or _id("v")
    cells.append(
        f'<mxCell id="{cid}" value="{esc(label)}" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
    )
    return cid


def edge(src, tgt, label="", style="", pts=None, sp=None, tp=None, lx=None):
    """lx: posición de la etiqueta a lo largo de la flecha (-1 = origen, 0 = centro, 1 = destino)."""
    cid = _id("e")
    geo = (f'<mxGeometry x="{lx}" relative="1" as="geometry">' if lx is not None
           else '<mxGeometry relative="1" as="geometry">')
    if sp:
        geo += f'<mxPoint x="{sp[0]}" y="{sp[1]}" as="sourcePoint"/>'
    if tp:
        geo += f'<mxPoint x="{tp[0]}" y="{tp[1]}" as="targetPoint"/>'
    if pts:
        geo += '<Array as="points">' + "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in pts) + "</Array>"
    geo += "</mxGeometry>"
    s = f' source="{src}"' if src else ""
    t = f' target="{tgt}"' if tgt else ""
    cells.append(f'<mxCell id="{cid}" value="{esc(label)}" style="{style}" edge="1" parent="1"{s}{t}>{geo}</mxCell>')
    return cid


# ---------------------------------------------------------------- estilos
def aws(icon, fill, grad):
    return (f"sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor={grad};gradientDirection=north;"
            f"fillColor={fill};strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;"
            f"align=center;html=1;fontSize=9;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;"
            f"resIcon=mxgraph.aws4.{icon};")


PINK = ("#B0084D", "#FF4F8B")      # integración de aplicaciones / gestión
ORANGE = ("#C8511B", "#F78E04")    # cómputo
DB = ("#2E27AD", "#527FFF")        # bases de datos
GREEN = ("#3F8624", "#7AA116")     # almacenamiento
ML = ("#116D5B", "#4AB29A")        # IA / ML
RED = ("#BD0816", "#F54749")       # seguridad / front-end

I_APIGW = aws("api_gateway", *PINK)
I_SQS = aws("sqs", *PINK)
I_SNS = aws("sns", *PINK)
I_EB = aws("eventbridge", *PINK)
I_SFN = aws("step_functions", *PINK)
I_CW = aws("cloudwatch_2", *PINK)
I_DDB = aws("dynamodb", *DB)
I_S3 = aws("s3", *GREEN)
I_BEDROCK = aws("bedrock", *ML)
I_REKO = aws("rekognition", *ML)
I_SECRETS = aws("secrets_manager", *RED)
I_AMPLIFY = aws("amplify", *RED)

GCP_HEX = ("sketch=0;html=1;fillColor=#5184F3;strokeColor=none;verticalAlign=top;labelPosition=center;"
           "verticalLabelPosition=bottom;align=center;spacingTop=-6;fontSize=9;fontStyle=0;fontColor=#424242;"
           "shape=mxgraph.gcp2.hexIcon;prIcon=")
I_AZ_BLOB = ("image;aspect=fixed;html=1;points=[];align=center;fontSize=9;"
             "image=img/lib/azure2/storage/Storage_Accounts.svg;")

COLUMN = ("rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFAF5;strokeColor=#FF8000;strokeWidth=2;arcSize=2;"
          "verticalAlign=top;fontStyle=1;fontSize=13;spacingTop=4;")
TXT = "text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;fontSize=9;"
TXT_C = "text;html=1;align=center;verticalAlign=top;whiteSpace=wrap;fontSize=9;"
TBL = "text;html=1;align=center;verticalAlign=top;whiteSpace=wrap;fontSize=9;fontColor=#3333CC;"
L_API = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#FF8000;fontSize=9;arcSize=10;"
L_TRIG = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE6EE;strokeColor=#E7157B;strokeWidth=1.5;fontSize=9;arcSize=10;"
L_INT = "rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#3D7EDB;strokeWidth=1.5;fontSize=9;arcSize=10;"
STATE = "rounded=1;whiteSpace=wrap;html=1;fillColor=#F3E5F5;strokeColor=#9C27B0;fontSize=9;arcSize=10;"
STATE_D = STATE + "dashed=1;"
NOTE = ("rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#999999;dashed=1;fontSize=9;arcSize=6;"
        "align=left;spacingLeft=4;")
BOX = "rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#666666;fontSize=9;arcSize=10;"

_E = "html=1;fontSize=9;edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=classic;labelBackgroundColor=#FFFFFF;"
E_RW = _E + "startArrow=classic;strokeColor=#3333CC;strokeWidth=2;fontColor=#3333CC;"
E_W = _E + "strokeColor=#3333CC;strokeWidth=2;fontColor=#3333CC;"
E_EVT = _E + "strokeColor=#E7157B;strokeWidth=1.5;fontColor=#E7157B;"
E_EVT_D = E_EVT + "dashed=1;"
E_HTTP = _E + "strokeColor=#232F3E;strokeWidth=2;fontColor=#232F3E;"
E_INV = _E + "strokeColor=#3D7EDB;strokeWidth=1.5;dashed=1;fontColor=#3D7EDB;"
E_GREEN = _E + "strokeColor=#2D7600;strokeWidth=2;fontColor=#2D7600;"
E_GCP = _E + "strokeColor=#4285F4;strokeWidth=2;fontColor=#4285F4;"
E_AZ = _E + "strokeColor=#0078D4;strokeWidth=2;fontColor=#0078D4;"
E_SFN = _E + "strokeColor=#9C27B0;strokeWidth=1.5;fontColor=#9C27B0;"
E_SFN_D = E_SFN + "dashed=1;"

# ---------------------------------------------------------------- fila superior
users = vertex("<b>Usuarios</b><br>Clientes (web / celular) · Operadores NOC", 10, 20, 190, 55, BOX)
vertex("<b>Amplify Hosting</b> · React + Vite (SPA) · portal de reportes, chat y mapa NOC",
       215, 0, 330, 18, TXT_C)
amplify = vertex("", 300, 22, 48, 48, I_AMPLIFY)
git = vertex("<b>Repositorio Git</b><br>template.yaml (AWS SAM) · src/ · frontend/", 620, 22, 220, 50, BOX)
cfn = vertex("<b>CloudFormation</b> (vía AWS SAM)<br>1 stack: telecorp-dev · sam build &amp;&amp; sam deploy<br>"
             "Learner Lab · us-east-1", 900, 15, 330, 60,
             "rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;strokeWidth=2;fontSize=9;arcSize=10;")
vertex("<b>Externo</b> (desde el navegador)<br>OpenStreetMap: mapa de antenas e incidentes (Leaflet)<br>"
       "geolocalización del dispositivo", 1300, 20, 330, 55, BOX)

edge(users, amplify, "HTTPS", E_HTTP)
edge(git, amplify, "npm run build → deploy", E_HTTP)
edge(git, cfn, "sam deploy", E_HTTP)

# ---------------------------------------------------------------- columnas
COLX = [5, 260, 515, 770, 1025, 1280, 1535]
TOP, H, W = 200, 610, 240


def row(i, step=34):
    return 285 + step * i


def column(i, title):
    return vertex(title, COLX[i], TOP, W, H, COLUMN)


def header(i, icon_style, text):
    x = COLX[i]
    ic = vertex("", x + 12, 228, 40, 40, icon_style)
    vertex(text, x + 56, 222, 178, 52, TXT)
    return ic


def lam(i, label, style, r, step=34, h=30):
    return vertex(label, COLX[i] + 10, row(r, step), 220, h, style)


def table(i, label):
    x = COLX[i]
    t = vertex("", x + 96, 690, 48, 48, I_DDB)
    vertex(label, x + 10, 742, 220, 62, TBL)
    return t


# ---- M1 Reportes e incidencias
c1 = column(0, "M1 · Reportes e incidencias")
header(0, I_APIGW, "<b>API Gateway</b> · api-telecorp (HTTP API)<br>CORS · 8 rutas<br>auth: Cognito (siguiente fase)")
crear = lam(0, "<b>crearReporte</b><br>POST /reports → valida y encola (202)", L_API, 0)
lam(0, "<b>listar</b><br>GET /incidents?status=", L_API, 1)
lam(0, "<b>detalle</b><br>GET /incidents/{id} (+ historial)", L_API, 2)
cambiar = lam(0, "<b>cambiarEstado</b><br>PATCH /incidents/{id}/status", L_API, 3)
lam(0, "<b>urlImagen</b><br>POST /incidents/{id}/image-url (5 min)", L_API, 4)
lam(0, "<b>misIncidencias</b><br>GET /users/{userId}/incidents", L_API, 5)
lam(0, "<b>listarAntenas</b><br>GET /antennas (lee t_antenas)", L_API, 6)
vertex("rutas GET/PATCH/image-url: 1 Lambda router (ApiFunction)<br>estados: REGISTRADA → EN_REVISION → "
       "ATENDIDA → SOLUCIONADA → CERRADA (historial EVENT#)", 15, 523, 220, 62, NOTE)
t_inc = table(0, "<b>t_incidencias</b> (tabla central)<br>PK=INC#id · SK=META | EVENT#ts<br>"
                 "GSI byStatus · byUser · byZone<br>Streams ON · PITR")
edge(None, t_inc, "R/W", E_RW, sp=(125, 592))

# ---- M2 Procesamiento y zonas
c2 = column(1, "M2 · Procesamiento y zonas")
header(1, I_SQS, "<b>SQS</b> · q-reportes<br>event source mapping · lote 10<br>máx. 2 concurrentes (límite del lab)")
proc = lam(1, "<b>procesarReporte</b><br>SQS q-reportes · idempotente", L_TRIG, 0)
vertex("1) guarda META + EVENT en t_incidencias<br>2) zona = geohash(lat, lon), precisión 6 (~1 km)<br>"
       "3) registra al usuario en la zona (TTL 24 h)<br>4) cuenta usuarios DISTINTOS de la zona",
       270, 325, 220, 64, NOTE)
vertex("<b>≥ 10 usuarios en &lt; 24 h</b> → lock ACTIVE_INCIDENT (1 incidente por zona) → evento "
       "<b>ZoneThresholdReached</b><br>umbral y ventana leídos de Secrets Manager", 270, 397, 220, 72, NOTE)
t_zon = table(1, "<b>t_zonas</b><br>PK=ZONE#geohash<br>SK=USER#id | ACTIVE_INCIDENT<br>TTL 24 h (expiresAt)")
edge(None, t_zon, "R/W", E_RW, sp=(380, 482))
edge(None, t_inc, "escribe META + EVENT", E_W, sp=(268, 714), pts=[(200, 714)])

# ---- M3 Antenas
c3 = column(2, "M3 · Antenas (monitoreo)")
header(2, I_EB, "<b>EventBridge</b> · regla rate(1 min)<br>simula 20 antenas que reportan<br>tráfico en GB/min")
sim = lam(2, "<b>simulador</b><br>EventBridge 1 min → SQS q-antenas", L_TRIG, 0)
evalu = lam(2, "<b>evaluador</b><br>SQS q-antenas · máquina de estados", L_TRIG, 1)
vertex("<b>Máquina de estados</b><br>0 GB/min → <font color=\"#666666\"><b>INHABILITADA</b></font><br>"
       "&lt; 60 → <font color=\"#CC0000\"><b>CAÍDA</b></font><br>60 – 129 → <font color=\"#2D7600\"><b>NORMAL</b>"
       "</font><br>&gt; 129 → <font color=\"#E67E00\"><b>SATURADA</b></font>", 525, 360, 220, 72, NOTE)
vertex("emite <b>AntennaStateChanged</b> solo si cambia el estado · failCount++ al caer → detecta antenas "
       "recurrentes (falla estructural)", 525, 440, 220, 50, NOTE)
t_ant = table(2, "<b>t_antenas</b><br>PK=antennaId<br>state · gbPerMin · zone · failCount · lastSeen")
edge(None, t_ant, "R/W", E_RW, sp=(635, 500))

# ---- M4 Asistente IA
c4 = column(3, "M4 · Asistente IA (chatbot)")
header(3, I_APIGW, "<b>API Gateway</b> · POST /chat<br>(misma api-telecorp)<br>timeout 29 s")
chat = lam(3, "<b>chat</b><br>POST /chat · bucle de herramientas (máx. 5)", L_API, 0)
bedrock = vertex("", 782, 332, 44, 44, I_BEDROCK)
bedrock_txt = vertex("<b>Amazon Bedrock</b> · Claude<br>anthropic.claude-opus-5-5<br>"
                     "alternativa: Vertex AI (LLM_PROVIDER)", 832, 326, 172, 56, TXT)
vertex("<b>Herramientas (tool use)</b><br>registrar_incidencia → misma validación de POST /reports → SQS<br>"
       "consultar_incidencia → t_incidencias<br>listar_mis_incidencias → GSI byUser", 780, 400, 220, 78, NOTE)
t_chat = table(3, "<b>t_chat</b><br>PK=sessionId · historial de la conversación<br>TTL 24 h")
edge(chat, bedrock, "", E_INV + "exitX=0.11;exitY=1;entryX=0.5;entryY=0;")
edge(None, t_chat, "R/W", E_RW, sp=(890, 490))

# ---- M5 Evidencias
c5 = column(4, "M5 · Evidencias (fotos)")
s3 = header(4, I_S3, "<b>S3</b> · telecorp-dev-uploads<br>privado · CORS PUT<br>subida directa desde el navegador")
analizar = lam(4, "<b>analizarImagen</b><br>S3 ObjectCreated · prefijo incidents/", L_TRIG, 0)
reko = vertex("", 1037, 332, 44, 44, I_REKO)
vertex("<b>Amazon Rekognition</b><br>DetectModerationLabels · DetectLabels · DetectText", 1087, 326, 172, 56, TXT)
vertex("foto inapropiada → imageStatus = RECHAZADA<br>fuego · humo · inundación → physicalDamage = true → "
       "evento <b>PhysicalDamageDetected</b><br>etiquetas y texto → t_incidencias (la IA los usa al priorizar)",
       1035, 400, 220, 90, NOTE)
edge(analizar, reko, "", E_INV + "exitX=0.11;exitY=1;entryX=0.5;entryY=0;")

# ---- M6 Incidente colectivo
c6 = column(5, "M6 · Incidente colectivo")
sfn = header(5, I_SFN, "<b>Step Functions</b> · CollectiveIncident<br>Standard · la inicia la regla<br>"
                       "ZoneThresholdRule (EventBridge)")
s0 = lam(5, "<b>1. AnalizarConIA</b><br>Lambda resumirZona · 2 reintentos", STATE, 0, step=44)
s1 = lam(5, "<b>2. IASinRespuesta</b> (si la IA falla)<br>Pass: prioridad 3 y mensaje por defecto", STATE_D, 1, step=44)
s2 = lam(5, "<b>3. CrearIncidenteColectivo</b><br>DynamoDB putItem directo · INC#COL-…", STATE, 2, step=44)
s3n = lam(5, "<b>4. NotificarNOC</b><br>SNS publish · resumen + prioridad", STATE, 3, step=44)
resumir = vertex("<b>resumirZona</b><br>sin ruta · invocada por Step Functions<br>"
                 "lee reportes (GSI byZone) + antenas → Claude", 1290, 482, 220, 44, L_INT)
vertex("escribe en t_incidencias: type=COLLECTIVE · affectedUsers · priority (1–5) · aiSummary · aiCause · "
       "aiAction · userMessage", 1290, 540, 220, 52, NOTE)
edge(s0, s1, "Catch", E_SFN_D)
edge(s1, s2, "", E_SFN)
edge(s2, s3n, "", E_SFN)
edge(s0, s2, "OK", E_SFN, pts=[(1514, 300), (1514, 388)])
edge(s0, resumir, "", E_INV + "exitX=0;exitY=0.5;entryX=0;entryY=0.5;", pts=[(1285, 300), (1285, 504)])
edge(resumir, bedrock_txt, "resumen, causa y prioridad (Messages API)", E_INV + "exitX=1;exitY=0.5;entryX=1;entryY=0.5;",
     pts=[(1527, 504), (1527, 165), (1017, 165), (1017, 354)])

# ---- M7 Exportación multinube
c7 = column(6, "M7 · Exportación multinube")
header(6, I_DDB, "<b>DynamoDB Streams</b> · t_incidencias<br>NEW_AND_OLD_IMAGES · lote 100<br>"
                 "3 reintentos · bisect en error")
exp_gcp = lam(6, "<b>exportarGCP</b><br>Stream → Pub/Sub (REST + service account)", L_TRIG, 0)
exp_az = lam(6, "<b>exportarAzure</b><br>Stream → Blob .jsonl por lote (idempotente)", L_TRIG, 1)
vertex("credenciales en Secrets Manager (telecorp/cloud-creds)<br>si el secreto aún no existe → omite sin fallar"
       "<br><b>AWS procesa · GCP analiza · Azure respalda</b>", 1545, 365, 220, 64, NOTE)

# ---------------------------------------------------------------- nubes externas
vertex("Google Cloud · analítica histórica", 1800, 200, 310, 380,
       "rounded=1;arcSize=3;whiteSpace=wrap;html=1;fillColor=#F1F6FE;strokeColor=#4285F4;strokeWidth=2;"
       "verticalAlign=top;fontStyle=1;fontSize=13;spacingTop=4;")
pubsub = vertex("", 1815, 245, 50, 44, GCP_HEX + "cloud_pubsub")
vertex("<b>Pub/Sub</b> · topic telecorp-incidents<br>suscripción BigQuery (escritura directa)", 1872, 240, 230, 50, TXT)
bq = vertex("", 1815, 325, 50, 44, GCP_HEX + "bigquery")
vertex("<b>BigQuery</b> · telecorp.incidents_raw<br>top zonas, antenas y tipos · duración · usuarios afectados",
       1872, 320, 230, 50, TXT)
looker = vertex("<b>Looker Studio</b><br>dashboard histórico para los responsables", 1815, 400, 280, 40,
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#4285F4;fontSize=9;arcSize=10;")
vertex("<b>Vertex AI</b> · Claude (opcional)<br>respaldo si Bedrock no está habilitado en Learner Lab", 1815, 455, 280, 45,
       "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#4285F4;dashed=1;fontSize=9;arcSize=10;")
vertex("service account <b>aws-publisher</b><br>roles: pubsub.publisher (+ aiplatform.user)", 1815, 515, 280, 45, NOTE)
edge(pubsub, bq, "suscripción", E_GCP)
edge(bq, looker, "", E_GCP)

vertex("Microsoft Azure · respaldo / DR", 1800, 600, 310, 210,
       "rounded=1;arcSize=3;whiteSpace=wrap;html=1;fillColor=#EEF6FD;strokeColor=#0078D4;strokeWidth=2;"
       "verticalAlign=top;fontStyle=1;fontSize=13;spacingTop=4;")
blob = vertex("", 1815, 648, 48, 38, I_AZ_BLOB)
vertex("<b>Blob Storage</b> · Standard_GRS (geo-redundante)<br>contenedor incidents/AAAA/MM/DD/*.jsonl",
       1870, 640, 232, 55, TXT)
vertex("copia de todo t_incidencias fuera de AWS<br>si AWS cae, el historial sigue disponible<br>"
       "(persistencia y alta disponibilidad)", 1815, 712, 280, 70, NOTE)

edge(exp_gcp, pubsub, "HTTPS", E_GCP, pts=[(1785, 300), (1785, 267)])
edge(exp_az, blob, "HTTPS", E_AZ, pts=[(1790, 334), (1790, 667)])

# ---------------------------------------------------------------- fila inferior: colas, bus, alertas
qrep = vertex("", 330, 905, 44, 44, I_SQS)
vertex("<b>q-reportes</b><br>API + chatbot", 300, 951, 104, 30, TXT_C)
dlq1 = vertex("", 440, 905, 44, 44, I_SQS)
vertex("<b>DLQ</b> · 3 intentos<br>retención 14 días", 410, 951, 104, 30, TXT_C)
qant = vertex("", 585, 905, 44, 44, I_SQS)
vertex("<b>q-antenas</b><br>métricas cada minuto", 555, 951, 104, 30, TXT_C)
dlq2 = vertex("", 695, 905, 44, 44, I_SQS)
vertex("<b>DLQ</b> · 3 intentos<br>retención 14 días", 665, 951, 104, 30, TXT_C)
edge(qrep, dlq1, "redrive", E_EVT)
edge(qant, dlq2, "redrive", E_EVT)

bus = vertex("", 1100, 905, 48, 48, I_EB)
vertex("<b>EventBridge</b> · bus telecorp-dev-bus<br>ZoneThresholdReached · AntennaStateChanged<br>"
       "IncidentStatusChanged · PhysicalDamageDetected", 1155, 900, 220, 58, TXT)
sns = vertex("", 1400, 990, 44, 44, I_SNS)
vertex("<b>SNS</b> · alertas<br>suscripción email", 1372, 1036, 100, 30, TXT_C)
noc = vertex("<b>Operadores NOC</b><br>email con resumen IA + prioridad", 1520, 990, 170, 44, BOX)
edge(sns, noc, "", E_EVT)

secrets = vertex("", 20, 905, 44, 44, I_SECRETS)
vertex("<b>Secrets Manager</b><br>ConfigSecret: umbral 10 · ventana 24 h<br>telecorp/cloud-creds: GCP + Azure",
       70, 898, 200, 58, TXT)

# ---------------------------------------------------------------- flujos entre módulos
# navegador -> API / S3
edge(amplify, c1, "", E_HTTP, pts=[(324, 105), (125, 105)])
edge(amplify, c4, "", E_HTTP, pts=[(324, 105), (890, 105)])
edge(amplify, s3, "PUT con URL firmada (5 min)", E_GREEN, pts=[(340, 118), (1059, 118)])

# reportes -> cola -> procesamiento
L, R, T, B = "exitX=0;exitY=0.5;", "exitX=1;exitY=0.5;", "exitX=0.5;exitY=0;", "exitX=0.5;exitY=1;"
EL, ER, ET = "entryX=0;entryY=0.5;", "entryX=1;entryY=0.5;", "entryX=0.5;entryY=0;"
edge(crear, qrep, "encola", E_EVT + R + EL, pts=[(241, 300), (241, 927)], lx=0)
edge(chat, qrep, "registrar_incidencia", E_EVT + L + "entryX=0;entryY=0.3;",
     pts=[(775, 300), (775, 866), (310, 866), (310, 918)], lx=-0.4)
edge(qrep, proc, "event source mapping", E_EVT + T + EL, pts=[(352, 888), (265, 888), (265, 300)], lx=0.3)

# antenas
edge(sim, qant, "", E_EVT + L + EL, pts=[(520, 300), (520, 927)])
edge(qant, evalu, "event source mapping", E_EVT + T + ER, pts=[(607, 888), (750, 888), (750, 334)])

# eventos al bus (las 3 flechas comparten el carril y=848)
PINK_TXT = "text;html=1;align=right;verticalAlign=middle;whiteSpace=wrap;fontSize=8;fontColor=#E7157B;"
edge(None, bus, "", E_EVT_D + "entryX=0;entryY=0.5;", sp=(200, 810), pts=[(200, 848), (1085, 848), (1085, 929)])
vertex("IncidentStatusChanged", 92, 812, 104, 12, PINK_TXT)
edge(None, bus, "", E_EVT + "entryX=0;entryY=0.5;", sp=(470, 810), pts=[(470, 848), (1085, 848), (1085, 929)])
vertex("ZoneThresholdReached", 362, 812, 104, 12, PINK_TXT)
edge(None, bus, "", E_EVT + "entryX=0;entryY=0.5;", sp=(700, 810), pts=[(700, 848), (1085, 848), (1085, 929)])
vertex("AntennaStateChanged", 592, 812, 104, 12, PINK_TXT)
edge(None, bus, "", E_EVT + ET, sp=(1124, 810))
vertex("PhysicalDamageDetected", 1128, 870, 110, 12, PINK_TXT.replace("align=right", "align=left"))

# bus -> Step Functions -> SNS
edge(bus, sfn, "regla ZoneThresholdRule (LabRole)", E_EVT + B + EL,
     pts=[(1124, 975), (1272, 975), (1272, 248)], lx=-0.2)
edge(s3n, sns, "", E_EVT + R + ET, pts=[(1516, 432), (1516, 880), (1422, 880)])

# S3 -> analizarImagen
edge(s3, analizar, "ObjectCreated", E_EVT + B + EL, pts=[(1059, 278), (1030, 278), (1030, 300)])

# Streams -> exportadores
edge(None, None, "DynamoDB Streams (cada cambio de t_incidencias)", E_EVT,
     sp=(150, 810), tp=(1655, 810), pts=[(150, 832), (1655, 832)], lx=0.6)

# ---------------------------------------------------------------- pie: observabilidad, IAM, leyenda
vertex("", 20, 1095, 44, 44, I_CW)
vertex("<b>CloudWatch</b> · logs de cada Lambda<br>(sam logs -n &lt;función&gt; --tail)", 70, 1092, 200, 50, TXT)
vertex("<b>IAM:</b> todas las Lambdas, la Step Function y la regla de EventBridge usan el rol <b>LabRole</b> "
       "de AWS Academy (Learner Lab no permite crear roles)", 300, 1090, 330, 55,
       "rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#666666;fontSize=9;arcSize=10;")
vertex("<b>Leyenda</b><br>"
       "<font color=\"#FF8000\">■</font> Lambda expuesta por API Gateway · "
       "<font color=\"#E7157B\">■</font> Lambda disparada por SQS, S3, EventBridge o Streams · "
       "<font color=\"#3D7EDB\">■</font> Lambda interna (sin ruta) · "
       "<font color=\"#9C27B0\">■</font> estado de Step Functions<br>"
       "── negro: HTTPS del navegador · ── azul: lectura/escritura DynamoDB · ┄ azul: invocación directa "
       "(Lambda o modelo de IA) · ── rosado: mensaje o evento (SQS, EventBridge, SNS, Streams)<br>"
       "── verde: subida directa a S3 · ── azul claro: exportación a GCP / Azure<br>"
       "<b>3 nubes:</b> AWS (núcleo + IA) · Google Cloud (analítica) · Azure (respaldo)",
       650, 1080, 800, 80,
       "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;fontSize=9;arcSize=6;"
       "align=left;spacingLeft=8;")
vertex("<b>100% serverless · pago por uso</b><br>Lambda · DynamoDB on-demand · SQS · Step Functions · S3 · "
       "BigQuery · Blob<br>sin servidores encendidos (no EC2)", 1470, 1080, 340, 80,
       "rounded=1;whiteSpace=wrap;html=1;fillColor=#F1F8E9;strokeColor=#2D7600;fontSize=9;arcSize=6;"
       "align=left;spacingLeft=8;")

# ---------------------------------------------------------------- salida
xml = ('<mxfile host="app.diagrams.net"><diagram id="telecorp" name="Arquitectura TeleCorp">'
       '<mxGraphModel dx="2200" dy="1200" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
       'fold="1" page="1" pageScale="1" pageWidth="2150" pageHeight="1200" math="0" shadow="0"><root>'
       '<mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) +
       "</root></mxGraphModel></diagram></mxfile>")

out = Path(__file__).with_name("arquitectura.drawio")
out.write_text(xml, encoding="utf-8")
print(f"OK -> {out} ({len(cells)} elementos)")
