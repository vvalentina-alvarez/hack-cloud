import json
import os
import random

import boto3

from shared.common import now_iso

sqs = boto3.client("sqs")

CENTER = (-12.06, -77.04)
_rng = random.Random(42)
ANTENNAS = [
    {
        "antennaId": f"ANT-{i:03d}",
        "lat": round(CENTER[0] + _rng.uniform(-0.08, 0.08), 6),
        "lon": round(CENTER[1] + _rng.uniform(-0.08, 0.08), 6),
    }
    for i in range(1, 21)
]


def sample_traffic():
    r = random.random()
    if r < 0.005:
        return 0.0                                   #inhabilitada
    if r < 0.025:
        return round(random.uniform(1, 59.9), 2)     #caída
    if r < 0.045:
        return round(random.uniform(129.1, 200), 2)  #saturada
    return round(random.uniform(60, 129), 2)         #normal


def handler(event, context):
    # Para la demo: {"force": {"ANT-003": 0, "ANT-004": 20}}
    forced = event.get("force", {}) if isinstance(event, dict) else {}
    ts = now_iso()
    entries = [
        {"Id": a["antennaId"],
         "MessageBody": json.dumps({**a, "gbPerMin": forced.get(a["antennaId"], sample_traffic()), "at": ts})}
        for a in ANTENNAS
    ]
    for i in range(0, len(entries), 10):  #SQS acepta 10 por batch
        sqs.send_message_batch(QueueUrl=os.environ["ANTENNA_QUEUE_URL"], Entries=entries[i:i + 10])
    return {"sent": len(entries)}
