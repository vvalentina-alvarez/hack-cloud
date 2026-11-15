import json
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from functools import lru_cache

import boto3

dynamodb = boto3.resource("dynamodb")
_events = boto3.client("events")
_secrets = boto3.client("secretsmanager")

incidents_table = dynamodb.Table(os.environ["INCIDENTS_TABLE"])
antennas_table = dynamodb.Table(os.environ["ANTENNAS_TABLE"])
zone_table = dynamodb.Table(os.environ["ZONE_TABLE"])

GEOHASH_PRECISION = 6  #1.2 km x 0.6 km por zona

TRANSITIONS = {
    "REGISTRADA": {"EN_REVISION"},
    "EN_REVISION": {"ATENDIDA", "CERRADA"},
    "ATENDIDA": {"SOLUCIONADA"},
    "SOLUCIONADA": {"CERRADA", "ATENDIDA"},
    "CERRADA": set(),
}


@lru_cache(maxsize=1)
def get_config():
    raw = _secrets.get_secret_value(SecretId=os.environ["CONFIG_SECRET_ARN"])["SecretString"]
    return json.loads(raw)


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def to_dec(x):
    return Decimal(str(x))


def _json_default(o):
    if isinstance(o, Decimal):
        return int(o) if o == o.to_integral_value() else float(o)
    if isinstance(o, set):
        return sorted(o)
    raise TypeError(f"No serializable: {type(o)}")


def dumps(obj):
    return json.dumps(obj, default=_json_default)


def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": dumps(body),
    }


def put_event(source, detail_type, detail):
    resp = _events.put_events(Entries=[{
        "Source": source,
        "DetailType": detail_type,
        "Detail": dumps(detail),
        "EventBusName": os.environ["EVENT_BUS"],
    }])
    if resp.get("FailedEntryCount"):
        raise RuntimeError(f"EventBridge rechazó el evento: {resp['Entries']}")


def classify(gb_per_min):
    gb = float(gb_per_min)
    if gb == 0:
        return "INHABILITADA"
    if gb < 60:
        return "CAIDA"
    if gb > 129:
        return "SATURADA"
    return "NORMAL"


_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def geohash(lat, lon, precision=GEOHASH_PRECISION):
    #indice espacial: misma zona -> mismo geohash
    lat_r, lon_r = [-90.0, 90.0], [-180.0, 180.0]
    bits, bit, ch, even, out = [16, 8, 4, 2, 1], 0, 0, True, []
    lat, lon = float(lat), float(lon)
    while len(out) < precision:
        rng, val = (lon_r, lon) if even else (lat_r, lat)
        mid = (rng[0] + rng[1]) / 2
        if val > mid:
            ch |= bits[bit]
            rng[0] = mid
        else:
            rng[1] = mid
        even = not even
        if bit < 4:
            bit += 1
        else:
            out.append(_BASE32[ch])
            bit, ch = 0, 0
    return "".join(out)
